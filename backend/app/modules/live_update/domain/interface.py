from __future__ import annotations

from typing import Protocol

from app.modules.live_update.domain.events import DomainEvent


class EventPublisher(Protocol):
    """Port for emitting domain events to interested consumers."""

    async def publish(self, event: DomainEvent) -> None: ...
