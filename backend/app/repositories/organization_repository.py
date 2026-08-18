from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.organization import Organization


def get_organization_by_id(
    db: Session,
    organization_id: int,
) -> Organization | None:
    statement = select(Organization).where(Organization.id == organization_id)
    return db.scalar(statement)


def get_organization_by_public_id(
    db: Session,
    public_id: str,
) -> Organization | None:
    statement = select(Organization).where(Organization.public_id == public_id)
    return db.scalar(statement)


def create_organization(
    db: Session,
    *,
    public_id: str,
    name: str,
) -> Organization:
    organization = Organization(
        public_id=public_id,
        name=name,
    )

    db.add(organization)
    db.flush()

    return organization

def update_organization(
    db: Session,
    *,
    organization: Organization,
    update_data: dict,
) -> Organization:
    """
    Обновляет профиль организации.

    update_data должен содержать только поля, которые разрешено менять.
    """
    for field_name, value in update_data.items():
        setattr(organization, field_name, value)

    db.flush()

    return organization
