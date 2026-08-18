from fastapi import APIRouter

from app.api.deps import CurrentOrganization, CurrentUser, DbSession
from app.schemas.auth import (
    ActivateOrganizationRequest,
    ActivateOrganizationResponse,
    LoginRequest,
    MeResponse,
    TokenResponse,
)
from app.services.auth_service import activate_organization, login_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/activate", response_model=ActivateOrganizationResponse)
def activate(
    data: ActivateOrganizationRequest,
    db: DbSession,
) -> ActivateOrganizationResponse:
    """
    Активация организации по лицензионному коду.

    Это первый вход школы в систему.
    """
    token, user, organization = activate_organization(db, data)

    return ActivateOrganizationResponse(
        access_token=token,
        user=user,
        organization=organization,
    )


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    db: DbSession,
) -> TokenResponse:
    """
    Вход пользователя по email и паролю.
    """
    token = login_user(db, data)

    return TokenResponse(
        access_token=token,
    )


@router.get("/me", response_model=MeResponse)
def get_me(
    current_user: CurrentUser,
    current_organization: CurrentOrganization,
) -> MeResponse:
    """
    Возвращает текущего пользователя и его организацию.
    """
    return MeResponse(
        user=current_user,
        organization=current_organization,
    )