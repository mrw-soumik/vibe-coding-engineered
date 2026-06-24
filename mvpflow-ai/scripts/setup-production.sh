#!/bin/bash
# Production deployment helper script

set -e

echo "🚀 MVPFlow AI Production Deployment Setup"
echo "=========================================="

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Edit .env with your production configuration"
fi

# Install dependencies
echo "📦 Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Initialize database
echo "🗄️  Initializing database..."
python -c "from app.database import init_db; from app.config import config; init_db(config.DATABASE_URL)"

# Run migrations (if using Alembic)
if [ -d "alembic" ]; then
    echo "🔄 Running database migrations..."
    alembic upgrade head
fi

# Create logs directory
mkdir -p logs

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -v

echo ""
echo "✅ Production setup complete!"
echo ""
echo "To start the server:"
echo "  Development:  uvicorn app.main:app --reload"
echo "  Production:   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app"
echo ""
echo "With Docker:"
echo "  docker-compose up -d"
echo ""
echo "API Documentation:"
echo "  Swagger: http://localhost:8000/docs"
echo "  ReDoc: http://localhost:8000/redoc"
