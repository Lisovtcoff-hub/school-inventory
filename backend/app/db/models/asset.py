from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.utils.datetime import utc_now
from app.db.base import Base


class Asset(Base):
    """
    Единица техники.

    Например:
    - ноутбук;
    - компьютер;
    - монитор;
    - принтер;
    - проектор;
    - интерактивная доска.

    asset_code — 16-значный код техники.
    local_number — номер техники внутри конкретной организации.
    """

    __tablename__ = "assets"
    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "local_number",
            name="uq_assets_organization_id_local_number",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    asset_code: Mapped[str] = mapped_column(
        String(16),
        unique=True,
        index=True,
        nullable=False,
    )

    local_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    type: Mapped[str] = mapped_column(String(100), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    manufacturer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    model: Mapped[str | None] = mapped_column(String(255), nullable=True)

    serial_number: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    inventory_number: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    commissioning_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    room: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    responsible_person: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    user_category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    status: Mapped[str] = mapped_column(
        String(100),
        default="in_use",
        nullable=False,
        index=True,
    )

    os: Mapped[str | None] = mapped_column(String(255), nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Поля для отчётности. Они не ломают обычный учёт техники,
    # но позволяют считать ОО-2 и будущие статистические отчёты.
    report_category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    is_used_for_education: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_available_for_students: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    has_lan: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_internet: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    has_intranet: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    received_in_current_year: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    ownership_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    include_in_reports: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

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

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    organization = relationship(
        "Organization",
        back_populates="assets",
    )

    history_records = relationship(
        "AssetHistory",
        back_populates="asset",
        cascade="all, delete-orphan",
    )
