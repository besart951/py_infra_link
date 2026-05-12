from __future__ import annotations

from dataclasses import dataclass

from app.modules.live_update.domain.events import DomainEvent
from app.modules.live_update.infrastructure.connection_manager import ConnectionManager


@dataclass(frozen=True, slots=True)
class WebSocketEventPublisher:
    """Publishes domain events to all connected WebSocket clients."""

    _manager: ConnectionManager

    async def publish(self, event: DomainEvent) -> None:
        await self._manager.broadcast(
            {
                "event_type": str(event.event_type),
                "aggregate_id": str(event.aggregate_id),
                "payload": event.payload,
                "occurred_at": event.occurred_at.isoformat(),
            }
        )
