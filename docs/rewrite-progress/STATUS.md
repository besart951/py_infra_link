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
- **Project domain** — deep Module, ProjectName value object, per-owner name uniqueness, cross-module validation (User), SQLAlchemy adapter + migration, 10 tests
- **Project Resource Link domain** — deep Module, ResourceType StrEnum, link/unlink/import-building use cases, HierarchyReader port, SQLAlchemy adapter + hierarchy reader, in-memory adapters, FastAPI routes, Alembic migration, 14 tests
- **Live Update domain** — WebSocket broadcaster, ConnectionManager, CompositeEventPublisher (fans out to WS + Notifications), InMemoryEventPublisher, NullPublisher, tests
- **Notification domain** — deep Module, Notification model, NotificationRepository protocol, event-driven creation via NotificationEventPublisher, SQLAlchemy adapter + in-memory adapter, FastAPI routes, Alembic migration, tests

- **Cross-domain consistency** — all error mappers standardised to 409/422/404, `DomainError` parameter type throughout, user module pagination unified to `Page[T]`, `UserResponse` schema corrected (`from_attributes`, `UUID` id), `_make_module()` factory applied to all 11 route files, notification schemas UUID import normalised, CI pipeline added

## In Progress

_(none — all domains and consistency pass complete)_

## Not Started

- Fix pyright dict[Unknown] errors in in-memory adapters
- Auth layer (JWT middleware)
- Integration tests with PostgreSQL test container

## Architectural Decisions

- [ADR-0001](../adr/0001-backend-technology-stack.md) — FastAPI + SQLAlchemy 2.x + Alembic + Pydantic v2 + PostgreSQL
- [ADR-0002](../adr/0002-clean-architecture-seam-discipline.md) — Ports only at real seams (two Adapters minimum)

## Known Risks

- No CI pipeline yet — needs a GitHub Actions workflow
- Alembic migrations validated in offline SQL mode only; not yet applied to a live PostgreSQL instance
- Authentication/authorization behavior is still not implemented (identity CRUD exists)

## Next Run Recommendation

Fix pyright dict[Unknown] errors in in-memory adapters: add explicit type annotations
`dict[SomeId, SomeDomain]` on `_store` fields of all in-memory adapters.
Then consider adding JWT auth middleware or PostgreSQL integration tests.
