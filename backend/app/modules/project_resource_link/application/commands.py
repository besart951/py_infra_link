from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.modules.project_resource_link.domain.models import ResourceType
from app.shared.ids import BuildingId, ProjectId, ProjectResourceLinkId, UserId


@dataclass(frozen=True, slots=True)
class LinkResourceCommand:
    owner_id: UserId
    project_id: ProjectId
    resource_type: ResourceType
    resource_id: uuid.UUID


@dataclass(frozen=True, slots=True)
class ImportBuildingCommand:
    owner_id: UserId
    project_id: ProjectId
    building_id: BuildingId


@dataclass(frozen=True, slots=True)
class UnlinkResourceCommand:
    owner_id: UserId
    project_id: ProjectId
    link_id: ProjectResourceLinkId
