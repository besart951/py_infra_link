from __future__ import annotations

from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.database.session import get_session
from app.modules.auth.infrastructure.jwt_codec import jwt_decode
from app.modules.user.domain.models import User
from app.modules.user.infrastructure.sqlalchemy_adapter import SqlAlchemyUserAdapter
from app.shared.ids import UserId

_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),  # noqa: B008
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> User:
    """FastAPI dependency that validates a Bearer JWT and returns the owner ``User``.

    Raises ``HTTP 401`` for any token problem (missing, expired, malformed,
    or referencing a user that no longer exists).
    """
    _unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    settings = get_settings()
    try:
        payload = jwt_decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        user_id_str = payload.get("sub")
        if not isinstance(user_id_str, str):
            raise _unauthorized
        user_id = UserId(UUID(user_id_str))
    except (jwt.InvalidTokenError, ValueError):
        raise _unauthorized from None

    adapter = SqlAlchemyUserAdapter(session)
    user = await adapter.get_by_id(user_id)
    if user is None:
        raise _unauthorized

    return user
