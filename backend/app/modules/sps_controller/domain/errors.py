from __future__ import annotations

from app.shared.errors import DomainError


class SpsControllerError(DomainError):
    """Base class for SPS controller domain errors."""


class SpsControllerNotFoundError(SpsControllerError):
    """Raised when an SPS controller is not found."""


class SpsControllerNameConflictError(SpsControllerError):
    """Raised when an SPS controller name already exists in the same control cabinet."""


class InvalidSpsControllerNameError(SpsControllerError):
    """Raised when an SPS controller name is invalid."""


class ControlCabinetDoesNotExistError(SpsControllerError):
    """Raised when the parent control cabinet does not exist."""


class SpsControllerSystemTypeDoesNotExistError(SpsControllerError):
    """Raised when the associated system type does not exist."""
