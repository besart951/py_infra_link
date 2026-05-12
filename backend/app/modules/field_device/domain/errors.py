from __future__ import annotations

from app.shared.errors import DomainError


class FieldDeviceError(DomainError):
    """Base class for field device domain errors."""


class FieldDeviceNotFoundError(FieldDeviceError):
    """Raised when a field device is not found."""


class FieldDeviceNameConflictError(FieldDeviceError):
    """Raised when a field device name already exists under the same SPS controller."""


class InvalidFieldDeviceNameError(FieldDeviceError):
    """Raised when a field device name is invalid."""


class SpsControllerDoesNotExistError(FieldDeviceError):
    """Raised when the parent SPS controller does not exist."""
