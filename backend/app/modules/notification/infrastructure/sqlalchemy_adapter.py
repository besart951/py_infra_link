from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notification.domain.models import Notification
from app.modules.notification.infrastructure.sqlalchemy_models import NotificationOrm
from app.shared.ids import NotificationId, UserId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class SqlAlchemyNotificationAdapter:
    _session: AsyncSession

    async def create(self, notification: Notification) -> Notification:
        orm = NotificationOrm(
            id=notification.id,
            user_id=notification.user_id,
            title=notification.title,
            body=notification.body,
            is_read=notification.is_read,
            created_at=notification.created_at,
        )
        self._session.add(orm)
        await self._session.flush()
        return notification

    async def get_by_id(
        self, notification_id: NotificationId
    ) -> Notification | None:
        stmt = select(NotificationOrm).where(NotificationOrm.id == notification_id)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def mark_as_read(
        self, notification_id: NotificationId
    ) -> Notification | None:
        stmt = (
            update(NotificationOrm)
            .where(NotificationOrm.id == notification_id)
            .values(is_read=True)
            .returning(NotificationOrm)
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def mark_all_as_read(self, user_id: UserId) -> int:
        stmt = (
            update(NotificationOrm)
            .where(
                NotificationOrm.user_id == user_id,
                NotificationOrm.is_read.is_(False),
            )
            .values(is_read=True)
            .returning(NotificationOrm.id)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return len(result.all())

    async def list_page(
        self,
        user_id: UserId,
        params: PageParams,
        *,
        unread_only: bool = False,
    ) -> tuple[list[Notification], int]:
        base_filter = [NotificationOrm.user_id == user_id]
        if unread_only:
            base_filter.append(NotificationOrm.is_read.is_(False))

        count_stmt = (
            select(func.count())
            .select_from(NotificationOrm)
            .where(*base_filter)
        )
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0

        stmt = (
            select(NotificationOrm)
            .where(*base_filter)
            .order_by(NotificationOrm.created_at.desc())
            .offset(params.offset)
            .limit(params.size)
        )
        result = await self._session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms], total

    async def delete(self, notification_id: NotificationId) -> None:
        stmt = delete(NotificationOrm).where(NotificationOrm.id == notification_id)
        await self._session.execute(stmt)
        await self._session.flush()

    def _to_domain(self, orm: NotificationOrm) -> Notification:
        return Notification(
            id=NotificationId(orm.id),
            user_id=UserId(orm.user_id),
            title=orm.title,
            body=orm.body,
            is_read=orm.is_read,
            created_at=orm.created_at,
        )
