# py_infra_link Rewrite Status

## Completed Domains

- **Shared kernel** — `errors`, `result`, `ids`, `clock`, `pagination` — 27 interface-level tests, ruff clean
- **Database layer** — `engine`, `session`, `transaction`, Alembic baseline migration

## In Progress

_(none — ready to start User/auth domain)_

## Not Started

- User / auth / domain identity
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
- `pyright` strict-mode not fully verified (no live DB for engine imports)
- Alembic baseline not yet applied to a live database

## Next Run Recommendation

Implement the **User / auth / domain identity** module.  This will be the first domain module and will establish the `modules/<domain>/` folder structure including SQLAlchemy ORM model, Alembic migration, Pydantic v2 schemas, and FastAPI routes.

