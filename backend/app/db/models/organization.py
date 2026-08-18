from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.utils.datetime import utc_now
from app.db.base import Base


class Organization(Base):
    """
    Образовательная организация.

    В нашем случае это школа, лицей, колледж и т.д.

    public_id — публичный 8-значный код организации.
    Он нужен для генерации кодов техники:

    12345678 + 00000001 = 1234567800000001
    """

    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    public_id: Mapped[str] = mapped_column(
        String(8),
        unique=True,
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    inn: Mapped[str | None] = mapped_column(String(20), nullable=True)
    kpp: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ogrn: Mapped[str | None] = mapped_column(String(30), nullable=True)

    address: Mapped[str | None] = mapped_column(String(500), nullable=True)

    director_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    responsible_person: Mapped[str | None] = mapped_column(String(255), nullable=True)

    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)

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

    users = relationship(
        "User",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    assets = relationship(
        "Asset",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    license_codes = relationship(
        "LicenseCode",
        back_populates="organization",
    )

    history_records = relationship(
        "AssetHistory",
        back_populates="organization",
    )
