from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import LICENSE_STATUS_ACTIVATED
from app.db.models.license import LicenseCode


def get_license_by_code(db: Session, code: str) -> LicenseCode | None:
    statement = select(LicenseCode).where(LicenseCode.code == code.strip())
    return db.scalar(statement)


def create_license_code(
    db: Session,
    *,
    code: str,
    status: str = "new",
    max_users: int | None = None,
    max_assets: int | None = None,
) -> LicenseCode:
    license_code = LicenseCode(
        code=code,
        status=status,
        max_users=max_users,
        max_assets=max_assets,
    )

    db.add(license_code)
    db.flush()

    return license_code


def get_active_license_for_organization(
    db: Session,
    *,
    organization_id: int,
) -> LicenseCode | None:
    statement = (
        select(LicenseCode)
        .where(
            LicenseCode.organization_id == organization_id,
            LicenseCode.status == LICENSE_STATUS_ACTIVATED,
        )
        .order_by(LicenseCode.id.desc())
    )
    return db.scalar(statement)
