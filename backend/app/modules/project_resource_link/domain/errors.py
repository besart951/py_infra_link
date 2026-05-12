from __future__ import annotations

from app.shared.errors import DomainError


class ProjectResourceLinkError(DomainError):
    """Base class for Project Resource Link domain errors."""


class ProjectResourceLinkNotFoundError(ProjectResourceLinkError):
    """Raised when a Project Resource Link is not found."""


class ResourceAlreadyLinkedError(ProjectResourceLinkError):
    """Raised when a resource is already linked to a project."""


class ProjectDoesNotExistError(ProjectResourceLinkError):
    """Raised when the target Project does not exist."""


class BuildingDoesNotExistError(ProjectResourceLinkError):
    """Raised when the target Building does not exist during import."""
