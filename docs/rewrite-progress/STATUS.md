# py_infra_link Rewrite Status

## Completed Domains

- **Shared kernel** — `errors`, `result`, `ids`, `clock`, `pagination` — 27 interface-level tests, ruff clean
- **Database layer** — `engine`, `session`, `transaction`, Alembic baseline migration
- **User / auth / domain identity** — deep User Module (domain/application/infrastructure/presentation), SQLAlchemy model + adapter, FastAPI routes, Alembic users-table migration, interface tests

## In Progress

_(none — ready to start Facility domain)_

## Not Started

- Facility domain
- Building domain
- Control Cabinet domain
- SPS Controller domain
- SPS Controller System Type domain
- Field Device domain
- BACnet Object domain
- Project domain
- Project Resource Link / importing / copying
- Live update / websocket event publishing
- Notifications
- Cross-domain consistency and cleanup

## Architectural Decisions

- [ADR-0001](../adr/0001-backend-technology-stack.md) — FastAPI + SQLAlchemy 2.x + Alembic + Pydantic v2 + PostgreSQL
- [ADR-0002](../adr/0002-clean-architecture-seam-discipline.md) — Ports only at real seams (two Adapters minimum)

## Known Risks

- No CI pipeline yet — needs a GitHub Actions workflow
- Alembic migrations validated in offline SQL mode only; not yet applied to a live PostgreSQL instance
- Authentication/authorization behavior is still not implemented (identity CRUD exists)

## Next Run Recommendation

Implement the **Facility domain** (priority 4). Reuse the User Module patterns: thin routes, domain Interface as test surface, SQLAlchemy adapter, and explicit transaction boundaries.
