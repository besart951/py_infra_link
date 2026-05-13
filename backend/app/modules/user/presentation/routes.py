from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.modules.user.application.commands import CreateUserCommand
from app.modules.user.application.queries import GetUserQuery, ListUsersQuery
from app.modules.user.application.use_cases import UserModule
from app.modules.user.infrastructure.sqlalchemy_adapter import SqlAlchemyUserAdapter
from app.modules.user.presentation.error_mapping import map_user_error
from app.modules.user.presentation.schemas import CreateUserRequest, UserResponse
from app.shared.clock import SystemClock
from app.shared.ids import UserId
from app.shared.pagination import Page, PageParams
from app.shared.result import Ok

router = APIRouter(prefix="/users", tags=["users"])


def _make_module(session: AsyncSession) -> UserModule:
    return UserModule(repository=SqlAlchemyUserAdapter(session), clock=SystemClock())


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: CreateUserRequest,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> UserResponse:
    module = _make_module(session)
    result = await module.create_user(
        CreateUserCommand(email=request.email, display_name=request.display_name)
    )

    if isinstance(result, Ok):
        return UserResponse.model_validate(result.value)

    raise map_user_error(result.error)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> UserResponse:
    module = _make_module(session)
    result = await module.get_user(GetUserQuery(user_id=UserId(user_id)))

    if isinstance(result, Ok):
        return UserResponse.model_validate(result.value)

    raise map_user_error(result.error)


@router.get("", response_model=Page[UserResponse])
async def list_users(
    page: int = 1,
    size: int = 20,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> Page[UserResponse]:
    module = _make_module(session)
    result = await module.list_users(ListUsersQuery(page=PageParams(page=page, size=size)))

    return Page[UserResponse](
        items=[UserResponse.model_validate(user) for user in result.items],
        total=result.total,
        page=result.page,
        size=result.size,
    )
