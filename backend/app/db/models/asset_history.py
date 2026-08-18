from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.utils.datetime import utc_now
from app.db.base import Base


class AssetHistory(Base):
    """
    История изменений техники.

    Примеры событий:
    - техника создана;
    - изменён кабинет;
    - изменён статус;
    - изменён ответственный;
    - добавлена ручная заметка;
    - техника удалена из активного списка.
    """

    __tablename__ = "asset_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(String(100), nullable=False)

    field_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)

    message: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        nullable=False,
    )

    organization = relationship(
        "Organization",
        back_populates="history_records",
    )

    asset = relationship(
        "Asset",
        back_populates="history_records",
    )

    user = relationship(
        "User",
        back_populates="history_records",
    )
