from __future__ import annotations

from dataclasses import dataclass

from app.modules.live_update.domain.events import DomainEvent


@dataclass(frozen=True, slots=True)
class NullEventPublisher:
    """EventPublisher that discards all events.

    Use in contexts where event publishing is not required (e.g. read-only
    operations or modules not yet wired to the live-update system).
    """

    async def publish(self, event: DomainEvent) -> None:
        pass
