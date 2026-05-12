from __future__ import annotations

from app.shared.errors import DomainError


class NotificationNotFoundError(DomainError):
    """Raised when a Notification does not exist or belongs to a different user."""
