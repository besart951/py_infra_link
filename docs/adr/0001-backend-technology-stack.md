# Backend technology stack

We are building a modern Python backend using FastAPI, SQLAlchemy 2.x (async, typed ORM with `Mapped[...]` / `mapped_column(...)`), Alembic, Pydantic v2, and PostgreSQL. Python 3.12+ strict typing throughout. `uv` as package manager, `ruff` for formatting/linting, `pyright` for type-checking, `pytest` + `pytest-asyncio` for tests.

These choices carry meaningful lock-in (SQLAlchemy async session shape, Alembic migration history, Pydantic v2 serialisation contract) and replacing any of them would require a project-wide migration. Avoid suggesting alternatives unless a specific capability gap appears.
