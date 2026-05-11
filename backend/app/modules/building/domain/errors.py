from __future__ import annotations

from app.shared.errors import DomainError


class BuildingError(DomainError):
    """Base class for building domain errors."""


class BuildingNotFoundError(BuildingError):
    """Raised when a building is not found."""


class BuildingNameConflictError(BuildingError):
    """Raised when a building name already exists in the same facility."""


class InvalidBuildingNameError(BuildingError):
    """Raised when a building name is invalid."""


class FacilityDoesNotExistError(BuildingError):
    """Raised when the parent facility does not exist."""
