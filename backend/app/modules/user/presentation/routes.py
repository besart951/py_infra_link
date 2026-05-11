from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.modules.user.application.commands import CreateUserCommand
from app.modules.user.application.queries import GetUserQuery, ListUsersQuery
from app.modules.user.application.use_cases import UserModule
from app.modules.user.infrastructure.sqlalchemy_adapter import SqlAlchemyUserAdapter
from app.modules.user.presentation.error_mapping import map_user_error
from app.modules.user.presentation.schemas import CreateUserRequest, UserPageResponse, UserResponse
from app.shared.clock import SystemClock
from app.shared.ids import UserId
from app.shared.pagination import PageParams
from app.shared.result import Ok

router = APIRouter(prefix="/users", tags=["users"])


def _to_response(
    user_id: UserId, email: str, display_name: str, created_at: datetime
) -> UserResponse:
    return UserResponse(
        id=str(user_id),
        email=email,
        display_name=display_name,
        created_at=created_at,
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: CreateUserRequest,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> UserResponse:
    module = UserModule(repository=SqlAlchemyUserAdapter(session), clock=SystemClock())
    result = await module.create_user(
        CreateUserCommand(email=request.email, display_name=request.display_name)
    )

    if isinstance(result, Ok):
        user = result.value
        return _to_response(user.id, user.email, user.display_name, user.created_at)

    raise map_user_error(result.error)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> UserResponse:
    module = UserModule(repository=SqlAlchemyUserAdapter(session), clock=SystemClock())
    result = await module.get_user(GetUserQuery(user_id=UserId(user_id)))

    if isinstance(result, Ok):
        user = result.value
        return _to_response(user.id, user.email, user.display_name, user.created_at)

    raise map_user_error(result.error)


@router.get("", response_model=UserPageResponse)
async def list_users(
    page: int = 1,
    size: int = 20,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> UserPageResponse:
    module = UserModule(repository=SqlAlchemyUserAdapter(session), clock=SystemClock())
    result = await module.list_users(ListUsersQuery(page=PageParams(page=page, size=size)))

    return UserPageResponse(
        items=[
            _to_response(user.id, user.email, user.display_name, user.created_at)
            for user in result.items
        ],
        total=result.total,
        page=result.page,
        size=result.size,
        pages=result.pages,
        has_next=result.has_next,
        has_prev=result.has_prev,
    )
