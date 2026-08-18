from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.constants import ALLOWED_USER_ROLES, USER_ROLE_ADMIN
from app.core.security import hash_password
from app.db.models.user import User
from app.repositories.user_repository import (
    count_active_users_by_organization,
    create_user,
    get_user_by_email,
    list_users_by_organization,
)
from app.schemas.user import UserCreate, UserListResponse
from app.services.license_service import ensure_license_allows_write


def _ensure_admin(user: User) -> None:
    if user.role != USER_ROLE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав. Требуется роль admin",
        )


def _validate_role(role: str) -> None:
    if role not in ALLOWED_USER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимая роль пользователя: {role}",
        )


def _ensure_license_allows_user_creation(db: Session, *, organization_id: int) -> None:
    license_code = ensure_license_allows_write(
        db,
        organization_id=organization_id,
    )

    if license_code is None or license_code.max_users is None:
        return

    current_users_count = count_active_users_by_organization(
        db,
        organization_id=organization_id,
    )

    if current_users_count >= license_code.max_users:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Превышен лимит пользователей по лицензии",
        )


def get_users_for_current_organization(
    db: Session,
    *,
    current_user: User,
) -> UserListResponse:
    _ensure_admin(current_user)

    users = list_users_by_organization(
        db,
        organization_id=current_user.organization_id,
    )

    return UserListResponse(
        items=users,
        total=len(users),
    )


def create_user_for_current_organization(
    db: Session,
    *,
    current_user: User,
    data: UserCreate,
) -> User:
    _ensure_admin(current_user)
    _validate_role(data.role)
    _ensure_license_allows_user_creation(
        db,
        organization_id=current_user.organization_id,
    )

    existing_user = get_user_by_email(db, data.email)

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует",
        )

    try:
        user = create_user(
            db,
            organization_id=current_user.organization_id,
            email=data.email,
            password_hash=hash_password(data.password),
            full_name=data.full_name,
            role=data.role,
        )

        db.commit()
        db.refresh(user)

        return user

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Конфликт данных при создании пользователя",
        )
