from __future__ import annotations

from typing import Protocol

from app.modules.auth.domain.models import UserCredential
from app.shared.ids import UserId


class CredentialRepository(Protocol):
    async def get_by_user_id(self, user_id: UserId) -> UserCredential | None: ...

    async def create(self, credential: UserCredential) -> UserCredential: ...


class PasswordHasher(Protocol):
    def hash(self, raw_password: str) -> str: ...

    def verify(self, raw_password: str, hashed: str) -> bool: ...
