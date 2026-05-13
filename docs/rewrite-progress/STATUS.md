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

- **JWT auth middleware** — `auth` module with `UserCredential` model, `CredentialRepository`/`PasswordHasher` ports, `AuthModule` (register + login), `BcryptPasswordHasher`/`PlainPasswordHasher` adapters, `InMemoryCredentialAdapter`, `SqlAlchemyCredentialAdapter`, `JwtSettings`, `get_current_user` FastAPI dependency, `/auth/register` and `/auth/login` routes, Alembic migration `h93ac4edbe92`, ownership guard on project and notification routes. 145 tests pass (9 new auth tests).

- **PostgreSQL integration tests** — `testcontainers[postgres]` dev dependency; `app/integration_tests/` with conftest (session-scoped PG container + Alembic migrations, per-test transaction rollback via `NullPool`); 29 tests across User, Auth/Credential, Facility, Project, Notification adapters. Also fixed two production bugs uncovered by integration testing: (1) `SqlAlchemyUserAdapter.create` used `atomic()` → `session.begin()` which raises `InvalidRequestError` after autobegin — fixed to `session.begin_nested()` (SAVEPOINT); (2) all non-User ORM models used `Mapped[datetime]` without `DateTime(timezone=True)` causing asyncpg failures on timezone-aware datetimes — fixed to `DateTime(timezone=True)` across 10 ORM models.

## In Progress

_(none)_

## Not Started

- Auth layer (JWT middleware) ✅ done
- Integration tests with PostgreSQL test container ✅ done

## Architectural Decisions

- [ADR-0001](../adr/0001-backend-technology-stack.md) — FastAPI + SQLAlchemy 2.x + Alembic + Pydantic v2 + PostgreSQL
- [ADR-0002](../adr/0002-clean-architecture-seam-discipline.md) — Ports only at real seams (two Adapters minimum)

## Known Risks

- No CI pipeline yet — needs a GitHub Actions workflow
- Authentication/authorization behavior is still not implemented (identity CRUD exists)

## Next Run Recommendation

- All domains complete. PostgreSQL integration tests pass (29 tests). 145 unit tests pass.
- Next: CI/CD pipeline to run both test suites automatically, or add missing auth integration tests (role-based access, JWT expiry, refresh token).
