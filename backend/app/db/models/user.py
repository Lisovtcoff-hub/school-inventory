from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.utils.datetime import utc_now
from app.db.base import Base


class User(Base):
    """
    Пользователь внутри организации.

    Роли приложения:
    - admin: администратор школы;
    - editor: может работать с техникой;
    - viewer: только просмотр.

    Пароль храним только как password_hash.
    Обычный пароль в базе хранить нельзя.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[str] = mapped_column(
        String(50),
        default="admin",
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    organization = relationship(
        "Organization",
        back_populates="users",
    )

    history_records = relationship(
        "AssetHistory",
        back_populates="user",
    )
