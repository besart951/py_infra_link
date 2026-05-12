from __future__ import annotations

from app.shared.errors import DomainError


class ProjectError(DomainError):
    """Base class for Project domain errors."""


class ProjectNotFoundError(ProjectError):
    """Raised when a Project is not found."""


class ProjectNameConflictError(ProjectError):
    """Raised when a Project name already exists for the same owner."""


class InvalidProjectNameError(ProjectError):
    """Raised when a Project name is invalid."""


class UserDoesNotExistError(ProjectError):
    """Raised when the owner User does not exist."""
