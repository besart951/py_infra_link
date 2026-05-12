from __future__ import annotations

import dataclasses
import uuid
from datetime import UTC, datetime

import pytest

from app.modules.live_update.domain.events import DomainEvent, DomainEventType
from app.modules.live_update.infrastructure.in_memory_publisher import (
    InMemoryEventPublisher,
)
from app.modules.live_update.infrastructure.null_publisher import NullEventPublisher


def _make_event(
    event_type: DomainEventType = DomainEventType.PROJECT_CREATED,
) -> DomainEvent:
    return DomainEvent(
        event_type=event_type,
        aggregate_id=uuid.uuid4(),
        payload={"project_id": str(uuid.uuid4()), "name": "Test"},
        occurred_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


# ── DomainEvent ────────────────────────────────────────────────────────────────


def test_domain_event_is_immutable() -> None:
    event = _make_event()
    with pytest.raises(dataclasses.FrozenInstanceError):
        event.event_type = DomainEventType.PROJECT_DELETED  # type: ignore[misc]


def test_domain_event_type_values_are_stable() -> None:
    assert DomainEventType.PROJECT_CREATED == "project.created"
    assert DomainEventType.PROJECT_UPDATED == "project.updated"
    assert DomainEventType.PROJECT_DELETED == "project.deleted"
    assert DomainEventType.PROJECT_RESOURCE_LINKED == "project_resource_link.linked"
    assert DomainEventType.PROJECT_RESOURCE_UNLINKED == "project_resource_link.unlinked"
    assert DomainEventType.PROJECT_BUILDING_IMPORTED == "project_resource_link.building_imported"


# ── NullEventPublisher ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_null_publisher_does_not_raise() -> None:
    publisher = NullEventPublisher()
    event = _make_event()
    # Must complete silently
    await publisher.publish(event)


# ── InMemoryEventPublisher ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_in_memory_publisher_collects_events() -> None:
    publisher = InMemoryEventPublisher()
    e1 = _make_event(DomainEventType.PROJECT_CREATED)
    e2 = _make_event(DomainEventType.PROJECT_UPDATED)
    e3 = _make_event(DomainEventType.PROJECT_CREATED)

    await publisher.publish(e1)
    await publisher.publish(e2)
    await publisher.publish(e3)

    assert len(publisher.all_events()) == 3


@pytest.mark.asyncio
async def test_in_memory_publisher_filters_by_type() -> None:
    publisher = InMemoryEventPublisher()
    await publisher.publish(_make_event(DomainEventType.PROJECT_CREATED))
    await publisher.publish(_make_event(DomainEventType.PROJECT_DELETED))
    await publisher.publish(_make_event(DomainEventType.PROJECT_CREATED))

    created = publisher.events_of_type(DomainEventType.PROJECT_CREATED)
    deleted = publisher.events_of_type(DomainEventType.PROJECT_DELETED)

    assert len(created) == 2
    assert len(deleted) == 1


@pytest.mark.asyncio
async def test_in_memory_publisher_clear_resets_state() -> None:
    publisher = InMemoryEventPublisher()
    await publisher.publish(_make_event())
    await publisher.publish(_make_event())
    assert len(publisher.all_events()) == 2

    publisher.clear()
    assert len(publisher.all_events()) == 0


@pytest.mark.asyncio
async def test_in_memory_publisher_preserves_payload() -> None:
    publisher = InMemoryEventPublisher()
    event = DomainEvent(
        event_type=DomainEventType.PROJECT_CREATED,
        aggregate_id=uuid.uuid4(),
        payload={"project_id": "abc-123", "owner_id": "xyz-456", "name": "Alpha"},
        occurred_at=datetime(2026, 6, 1, tzinfo=UTC),
    )
    await publisher.publish(event)

    stored = publisher.all_events()[0]
    assert stored.payload["name"] == "Alpha"
    assert stored.payload["project_id"] == "abc-123"
    assert stored.occurred_at == datetime(2026, 6, 1, tzinfo=UTC)
