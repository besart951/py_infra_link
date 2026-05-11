from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.transaction import atomic
from app.modules.user.domain.errors import UserEmailConflictError
from app.modules.user.domain.models import User
from app.modules.user.domain.value_objects import UserEmail
from app.modules.user.infrastructure.sqlalchemy_models import UserRecord
from app.shared.ids import UserId
from app.shared.pagination import PageParams


def _to_domain(record: UserRecord) -> User:
    return User(
        id=UserId(record.id),
        email=record.email,
        display_name=record.display_name,
        created_at=record.created_at,
    )


@dataclass(frozen=True, slots=True)
class SqlAlchemyUserAdapter:
    _session: AsyncSession

    async def get_by_id(self, user_id: UserId) -> User | None:
        stmt = select(UserRecord).where(UserRecord.id == user_id)
        record = (await self._session.execute(stmt)).scalar_one_or_none()
        if record is None:
            return None
        return _to_domain(record)

    async def get_by_email(self, email: UserEmail) -> User | None:
        stmt = select(UserRecord).where(UserRecord.email == email.value)
        record = (await self._session.execute(stmt)).scalar_one_or_none()
        if record is None:
            return None
        return _to_domain(record)

    async def create(self, user: User) -> User:
        record = UserRecord(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            created_at=user.created_at,
        )

        try:
            async with atomic(self._session):
                self._session.add(record)
                await self._session.flush()
        except IntegrityError as exc:
            raise UserEmailConflictError(f"User with email '{user.email}' already exists") from exc

        return _to_domain(record)

    async def update(self, user: User) -> User:
        stmt = select(UserRecord).where(UserRecord.id == user.id)
        result = await self._session.execute(stmt)
        record = result.scalar_one()
        record.display_name = user.display_name
        await self._session.flush()
        return _to_domain(record)

    async def delete(self, user_id: UserId) -> None:
        stmt = delete(UserRecord).where(UserRecord.id == user_id)
        await self._session.execute(stmt)
        await self._session.flush()

    async def list_page(self, params: PageParams) -> tuple[list[User], int]:
        total_stmt = select(func.count()).select_from(UserRecord)
        total = int((await self._session.execute(total_stmt)).scalar_one())

        stmt = (
            select(UserRecord)
            .order_by(UserRecord.created_at.asc(), UserRecord.id.asc())
            .offset(params.offset)
            .limit(params.limit)
        )
        rows = (await self._session.execute(stmt)).scalars().all()
        return ([_to_domain(row) for row in rows], total)
