# English Learning Backend

FastAPI-based backend for the AI-powered English education platform.

## Features

- JWT-based authentication (email/password)
- PostgreSQL database with SQLAlchemy async ORM
- Alembic migrations
- GPU auto-detection for LLM inference (NVIDIA & AMD)
- Async I/O operations throughout

## Setup

### Prerequisites

- Python 3.13+
- PostgreSQL 16
- Docker & Docker Compose (optional)

### Development Setup

1. Create virtual environment and install dependencies:
```bash
cd backend
uv sync
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run migrations:
```bash
uv run alembic upgrade head
```

4. Start the development server:
```bash
uv run uvicorn app.main:app --reload
```

### Docker Setup

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Run migrations
docker-compose exec backend uv run alembic upgrade head
```

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Migrations

```bash
# Create new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Downgrade
uv run alembic downgrade -1
```

## Testing

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=app
```
