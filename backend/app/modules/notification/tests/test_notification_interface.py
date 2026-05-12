from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from app.modules.live_update.domain.events import DomainEvent, DomainEventType
from app.modules.notification.application.commands import (
    DeleteNotificationCommand,
    MarkAllReadCommand,
    MarkAsReadCommand,
)
from app.modules.notification.application.queries import ListNotificationsQuery
from app.modules.notification.application.use_cases import NotificationModule
from app.modules.notification.domain.errors import NotificationNotFoundError
from app.modules.notification.domain.models import Notification
from app.modules.notification.infrastructure.event_publisher import (
    NotificationEventPublisher,
)
from app.modules.notification.infrastructure.in_memory_adapter import (
    InMemoryNotificationAdapter,
)
from app.shared.clock import FixedClock
from app.shared.ids import NotificationId, UserId, new_id
from app.shared.pagination import PageParams
from app.shared.result import Err, Ok


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(datetime(2026, 1, 1, tzinfo=UTC))


@pytest.fixture
def repo() -> InMemoryNotificationAdapter:
    return InMemoryNotificationAdapter()


@pytest.fixture
def module(repo: InMemoryNotificationAdapter) -> NotificationModule:
    return NotificationModule(notification_repository=repo)


def _make_notification(user_id: UserId, clock: FixedClock, *, is_read: bool = False) -> Notification:
    return Notification(
        id=new_id(NotificationId),
        user_id=user_id,
        title="Test",
        body="Test body",
        is_read=is_read,
        created_at=clock.now(),
    )


# ── NotificationModule ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_notifications_empty(
    module: NotificationModule,
) -> None:
    user_id = new_id(UserId)
    page = await module.list_notifications(
        ListNotificationsQuery(user_id=user_id, page=PageParams(page=1, size=10))
    )
    assert page.total == 0
    assert page.items == []


@pytest.mark.asyncio
async def test_list_notifications_scoped_to_user(
    module: NotificationModule,
    repo: InMemoryNotificationAdapter,
    clock: FixedClock,
) -> None:
    user_a = new_id(UserId)
    user_b = new_id(UserId)
    await repo.create(_make_notification(user_a, clock))
    await repo.create(_make_notification(user_a, clock))
    await repo.create(_make_notification(user_b, clock))

    page = await module.list_notifications(
        ListNotificationsQuery(user_id=user_a, page=PageParams(page=1, size=10))
    )
    assert page.total == 2
    assert all(n.user_id == user_a for n in page.items)


@pytest.mark.asyncio
async def test_list_notifications_unread_only(
    module: NotificationModule,
    repo: InMemoryNotificationAdapter,
    clock: FixedClock,
) -> None:
    user_id = new_id(UserId)
    await repo.create(_make_notification(user_id, clock, is_read=False))
    await repo.create(_make_notification(user_id, clock, is_read=True))
    await repo.create(_make_notification(user_id, clock, is_read=False))

    page = await module.list_notifications(
        ListNotificationsQuery(
            user_id=user_id,
            page=PageParams(page=1, size=10),
            unread_only=True,
        )
    )
    assert page.total == 2
    assert all(not n.is_read for n in page.items)


@pytest.mark.asyncio
async def test_mark_as_read_success(
    module: NotificationModule,
    repo: InMemoryNotificationAdapter,
    clock: FixedClock,
) -> None:
    user_id = new_id(UserId)
    notification = await repo.create(_make_notification(user_id, clock))
    assert not notification.is_read

    result = await module.mark_as_read(
        MarkAsReadCommand(user_id=user_id, notification_id=notification.id)
    )

    assert isinstance(result, Ok)
    assert result.unwrap().is_read is True


@pytest.mark.asyncio
async def test_mark_as_read_not_found(
    module: NotificationModule,
) -> None:
    result = await module.mark_as_read(
        MarkAsReadCommand(
            user_id=new_id(UserId),
            notification_id=new_id(NotificationId),
        )
    )
    assert isinstance(result, Err)
    assert isinstance(result.error, NotificationNotFoundError)


@pytest.mark.asyncio
async def test_mark_as_read_wrong_user_treated_as_not_found(
    module: NotificationModule,
    repo: InMemoryNotificationAdapter,
    clock: FixedClock,
) -> None:
    owner = new_id(UserId)
    notification = await repo.create(_make_notification(owner, clock))

    result = await module.mark_as_read(
        MarkAsReadCommand(
            user_id=new_id(UserId),
            notification_id=notification.id,
        )
    )
    assert isinstance(result, Err)
    assert isinstance(result.error, NotificationNotFoundError)


@pytest.mark.asyncio
async def test_mark_all_as_read(
    module: NotificationModule,
    repo: InMemoryNotificationAdapter,
    clock: FixedClock,
) -> None:
    user_id = new_id(UserId)
    await repo.create(_make_notification(user_id, clock, is_read=False))
    await repo.create(_make_notification(user_id, clock, is_read=False))
    await repo.create(_make_notification(user_id, clock, is_read=True))

    marked = await module.mark_all_as_read(MarkAllReadCommand(user_id=user_id))
    assert marked == 2

    page = await module.list_notifications(
        ListNotificationsQuery(
            user_id=user_id,
            page=PageParams(page=1, size=10),
            unread_only=True,
        )
    )
    assert page.total == 0


@pytest.mark.asyncio
async def test_delete_notification_success(
    module: NotificationModule,
    repo: InMemoryNotificationAdapter,
    clock: FixedClock,
) -> None:
    user_id = new_id(UserId)
    notification = await repo.create(_make_notification(user_id, clock))

    result = await module.delete_notification(
        DeleteNotificationCommand(
            user_id=user_id,
            notification_id=notification.id,
        )
    )
    assert isinstance(result, Ok)

    page = await module.list_notifications(
        ListNotificationsQuery(user_id=user_id, page=PageParams(page=1, size=10))
    )
    assert page.total == 0


@pytest.mark.asyncio
async def test_delete_notification_wrong_user_treated_as_not_found(
    module: NotificationModule,
    repo: InMemoryNotificationAdapter,
    clock: FixedClock,
) -> None:
    owner = new_id(UserId)
    notification = await repo.create(_make_notification(owner, clock))

    result = await module.delete_notification(
        DeleteNotificationCommand(
            user_id=new_id(UserId),
            notification_id=notification.id,
        )
    )
    assert isinstance(result, Err)
    assert isinstance(result.error, NotificationNotFoundError)


# ── NotificationEventPublisher ─────────────────────────────────────────────────


def _make_event(
    event_type: DomainEventType,
    payload: dict[str, str],
) -> DomainEvent:
    return DomainEvent(
        event_type=event_type,
        aggregate_id=uuid.uuid4(),
        payload=payload,
        occurred_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


@pytest.fixture
def event_publisher(
    repo: InMemoryNotificationAdapter, clock: FixedClock
) -> NotificationEventPublisher:
    return NotificationEventPublisher(_repository=repo, _clock=clock)


@pytest.mark.asyncio
async def test_event_publisher_project_created(
    event_publisher: NotificationEventPublisher,
    repo: InMemoryNotificationAdapter,
    clock: FixedClock,
) -> None:
    owner_id = new_id(UserId)
    event = _make_event(
        DomainEventType.PROJECT_CREATED,
        {"project_id": str(uuid.uuid4()), "owner_id": str(owner_id), "name": "Alpha"},
    )
    await event_publisher.publish(event)

    items, total = await repo.list_page(owner_id, PageParams(page=1, size=10))
    assert total == 1
    assert items[0].title == "Project created"
    assert "Alpha" in items[0].body
    assert items[0].is_read is False


@pytest.mark.asyncio
async def test_event_publisher_resource_linked(
    event_publisher: NotificationEventPublisher,
    repo: InMemoryNotificationAdapter,
    clock: FixedClock,
) -> None:
    owner_id = new_id(UserId)
    event = _make_event(
        DomainEventType.PROJECT_RESOURCE_LINKED,
        {
            "link_id": str(uuid.uuid4()),
            "project_id": str(uuid.uuid4()),
            "resource_type": "building",
            "resource_id": str(uuid.uuid4()),
            "owner_id": str(owner_id),
        },
    )
    await event_publisher.publish(event)

    items, total = await repo.list_page(owner_id, PageParams(page=1, size=10))
    assert total == 1
    assert items[0].title == "Resource linked"


@pytest.mark.asyncio
async def test_event_publisher_building_imported(
    event_publisher: NotificationEventPublisher,
    repo: InMemoryNotificationAdapter,
    clock: FixedClock,
) -> None:
    owner_id = new_id(UserId)
    event = _make_event(
        DomainEventType.PROJECT_BUILDING_IMPORTED,
        {
            "project_id": str(uuid.uuid4()),
            "building_id": str(uuid.uuid4()),
            "linked": "7",
            "skipped": "1",
            "owner_id": str(owner_id),
        },
    )
    await event_publisher.publish(event)

    items, _ = await repo.list_page(owner_id, PageParams(page=1, size=10))
    assert items[0].title == "Building imported"
    assert "7" in items[0].body


@pytest.mark.asyncio
async def test_event_publisher_ignores_missing_owner_id(
    event_publisher: NotificationEventPublisher,
    repo: InMemoryNotificationAdapter,
) -> None:
    """Events without owner_id in payload should produce no notification."""
    event = _make_event(
        DomainEventType.PROJECT_CREATED,
        {"project_id": str(uuid.uuid4()), "name": "No Owner"},
    )
    await event_publisher.publish(event)

    user_id = new_id(UserId)
    _, total = await repo.list_page(user_id, PageParams(page=1, size=10))
    assert total == 0
