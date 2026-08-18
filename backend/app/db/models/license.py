from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.utils.datetime import utc_now
from app.db.base import Base


class LicenseCode(Base):
    """
    Лицензионный код для активации школы.

    Для локальной разработки код создаётся вручную или через служебный скрипт.
    Потом школа вводит этот код при первом запуске.
    """

    __tablename__ = "license_codes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=True,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="new",
        nullable=False,
    )

    max_users: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_assets: Mapped[int | None] = mapped_column(Integer, nullable=True)

    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        nullable=False,
    )

    organization = relationship(
        "Organization",
        back_populates="license_codes",
    )
