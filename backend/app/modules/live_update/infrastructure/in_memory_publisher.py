from __future__ import annotations

from dataclasses import dataclass, field

from app.modules.live_update.domain.events import DomainEvent, DomainEventType


def _event_store() -> list[DomainEvent]:
    return []


@dataclass(frozen=True, slots=True)
class InMemoryEventPublisher:
    """EventPublisher that collects emitted events for test assertions."""

    _events: list[DomainEvent] = field(default_factory=_event_store)

    async def publish(self, event: DomainEvent) -> None:
        self._events.append(event)

    def events_of_type(self, event_type: DomainEventType) -> list[DomainEvent]:
        return [e for e in self._events if e.event_type == event_type]

    def all_events(self) -> list[DomainEvent]:
        return list(self._events)

    def clear(self) -> None:
        self._events.clear()
