from __future__ import annotations

from dataclasses import dataclass

from app.modules.live_update.domain.events import DomainEvent
from app.modules.live_update.infrastructure.broadcaster import WebSocketEventPublisher
from app.modules.notification.infrastructure.event_publisher import (
    NotificationEventPublisher,
)


@dataclass(frozen=True, slots=True)
class CompositeEventPublisher:
    """Fans out a single ``publish`` call to both the WebSocket broadcaster
    and the notification persister.

    Satisfies the ``EventPublisher`` Protocol while hiding the fan-out
    complexity from every caller.
    """

    _ws: WebSocketEventPublisher
    _notification: NotificationEventPublisher

    async def publish(self, event: DomainEvent) -> None:
        await self._ws.publish(event)
        await self._notification.publish(event)
