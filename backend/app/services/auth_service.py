from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.utils.datetime import utc_now
from app.core.constants import LICENSE_STATUS_ACTIVATED, USER_ROLE_ADMIN
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models.organization import Organization
from app.db.models.user import User
from app.repositories.organization_repository import (
    create_organization,
    get_organization_by_public_id,
)
from app.repositories.user_repository import create_user, get_user_by_email
from app.schemas.auth import ActivateOrganizationRequest, LoginRequest
from app.services.license_service import validate_license_for_activation
from app.utils.code_generator import generate_organization_public_id


def _generate_unique_organization_public_id(db: Session) -> str:
    """
    Генерирует уникальный 8-значный public_id для организации.
    """
    for _ in range(20):
        public_id = generate_organization_public_id()

        existing = get_organization_by_public_id(db, public_id)

        if existing is None:
            return public_id

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Не удалось сгенерировать ID организации",
    )


def _create_token_for_user(user: User) -> str:
    """
    Создаёт JWT для пользователя.
    """
    return create_access_token(
        subject=str(user.id),
        additional_claims={
            "organization_id": user.organization_id,
            "role": user.role,
        },
    )


def activate_organization(
    db: Session,
    data: ActivateOrganizationRequest,
) -> tuple[str, User, Organization]:
    """
    Активация школы по лицензионному коду.

    Логика:
    1. Проверяем license_code.
    2. Проверяем, что email администратора свободен.
    3. Создаём организацию.
    4. Создаём первого пользователя-админа.
    5. Помечаем код активированным.
    6. Возвращаем token, user, organization.
    """
    license_code = validate_license_for_activation(db, data.license_code)

    existing_user = get_user_by_email(db, data.admin_email)

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует",
        )

    public_id = _generate_unique_organization_public_id(db)

    try:
        organization = create_organization(
            db,
            public_id=public_id,
            name=data.organization_name,
        )

        user = create_user(
            db,
            organization_id=organization.id,
            email=data.admin_email,
            password_hash=hash_password(data.admin_password),
            full_name=data.admin_full_name,
            role=USER_ROLE_ADMIN,
        )

        license_code.organization_id = organization.id
        license_code.status = LICENSE_STATUS_ACTIVATED
        license_code.activated_at = utc_now()

        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Конфликт данных при активации организации",
        )

    db.refresh(organization)
    db.refresh(user)

    token = _create_token_for_user(user)

    return token, user, organization


def authenticate_user(
    db: Session,
    data: LoginRequest,
) -> User:
    """
    Проверяет email и пароль пользователя.
    """
    user = get_user_by_email(db, data.email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь отключён",
        )

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    user.last_login_at = utc_now()
    db.commit()
    db.refresh(user)

    return user


def login_user(
    db: Session,
    data: LoginRequest,
) -> str:
    user = authenticate_user(db, data)
    return _create_token_for_user(user)
