from __future__ import annotations

from app.shared.errors import DomainError


class ControlCabinetError(DomainError):
    """Base class for control cabinet domain errors."""


class ControlCabinetNotFoundError(ControlCabinetError):
    """Raised when a control cabinet is not found."""


class ControlCabinetNameConflictError(ControlCabinetError):
    """Raised when a control cabinet name already exists in the same building."""


class InvalidControlCabinetNameError(ControlCabinetError):
    """Raised when a control cabinet name is invalid."""


class BuildingDoesNotExistError(ControlCabinetError):
    """Raised when the parent building does not exist."""
