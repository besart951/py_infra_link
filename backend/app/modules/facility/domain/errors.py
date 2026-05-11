from __future__ import annotations

from app.shared.errors import DomainError


class FacilityError(DomainError):
    """Base class for facility domain errors."""


class FacilityNotFoundError(FacilityError):
    """Raised when a facility is not found."""


class FacilityNameConflictError(FacilityError):
    """Raised when a facility name already exists."""


class InvalidFacilityNameError(FacilityError):
    """Raised when a facility name is invalid."""
