# py_infra_link Rewrite Status

## Completed Domains

- **Shared kernel** — `errors`, `result`, `ids`, `clock`, `pagination` — 27 interface-level tests, ruff clean
- **Database layer** — `engine`, `session`, `transaction`, Alembic baseline migration
- **User / auth / domain identity** — deep User Module, SQLAlchemy model + adapter, FastAPI routes, Alembic migration, tests
- **Facility domain** — deep Facility Module, domain validation, SQLAlchemy adapter + migration, tests
- **Building domain** — deep Building Module, hierarchical routes, composite uniqueness, cross-module validation, tests
- **Control Cabinet domain** — deep Control Cabinet Module, hierarchical routes, composite uniqueness, cross-module validation, tests
- **SPS Controller System Type domain** — deep Module, classification classification, SQLAlchemy adapter + migration, tests
- **SPS Controller domain** — deep Module, hierarchical routes, cross-module validation (Cabinet, System Type), SQLAlchemy adapter + migration, tests
- **Field Device domain** — deep Module, hierarchical routes, cross-module validation (SPS Controller), SQLAlchemy adapter + migration, 9 tests
- **BACnet Object domain** — deep Module, BacnetObjectType StrEnum, dual uniqueness constraints (type+instance, name), cross-module validation (Field Device), SQLAlchemy adapter + migration, 11 tests

## In Progress

_(none — ready to start Project domain)_

## Not Started

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

Implement the **Project domain** (priority 11). The full physical/logical object tree is now complete.
