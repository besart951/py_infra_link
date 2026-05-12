from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class DomainEventType(StrEnum):
    PROJECT_CREATED = "project.created"
    PROJECT_UPDATED = "project.updated"
    PROJECT_DELETED = "project.deleted"
    PROJECT_RESOURCE_LINKED = "project_resource_link.linked"
    PROJECT_RESOURCE_UNLINKED = "project_resource_link.unlinked"
    PROJECT_BUILDING_IMPORTED = "project_resource_link.building_imported"


@dataclass(frozen=True, slots=True)
class DomainEvent:
    """An immutable record of something that happened within a domain.

    ``payload`` carries stringified fields to keep serialisation uniform.
    """

    event_type: DomainEventType
    aggregate_id: uuid.UUID
    payload: dict[str, str]
    occurred_at: datetime
