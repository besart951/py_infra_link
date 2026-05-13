from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from uuid import UUID

from app.modules.auth.application.commands import LoginCommand, RegisterCommand
from app.modules.auth.domain.errors import InvalidCredentialsError, WeakPasswordError
from app.modules.auth.domain.interface import CredentialRepository, PasswordHasher
from app.modules.auth.domain.models import IssuedToken, UserCredential
from app.modules.auth.domain.value_objects import RawPassword
from app.modules.auth.infrastructure.jwt_codec import jwt_encode
from app.modules.user.application.commands import CreateUserCommand
from app.modules.user.application.use_cases import UserModule
from app.modules.user.domain.errors import (
    InvalidUserDisplayNameError,
    InvalidUserEmailError,
    UserEmailConflictError,
)
from app.modules.user.domain.interface import UserRepository
from app.modules.user.domain.value_objects import UserEmail
from app.shared.clock import Clock
from app.shared.ids import UserId
from app.shared.result import Err, Ok, Result


@dataclass(frozen=True, slots=True)
class JwtSettings:
    """Immutable JWT configuration injected into AuthModule."""

    secret_key: str
    algorithm: str
    expire_minutes: int


@dataclass(frozen=True, slots=True)
class AuthModule:
    user_module: UserModule
    user_repository: UserRepository
    credential_repository: CredentialRepository
    hasher: PasswordHasher
    jwt_settings: JwtSettings
    clock: Clock

    # ── public interface ──────────────────────────────────────────────────────

    async def register(
        self, command: RegisterCommand
    ) -> Result[
        IssuedToken,
        UserEmailConflictError
        | InvalidUserEmailError
        | InvalidUserDisplayNameError
        | WeakPasswordError,
    ]:
        try:
            password = RawPassword.parse(command.password)
        except WeakPasswordError as exc:
            return Err(exc)

        user_result = await self.user_module.create_user(
            CreateUserCommand(email=command.email, display_name=command.display_name)
        )
        if isinstance(user_result, Err):
            return Err(user_result.error)

        user = user_result.value
        credential = UserCredential(
            user_id=user.id,
            password_hash=self.hasher.hash(password.value),
        )
        await self.credential_repository.create(credential)
        return Ok(self._issue_token(str(user.id)))

    async def login(
        self, command: LoginCommand
    ) -> Result[IssuedToken, InvalidCredentialsError]:
        _invalid = InvalidCredentialsError("Invalid email or password")

        try:
            email = UserEmail.parse(command.email)
        except Exception:
            return Err(_invalid)

        user = await self.user_repository.get_by_email(email)
        if user is None:
            return Err(_invalid)

        credential = await self.credential_repository.get_by_user_id(user.id)
        if credential is None:
            return Err(_invalid)

        if not self.hasher.verify(command.password, credential.password_hash):
            return Err(_invalid)

        return Ok(self._issue_token(str(user.id)))

    # ── private helpers ───────────────────────────────────────────────────────

    def _issue_token(self, user_id_str: str) -> IssuedToken:
        expiry = self.clock.now() + timedelta(minutes=self.jwt_settings.expire_minutes)
        payload = {
            "sub": user_id_str,
            "exp": int(expiry.timestamp()),
        }
        token = jwt_encode(
            payload,
            self.jwt_settings.secret_key,
            algorithm=self.jwt_settings.algorithm,
        )
        return IssuedToken(
            access_token=token,
            user_id=UserId(UUID(user_id_str)),
        )
