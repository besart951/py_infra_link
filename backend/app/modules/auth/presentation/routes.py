from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.database.session import get_session
from app.modules.auth.application.commands import LoginCommand, RegisterCommand
from app.modules.auth.application.use_cases import AuthModule, JwtSettings
from app.modules.auth.infrastructure.password_hasher import BcryptPasswordHasher
from app.modules.auth.infrastructure.sqlalchemy_adapter import SqlAlchemyCredentialAdapter
from app.modules.auth.presentation.error_mapping import map_auth_error
from app.modules.auth.presentation.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.modules.user.application.use_cases import UserModule
from app.modules.user.infrastructure.sqlalchemy_adapter import SqlAlchemyUserAdapter
from app.shared.clock import SystemClock
from app.shared.result import Ok

router = APIRouter(prefix="/auth", tags=["auth"])


def _make_module(session: AsyncSession) -> AuthModule:
    settings = get_settings()
    user_adapter = SqlAlchemyUserAdapter(session)
    return AuthModule(
        user_module=UserModule(repository=user_adapter, clock=SystemClock()),
        user_repository=user_adapter,
        credential_repository=SqlAlchemyCredentialAdapter(session),
        hasher=BcryptPasswordHasher(),
        jwt_settings=JwtSettings(
            secret_key=settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
            expire_minutes=settings.jwt_expire_minutes,
        ),
        clock=SystemClock(),
    )


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user and receive an access token.",
)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> TokenResponse:
    module = _make_module(session)
    result = await module.register(
        RegisterCommand(
            email=request.email,
            password=request.password,
            display_name=request.display_name,
        )
    )

    if isinstance(result, Ok):
        return TokenResponse(access_token=result.value.access_token)

    raise map_auth_error(result.error)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate with email and password and receive an access token.",
)
async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> TokenResponse:
    module = _make_module(session)
    result = await module.login(LoginCommand(email=request.email, password=request.password))

    if isinstance(result, Ok):
        return TokenResponse(access_token=result.value.access_token)

    raise map_auth_error(result.error)
