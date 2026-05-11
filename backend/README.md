# py_infra_link backend

FastAPI + SQLAlchemy 2.x + Alembic + Pydantic v2 + PostgreSQL.

## Development

```bash
# Install dependencies (requires uv)
uv sync

# Run linter / formatter
uv run ruff check app/
uv run ruff format app/

# Run type checker
uv run pyright

# Run tests
uv run pytest

# Start dev server
uv run uvicorn app.main:app --reload

# Alembic migrations
uv run alembic upgrade head
uv run alembic revision --autogenerate --message "describe change"
```

## Structure

```
app/
  main.py             FastAPI application entry-point
  config/
    settings.py       Pydantic-settings configuration
  shared/
    errors.py         Domain error hierarchy
    result.py         Ok / Err / Result types
    ids.py            NewType UUID identity aliases
    clock.py          Clock protocol + SystemClock + FixedClock
    pagination.py     PageParams + Page[T]
  database/
    engine.py         Shared AsyncEngine
    session.py        Session factory + FastAPI dependency
    transaction.py    atomic() context manager
    migrations/       Alembic migrations
  modules/
    <domain>/         One folder per domain (facility, building, ...)
```
