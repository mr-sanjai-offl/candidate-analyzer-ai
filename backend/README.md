# ApexGuidance AI — Backend

> AI-powered platform for evaluating software engineer capabilities using public coding platforms and project repositories.

## Prerequisites

- **Python 3.12+**
- **Docker** and **Docker Compose**
- **PostgreSQL 16** (or use Docker Compose)
- **Redis 7** (or use Docker Compose)

## Quick Start (Docker)

The fastest way to get the entire stack running:

```bash
# 1. Clone the repository
git clone <repository-url>
cd candidate-analyzer-ai

# 2. Create environment file
cp backend/.env.example backend/.env

# 3. Start all services
docker compose up --build
```

The API will be available at **http://localhost:8000**.

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/api/v1/health

## Local Development Setup

```bash
# 1. Navigate to the backend directory
cd backend

# 2. Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create environment file
cp .env.example .env
# Edit .env with your configuration

# 5. Start PostgreSQL and Redis (via Docker Compose)
docker compose up postgres redis -d

# 6. Run database migrations
alembic upgrade head

# 7. Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Running Tests

```bash
cd backend

# Run all tests
pytest

# Run with verbose output
pytest -v --tb=short

# Run a specific test file
pytest tests/test_health.py -v
```

## Code Quality

### Linting and Formatting

```bash
cd backend

# Ruff — Lint
ruff check app/ tests/

# Ruff — Lint with auto-fix
ruff check app/ tests/ --fix

# Black — Format
black app/ tests/

# Black — Check only
black --check app/ tests/

# mypy — Type check
mypy app/ --config-file pyproject.toml
```

### Pre-commit Hooks

```bash
# Install hooks (run once from project root)
pre-commit install

# Run all hooks manually
pre-commit run --all-files
```

## Database Migrations

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "description of changes"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current migration
alembic current
```

## Project Structure

```
backend/
├── app/
│   ├── api/v1/             # API route handlers (no business logic here)
│   ├── core/               # Config, logging, exceptions
│   ├── database/           # SQLAlchemy engine, session, models
│   ├── schemas/            # Pydantic request/response models
│   ├── services/           # Business logic layer
│   ├── collectors/         # External platform data collectors
│   │   ├── github/
│   │   ├── leetcode/
│   │   └── codeforces/
│   ├── agents/             # LangGraph AI agents
│   ├── scoring/            # Capability scoring engine
│   ├── tasks/              # Celery background tasks
│   └── utils/              # Shared utilities
├── tests/                  # Test suite
├── alembic/                # Database migrations
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Tool configuration (Ruff, Black, mypy, pytest)
├── Dockerfile              # Multi-stage production build
└── .env.example            # Environment variable template
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application display name | `ApexGuidance AI` |
| `APP_VERSION` | Semantic version | `1.0.0` |
| `ENVIRONMENT` | `development` / `staging` / `production` | `development` |
| `DEBUG` | Enable debug mode (auto-disabled in production) | `false` |
| `DATABASE_URL` | Async PostgreSQL connection string | `postgresql+asyncpg://...` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `CORS_ORIGINS` | Allowed CORS origins (JSON list) | `["http://localhost:3000"]` |
| `LOG_LEVEL` | Python logging level | `INFO` |
| `SENTRY_DSN` | Sentry error tracking DSN | _(empty)_ |

## Architecture

This project follows the architecture defined in [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md). Key principles:

- **No business logic in route handlers** — all logic lives in `services/`, `collectors/`, `agents/`, or `scoring/`.
- **Pydantic Settings only** — all configuration from environment variables.
- **Async everywhere** — all I/O operations use async/await.
- **Type hints required** — enforced by mypy in strict mode.
- **Structured JSON logging** — no `print()` statements.
- **Dependency injection** — FastAPI `Depends()` for all dependencies.
