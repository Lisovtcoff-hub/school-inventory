from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.user import UserCreate, UserListResponse, UserRead
from app.services.user_service import (
    create_user_for_current_organization,
    get_users_for_current_organization,
)


router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=UserListResponse)
def get_users(
    db: DbSession,
    current_user: CurrentUser,
) -> UserListResponse:
    """
    Получить список пользователей текущей организации.

    Доступно только admin.
    """
    return get_users_for_current_organization(
        db,
        current_user=current_user,
    )


@router.post("", response_model=UserRead)
def create_user(
    data: UserCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> UserRead:
    """
    Создать пользователя внутри текущей организации.

    Доступно только admin.
    """
    return create_user_for_current_organization(
        db,
        current_user=current_user,
        data=data,
    )
