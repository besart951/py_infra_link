"""Shared domain error hierarchy.

All domain errors derive from ``DomainError``.  Presentation adapters map these
to HTTP responses via ``presentation/error_mapping.py`` in each module — domain
logic never imports HTTP concerns.
"""

from __future__ import annotations


class DomainError(Exception):
    """Base class for all domain-level errors."""

    message: str

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.message!r})"


class NotFoundError(DomainError):
    """Raised when a requested resource does not exist."""


class ConflictError(DomainError):
    """Raised when an operation conflicts with existing state (e.g. duplicate)."""


class AuthorizationError(DomainError):
    """Raised when the caller lacks permission to perform an operation."""


class ValidationError(DomainError):
    """Raised when input data violates domain invariants."""


class InvariantError(DomainError):
    """Raised when a domain invariant is violated during an operation."""
