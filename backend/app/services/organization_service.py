from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import USER_ROLE_ADMIN
from app.db.models.organization import Organization
from app.db.models.user import User
from app.repositories.organization_repository import get_organization_by_id, update_organization
from app.schemas.organization import OrganizationUpdate


def _ensure_admin(user: User) -> None:
    if user.role != USER_ROLE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав. Требуется роль admin",
        )


def get_current_organization_profile(
    db: Session,
    *,
    current_user: User,
) -> Organization:
    organization = get_organization_by_id(
        db,
        current_user.organization_id,
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Организация не найдена",
        )

    return organization


def update_current_organization_profile(
    db: Session,
    *,
    current_user: User,
    data: OrganizationUpdate,
) -> Organization:
    _ensure_admin(current_user)

    organization = get_current_organization_profile(
        db,
        current_user=current_user,
    )

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        return organization

    updated_organization = update_organization(
        db,
        organization=organization,
        update_data=update_data,
    )

    db.commit()
    db.refresh(updated_organization)

    return updated_organization
