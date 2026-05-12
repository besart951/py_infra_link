from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from app.shared.ids import ProjectId, ProjectResourceLinkId


class ResourceType(StrEnum):
    FACILITY = "facility"
    BUILDING = "building"
    CONTROL_CABINET = "control_cabinet"
    SPS_CONTROLLER = "sps_controller"
    FIELD_DEVICE = "field_device"
    BACNET_OBJECT = "bacnet_object"


@dataclass(frozen=True, slots=True)
class ProjectResourceLink:
    id: ProjectResourceLinkId
    project_id: ProjectId
    resource_type: ResourceType
    resource_id: uuid.UUID
    linked_at: datetime


@dataclass(frozen=True, slots=True)
class ImportBuildingResult:
    """Summary returned after a transitive building import."""

    linked: int
    skipped: int
