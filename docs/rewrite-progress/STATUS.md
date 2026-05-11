# py_infra_link Rewrite Status

## Completed Domains

_(none yet)_

## In Progress

- **Shared kernel** — project skeleton, shared error model, result type, pagination, IDs, clock

## Not Started

- Database session and transaction handling
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

- No existing tests or CI pipeline — must be established in the shared-kernel run
- No existing database — Alembic baseline migration needed after first model is written

## Next Run Recommendation

Implement the **shared kernel** + **database layer** (Candidates 1 and 2 below). These are in-process or local-substitutable dependencies — always deepenable, zero external blockers.
