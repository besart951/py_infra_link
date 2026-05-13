"""Integration tests for SqlAlchemyNotificationAdapter against a real PostgreSQL database."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notification.application.commands import (
    DeleteNotificationCommand,
    MarkAllReadCommand,
    MarkAsReadCommand,
)
from app.modules.notification.application.queries import ListNotificationsQuery
from app.modules.notification.application.use_cases import NotificationModule
from app.modules.notification.domain.errors import NotificationNotFoundError
from app.modules.notification.infrastructure.sqlalchemy_adapter import (
    SqlAlchemyNotificationAdapter,
)
from app.modules.user.application.commands import CreateUserCommand
from app.modules.user.application.use_cases import UserModule
from app.modules.user.infrastructure.sqlalchemy_adapter import SqlAlchemyUserAdapter
from app.shared.clock import FixedClock
from app.shared.ids import NotificationId, UserId, new_id
from app.shared.pagination import PageParams
from app.shared.result import Err, Ok

_FIXED = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


async def _create_user(session: AsyncSession, email: str) -> UserId:
    module = UserModule(
        repository=SqlAlchemyUserAdapter(session), clock=FixedClock(_FIXED)
    )
    result = await module.create_user(CreateUserCommand(email=email, display_name="Test"))
    assert isinstance(result, Ok)
    return result.value.id


def _make_module(session: AsyncSession) -> NotificationModule:
    return NotificationModule(
        notification_repository=SqlAlchemyNotificationAdapter(session),
    )


async def _seed_notification(
    session: AsyncSession,
    user_id: UserId,
    title: str = "Title",
    body: str = "Body",
) -> NotificationId:
    """Create a notification directly via the adapter and return its id."""
    from app.modules.notification.domain.models import Notification

    adapter = SqlAlchemyNotificationAdapter(session)
    notif = Notification(
        id=new_id(NotificationId),
        user_id=user_id,
        title=title,
        body=body,
        is_read=False,
        created_at=_FIXED,
    )
    created = await adapter.create(notif)
    return created.id


@pytest.mark.asyncio
async def test_mark_as_read(session: AsyncSession) -> None:
    user_id = await _create_user(session, "notif_read@example.com")
    module = _make_module(session)
    notif_id = await _seed_notification(session, user_id)

    result = await module.mark_as_read(
        MarkAsReadCommand(user_id=user_id, notification_id=notif_id)
    )
    assert isinstance(result, Ok)
    assert result.value.is_read is True


@pytest.mark.asyncio
async def test_mark_as_read_not_found(session: AsyncSession) -> None:
    user_id = await _create_user(session, "notif_missing@example.com")
    module = _make_module(session)

    result = await module.mark_as_read(
        MarkAsReadCommand(user_id=user_id, notification_id=new_id(NotificationId))
    )
    assert isinstance(result, Err)
    assert isinstance(result.error, NotificationNotFoundError)


@pytest.mark.asyncio
async def test_mark_all_as_read(session: AsyncSession) -> None:
    user_id = await _create_user(session, "notif_all_read@example.com")
    module = _make_module(session)

    # Seed 3 unread notifications
    for i in range(3):
        await _seed_notification(session, user_id, title=f"N{i}")

    marked = await module.mark_all_as_read(MarkAllReadCommand(user_id=user_id))
    assert marked == 3

    # All are now read — calling again returns 0
    marked_again = await module.mark_all_as_read(MarkAllReadCommand(user_id=user_id))
    assert marked_again == 0


@pytest.mark.asyncio
async def test_list_notifications_pagination(session: AsyncSession) -> None:
    user_id = await _create_user(session, "notif_page@example.com")
    module = _make_module(session)

    for i in range(4):
        await _seed_notification(session, user_id, title=f"Page Notif {i}")

    result = await module.list_notifications(
        ListNotificationsQuery(
            user_id=user_id,
            page=PageParams(page=1, size=2),
            unread_only=False,
        )
    )
    assert result.total == 4
    assert len(result.items) == 2


@pytest.mark.asyncio
async def test_list_notifications_unread_only(session: AsyncSession) -> None:
    user_id = await _create_user(session, "notif_unread@example.com")
    module = _make_module(session)

    id1 = await _seed_notification(session, user_id, title="Unread 1")
    id2 = await _seed_notification(session, user_id, title="Unread 2")
    _id3 = await _seed_notification(session, user_id, title="Read")

    # Mark third as read
    await module.mark_as_read(MarkAsReadCommand(user_id=user_id, notification_id=_id3))

    result = await module.list_notifications(
        ListNotificationsQuery(
            user_id=user_id,
            page=PageParams(page=1, size=10),
            unread_only=True,
        )
    )
    assert result.total == 2
    returned_ids = {n.id for n in result.items}
    assert id1 in returned_ids
    assert id2 in returned_ids


@pytest.mark.asyncio
async def test_delete_notification(session: AsyncSession) -> None:
    user_id = await _create_user(session, "notif_del@example.com")
    module = _make_module(session)
    notif_id = await _seed_notification(session, user_id)

    delete_result = await module.delete_notification(
        DeleteNotificationCommand(user_id=user_id, notification_id=notif_id)
    )
    assert isinstance(delete_result, Ok)

    # Should no longer show up in the listing
    result = await module.list_notifications(
        ListNotificationsQuery(
            user_id=user_id,
            page=PageParams(page=1, size=10),
            unread_only=False,
        )
    )
    assert result.total == 0
