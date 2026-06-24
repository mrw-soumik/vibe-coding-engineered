import logging
import uuid
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException, status, Depends, Request
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.orm import Session
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import config
from app.models import FounderNotesRequest, WorkflowResponse
from app.core.workflow import run_workflow
from app.database import init_db, get_db_session, WorkflowExecution, AuditLog
from app.security import security_manager
from app.middleware import (
    setup_cors,
    setup_custom_middleware,
    setup_rate_limiter,
    setup_logging,
    get_client_ip,
)

# Configure logging first
setup_logging()
logger = logging.getLogger(__name__)

# Setup rate limiter
limiter = setup_rate_limiter()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events.
    
    Handles:
    - Database initialization on startup
    - Graceful shutdown
    """
    logger.info(f"Starting MVPFlow AI v{config.APP_VERSION}")
    logger.info(f"Environment: {config.APP_ENV}")
    logger.info(f"Database: {config.DATABASE_URL}")

    # Optional error tracking (no-op unless SENTRY_DSN is set)
    from app.observability import init_observability
    init_observability()
    
    # Initialize database
    try:
        init_db(config.DATABASE_URL)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}", exc_info=True)
        raise
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down MVPFlow AI")


# Create FastAPI app with lifespan
app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="Founder notes to MVP execution workflow - Production Edition",
    docs_url="/docs" if config.ENABLE_SWAGGER_UI else None,
    redoc_url="/redoc" if config.ENABLE_SWAGGER_UI else None,
    openapi_url="/openapi.json" if config.ENABLE_SWAGGER_UI else None,
    lifespan=lifespan,
)

# Register the rate limiter and its 429 exception handler so the per-route
# @limiter.limit(...) decorators actually enforce limits instead of 500-ing.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Setup middleware
setup_custom_middleware(app)
setup_cors(app)


async def audit_log(
    request: Request,
    action: str,
    resource_type: str,
    status_code: int,
    response_data: Optional[dict] = None,
    user_id: Optional[str] = None,
    db: Optional[Session] = None,
) -> None:
    """Create an audit log entry.
    
    Args:
        request: FastAPI request object.
        action: Action being performed (e.g., "workflow_execution").
        resource_type: Type of resource (e.g., "workflow").
        status_code: HTTP status code of the operation.
        response_data: Optional response data to log.
        user_id: Optional user ID for the operation.
        db: Optional database session.
    """
    if db is None:
        return
    
    try:
        log_entry = AuditLog(
            id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            status_code=status_code,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("user-agent", "")[:500],
            response_data=response_data,
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to create audit log: {str(e)}")


@app.get("/health")
async def health(db: Session = Depends(get_db_session)) -> dict:
    """Health check endpoint with database connectivity check.
    
    Returns:
        Status and service information.
    """
    try:
        # Test database connectivity
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "unhealthy"
    
    return {
        "status": "ok",
        "service": config.APP_NAME,
        "version": config.APP_VERSION,
        "environment": config.APP_ENV,
        "database": db_status,
    }


@app.post(f"{config.API_V1_STR}/workflow", response_model=WorkflowResponse)
@limiter.limit("10/minute")
async def workflow(
    request: Request,
    payload: FounderNotesRequest,
    user_id: Optional[str] = Depends(security_manager.get_optional_user),
    db: Session = Depends(get_db_session),
) -> WorkflowResponse:
    """Run the complete MVPFlow AI workflow.
    
    Accepts founder notes and optional domain, returns structured MVP package.
    
    Args:
        request: FastAPI request object.
        payload: FounderNotesRequest with notes and domain.
        user_id: Optional authenticated user ID.
        db: Database session for persistence.
        
    Returns:
        WorkflowResponse with requirements, MVP plan, architecture, tickets, 
        evaluation, and final summary.
        
    Raises:
        HTTPException 400: If input validation fails.
        HTTPException 500: If workflow execution fails.
    """
    execution_id = str(uuid.uuid4())
    start_time = __import__("time").time()
    
    try:
        logger.info(
            f"[{execution_id}] Workflow request received for domain: {payload.domain} "
            f"from user: {user_id or 'anonymous'}"
        )
        logger.debug(f"[{execution_id}] Input notes length: {len(payload.notes)} characters")
        
        # Execute workflow
        result = run_workflow(payload.notes, payload.domain)
        
        execution_time_ms = int((__import__("time").time() - start_time) * 1000)
        
        logger.info(
            f"[{execution_id}] Workflow completed. Score: {result.evaluation.overall_score}/5 "
            f"in {execution_time_ms}ms"
        )
        
        # Store execution record for audit trail
        try:
            execution_record = WorkflowExecution(
                id=execution_id,
                user_id=user_id,
                domain=payload.domain,
                input_notes=payload.notes[:1000],  # Store first 1000 chars
                requirements=result.requirements.model_dump(),
                mvp_plan=result.mvp_plan.model_dump(),
                architecture=result.architecture.model_dump(),
                jira_tickets=[t.model_dump() for t in result.jira_tickets],
                evaluation=result.evaluation.model_dump(),
                final_summary=result.final_summary,
                overall_score=result.evaluation.overall_score,
                execution_time_ms=execution_time_ms,
                status="success",
            )
            db.add(execution_record)
            db.commit()
            logger.debug(f"[{execution_id}] Execution record stored")
        except Exception as e:
            logger.error(f"[{execution_id}] Failed to store execution record: {str(e)}")
        
        # Create audit log
        await audit_log(
            request,
            action="workflow_execution",
            resource_type="workflow",
            status_code=200,
            response_data={"score": result.evaluation.overall_score},
            user_id=user_id,
            db=db,
        )
        
        return result
    
    except ValidationError as e:
        logger.warning(f"[{execution_id}] Validation error: {str(e)}")
        
        await audit_log(
            request,
            action="workflow_execution",
            resource_type="workflow",
            status_code=400,
            user_id=user_id,
            db=db,
        )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Input validation failed: {str(e)}",
        )
    
    except ValueError as e:
        logger.warning(f"[{execution_id}] Value error: {str(e)}")
        
        await audit_log(
            request,
            action="workflow_execution",
            resource_type="workflow",
            status_code=400,
            user_id=user_id,
            db=db,
        )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input: {str(e)}",
        )
    
    except Exception as e:
        logger.error(f"[{execution_id}] Workflow execution error: {str(e)}", exc_info=True)
        
        # Store failed execution
        try:
            execution_record = WorkflowExecution(
                id=execution_id,
                user_id=user_id,
                domain=payload.domain,
                input_notes=payload.notes[:1000],
                requirements={},
                mvp_plan={},
                architecture={},
                jira_tickets=[],
                evaluation={},
                final_summary="",
                overall_score=0.0,
                execution_time_ms=int((__import__("time").time() - start_time) * 1000),
                status="error",
                error_message=str(e)[:1000],
            )
            db.add(execution_record)
            db.commit()
        except Exception as db_error:
            logger.error(f"[{execution_id}] Failed to store error record: {str(db_error)}")
        
        await audit_log(
            request,
            action="workflow_execution",
            resource_type="workflow",
            status_code=500,
            user_id=user_id,
            db=db,
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {str(e)}",
        )


@app.get(f"{config.API_V1_STR}/executions")
@limiter.limit("5/minute")
async def list_executions(
    request: Request,
    limit: int = 10,
    offset: int = 0,
    user_id: Optional[str] = Depends(security_manager.get_optional_user),
    db: Session = Depends(get_db_session),
) -> dict:
    """List workflow execution history.
    
    Args:
        request: FastAPI request object.
        limit: Maximum number of records to return.
        offset: Number of records to skip.
        user_id: Optional authenticated user ID (filters to user's executions if provided).
        db: Database session.
        
    Returns:
        List of execution records and total count.
    """
    query = db.query(WorkflowExecution)
    
    if user_id:
        query = query.filter(WorkflowExecution.user_id == user_id)
    
    total = query.count()
    executions = query.order_by(WorkflowExecution.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "executions": [
            {
                "id": e.id,
                "domain": e.domain,
                "overall_score": e.overall_score,
                "execution_time_ms": e.execution_time_ms,
                "status": e.status,
                "created_at": e.created_at.isoformat(),
            }
            for e in executions
        ],
    }
