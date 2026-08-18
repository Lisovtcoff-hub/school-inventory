from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.utils.datetime import utc_now
from app.core.constants import LICENSE_STATUS_NEW
from app.db.models.license import LicenseCode
from app.repositories.license_repository import (
    get_active_license_for_organization,
    get_license_by_code,
)


def validate_license_for_activation(
    db: Session,
    license_code_value: str,
) -> LicenseCode:
    """
    Проверяет, что лицензионный код существует и может быть активирован.
    """
    license_code = get_license_by_code(db, license_code_value)

    if license_code is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Лицензионный код не найден",
        )

    if license_code.status != LICENSE_STATUS_NEW:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Лицензионный код уже использован или недоступен",
        )

    if license_code.expires_at is not None and license_code.expires_at < utc_now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Срок действия лицензии истек",
        )

    return license_code


def get_current_license_or_none(
    db: Session,
    *,
    organization_id: int,
) -> LicenseCode | None:
    """
    Возвращает активированную лицензию организации.

    Для совместимости со старыми/dev-базами отсутствие лицензии не блокирует
    чтение данных и не валит приложение целиком. Ограничения применяются,
    когда у организации есть активированная лицензия с заданными лимитами.
    """
    return get_active_license_for_organization(
        db,
        organization_id=organization_id,
    )


def ensure_license_allows_write(
    db: Session,
    *,
    organization_id: int,
) -> LicenseCode | None:
    """
    Проверяет срок лицензии перед операциями создания.

    Чтение существующих данных не блокируется даже при истёкшей лицензии.
    """
    license_code = get_current_license_or_none(
        db,
        organization_id=organization_id,
    )

    if license_code is None:
        return None

    if license_code.expires_at is not None and license_code.expires_at < utc_now():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Срок действия лицензии истек",
        )

    return license_code
