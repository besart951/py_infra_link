from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.modules.project_resource_link.domain.models import ResourceType


class ProjectResourceLinkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    resource_type: ResourceType
    resource_id: uuid.UUID
    linked_at: datetime


class LinkResourceRequest(BaseModel):
    resource_type: ResourceType
    resource_id: uuid.UUID


class ImportBuildingResponse(BaseModel):
    linked: int
    skipped: int
