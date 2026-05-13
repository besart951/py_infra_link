from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.domain.models import UserCredential
from app.modules.auth.infrastructure.sqlalchemy_models import UserCredentialRecord
from app.shared.ids import UserId


def _to_domain(record: UserCredentialRecord) -> UserCredential:
    return UserCredential(
        user_id=UserId(record.user_id),
        password_hash=record.password_hash,
    )


@dataclass(frozen=True, slots=True)
class SqlAlchemyCredentialAdapter:
    _session: AsyncSession

    async def get_by_user_id(self, user_id: UserId) -> UserCredential | None:
        stmt = select(UserCredentialRecord).where(
            UserCredentialRecord.user_id == user_id
        )
        record = (await self._session.execute(stmt)).scalar_one_or_none()
        return _to_domain(record) if record else None

    async def create(self, credential: UserCredential) -> UserCredential:
        record = UserCredentialRecord(
            user_id=credential.user_id,
            password_hash=credential.password_hash,
        )
        self._session.add(record)
        await self._session.flush()
        return _to_domain(record)
