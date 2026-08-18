from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.user import User


def get_user_by_id(db: Session, user_id: int) -> User | None:
    statement = select(User).where(User.id == user_id)
    return db.scalar(statement)


def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email.lower())
    return db.scalar(statement)


def create_user(
    db: Session,
    *,
    organization_id: int,
    email: str,
    password_hash: str,
    full_name: str,
    role: str,
) -> User:
    user = User(
        organization_id=organization_id,
        email=email.lower(),
        password_hash=password_hash,
        full_name=full_name,
        role=role,
    )

    db.add(user)
    db.flush()

    return user

def list_users_by_organization(
    db: Session,
    *,
    organization_id: int,
) -> list[User]:
    statement = (
        select(User)
        .where(User.organization_id == organization_id)
        .order_by(User.id.asc())
    )

    return list(db.scalars(statement).all())



def count_active_users_by_organization(
    db: Session,
    *,
    organization_id: int,
) -> int:
    statement = select(func.count(User.id)).where(
        User.organization_id == organization_id,
        User.is_active.is_(True),
    )
    return db.scalar(statement) or 0
