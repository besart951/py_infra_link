# py_infra_link

Infrastructure linking platform that models physical building infrastructure — facilities, buildings, control cabinets, SPS controllers, field devices, and BACnet objects — and associates them with projects.

## Language

### Infrastructure hierarchy

**Facility**:
A top-level physical site or location that contains one or more Buildings.
_Avoid_: Site, location, property

**Building**:
A physical structure inside a Facility that contains Control Cabinets.
_Avoid_: Structure, premise

**Control Cabinet**:
A physical enclosure inside a Building that houses one or more SPS Controllers.
_Avoid_: Enclosure, panel, cabinet

**SPS Controller**:
A programmable controller inside a Control Cabinet that manages Field Devices. Has an associated SPS Controller System Type.
_Avoid_: PLC, device controller, unit

**SPS Controller System Type**:
The make/model classification of an SPS Controller that determines its capabilities and protocol support.
_Avoid_: Controller type, model, variant

**Field Device**:
A physical sensor or actuator managed by an SPS Controller. Exposes one or more BACnet Objects.
_Avoid_: Sensor, actuator, endpoint

**BACnet Object**:
A logical data point exposed by a Field Device using the BACnet protocol.
_Avoid_: Data point, tag, property

### Project domain

**Project**:
A logical grouping that links together infrastructure resources (Buildings, Control Cabinets, SPS Controllers, etc.) for a specific purpose or deployment scope.
_Avoid_: Job, engagement, workspace

**Project Resource Link**:
An explicit association between a Project and a piece of infrastructure. Created when infrastructure is imported into or copied into a Project.
_Avoid_: Project assignment, project binding

### Identity and access

**User**:
A person with authenticated access to the system. Owns or participates in Projects.
_Avoid_: Account, member, operator

## Relationships

- A **Facility** contains one or more **Buildings**
- A **Building** contains zero or more **Control Cabinets**
- A **Control Cabinet** contains zero or more **SPS Controllers**
- An **SPS Controller** has exactly one **SPS Controller System Type**
- An **SPS Controller** manages zero or more **Field Devices**
- A **Field Device** exposes zero or more **BACnet Objects**
- A **Project** has zero or more **Project Resource Links**
- A **Project Resource Link** references one piece of infrastructure at any level of the hierarchy

## Coding Standards

To maintain consistency and leverage modern Python features, all domains must follow these rules:

### Modules and Adapters
- Use `@dataclass(frozen=True, slots=True)` for **Module** and **Adapter** classes.
- Eliminate manual `__init__` methods.
- In **Module** classes (application layer), fields must be **public** (e.g., `repository: UserRepository`) to allow easy dependency injection in routes.
- In **Adapter** classes (infrastructure layer), fields should be **private** (e.g., `_session: AsyncSession`) to encapsulate implementation details.
- Use `field(default_factory=dict)` for mutable state in in-memory adapters.

### Imports and Type Safety
- Always use `from __future__ import annotations`.
- Use explicit return types on every function.
- Prefer `list[str]`, `dict[str, str]` etc. over `typing.List`.
- Use `Protocol` for repository interfaces.

## Example dialogue

> **Dev:** "When a user imports a Building into a Project, do we copy the whole Control Cabinet hierarchy?"
> **Domain expert:** "Yes — importing a Building creates Project Resource Links for the Building, all its Control Cabinets, all their SPS Controllers, and their Field Devices transitively."

> **Dev:** "Can a Field Device belong to two SPS Controllers?"
> **Domain expert:** "No — a Field Device is owned by exactly one SPS Controller."

## Flagged ambiguities

- "device" was used informally to mean both **SPS Controller** and **Field Device** — resolved: always use the full names.
- "system type" was used for both the classification concept and a configuration property — resolved: **SPS Controller System Type** is the classification; "system configuration" covers runtime properties.
