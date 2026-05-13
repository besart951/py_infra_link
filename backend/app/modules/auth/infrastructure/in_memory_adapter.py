from __future__ import annotations

from dataclasses import dataclass, field

from app.modules.auth.domain.models import UserCredential
from app.shared.ids import UserId


def _credential_store() -> dict[UserId, UserCredential]:
    return {}


@dataclass(frozen=True, slots=True)
class InMemoryCredentialAdapter:
    _credentials: dict[UserId, UserCredential] = field(
        default_factory=_credential_store
    )

    async def get_by_user_id(self, user_id: UserId) -> UserCredential | None:
        return self._credentials.get(user_id)

    async def create(self, credential: UserCredential) -> UserCredential:
        self._credentials[credential.user_id] = credential
        return credential
