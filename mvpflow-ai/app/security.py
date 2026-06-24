"""Authentication and security for MVPFlow AI.

Provides JWT token generation/validation, password hashing, and auth dependencies.
"""
from __future__ import annotations
from datetime import datetime, timedelta, UTC
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from app.config import config

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT. Two schemes: one that 401s on a missing/blank token (for required auth),
# and one that returns None instead of erroring (for optional auth).
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)



class SecurityManager:
    """Manages authentication and security operations."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt.
        
        Args:
            password: Plain text password.
            
        Returns:
            Hashed password.
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash.
        
        Args:
            plain_password: Plain text password to verify.
            hashed_password: Hashed password to compare against.
            
        Returns:
            True if password matches, False otherwise.
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(
        subject: str,
        expires_delta: Optional[timedelta] = None,
        additional_claims: Optional[dict] = None,
    ) -> str:
        """Create a JWT access token.
        
        Args:
            subject: Subject for the token (usually user ID).
            expires_delta: Token expiration time (uses default if not provided).
            additional_claims: Additional claims to include in token.
            
        Returns:
            JWT token string.
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)

        expire = datetime.now(UTC) + expires_delta
        to_encode = {"sub": subject, "exp": expire}
        
        if additional_claims:
            to_encode.update(additional_claims)

        encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
        logger.debug(f"Created access token for subject: {subject}")
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode a JWT token.
        
        Args:
            token: JWT token string to verify.
            
        Returns:
            Token payload as dictionary.
            
        Raises:
            HTTPException: If token is invalid or expired.
        """
        try:
            payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
            subject: str = payload.get("sub")
            if subject is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing subject",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return payload
        except JWTError as e:
            logger.warning(f"Token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e

    @staticmethod
    def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
        """Dependency for getting current authenticated user.
        
        Args:
            credentials: HTTP Bearer credentials from request.
            
        Returns:
            User ID from token subject.
            
        Raises:
            HTTPException: If credentials are invalid.
        """
        token = credentials.credentials
        payload = SecurityManager.verify_token(token)
        return payload.get("sub")

    @staticmethod
    def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security)) -> Optional[str]:
        """Dependency for getting optional authenticated user.

        Uses an ``auto_error=False`` bearer scheme so an anonymous request
        (no Authorization header) resolves to ``None`` instead of raising 403.
        A token that is present but invalid still raises 401.

        Args:
            credentials: HTTP Bearer credentials from request (optional).

        Returns:
            User ID from token subject, or None if no credentials.

        Raises:
            HTTPException: If credentials are provided but invalid.
        """
        if credentials is None:
            return None
        return SecurityManager.get_current_user(credentials)


# Create singleton instance
security_manager = SecurityManager()
