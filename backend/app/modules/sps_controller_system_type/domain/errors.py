from __future__ import annotations

from app.shared.errors import DomainError


class SpsControllerSystemTypeError(DomainError):
    """Base class for SPS controller system type domain errors."""


class SpsControllerSystemTypeNotFoundError(SpsControllerSystemTypeError):
    """Raised when an SPS controller system type is not found."""


class SpsControllerSystemTypeNameConflictError(SpsControllerSystemTypeError):
    """Raised when an SPS controller system type name already exists."""


class InvalidSpsControllerSystemTypeNameError(SpsControllerSystemTypeError):
    """Raised when an SPS controller system type name is invalid."""
