from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.models.organization import Organization
from app.db.models.user import User
from app.db.session import get_db
from app.repositories.organization_repository import get_organization_by_id
from app.repositories.user_repository import get_user_by_id


DbSession = Annotated[Session, Depends(get_db)]

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    db: DbSession,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> User:
    """
    Достаёт текущего пользователя из JWT.

    Ожидает заголовок:

    Authorization: Bearer <token>
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Необходима авторизация",
        )

    token = credentials.credentials

    try:
        payload = decode_access_token(token)
        user_id_raw = payload.get("sub")

        if user_id_raw is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Некорректный токен",
            )

        user_id = int(user_id_raw)

    except (jwt.PyJWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректный или истёкший токен",
        )

    user = get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь отключён",
        )

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_organization(
    db: DbSession,
    current_user: CurrentUser,
) -> Organization:
    """
    Возвращает организацию текущего пользователя.
    """
    organization = get_organization_by_id(
        db,
        current_user.organization_id,
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Организация не найдена",
        )

    if not organization.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Организация отключена",
        )

    return organization


CurrentOrganization = Annotated[
    Organization,
    Depends(get_current_organization),
]