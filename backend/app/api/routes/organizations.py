from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.organization import OrganizationRead, OrganizationUpdate
from app.services.organization_service import (
    get_current_organization_profile,
    update_current_organization_profile,
)


router = APIRouter(prefix="/organization", tags=["organization"])


@router.get("/me", response_model=OrganizationRead)
def get_my_organization(
    db: DbSession,
    current_user: CurrentUser,
) -> OrganizationRead:
    """
    Получить профиль текущей организации.
    """
    return get_current_organization_profile(
        db,
        current_user=current_user,
    )


@router.put("/me", response_model=OrganizationRead)
def update_my_organization(
    data: OrganizationUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> OrganizationRead:
    """
    Обновить профиль текущей организации.

    Доступно только пользователю с ролью admin.
    """
    return update_current_organization_profile(
        db,
        current_user=current_user,
        data=data,
    )
