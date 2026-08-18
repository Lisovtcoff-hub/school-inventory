from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.constants import HISTORY_EVENT_MANUAL_NOTE
from app.db.models.asset_history import AssetHistory
from app.db.models.user import User
from app.repositories.asset_repository import get_asset_by_id
from app.repositories.history_repository import (
    create_history_record,
    list_history_for_asset,
)
from app.schemas.asset_history import AssetHistoryCreate


def get_asset_history_for_current_user(
    db: Session,
    *,
    current_user: User,
    asset_id: int,
) -> list[AssetHistory]:
    """
    Получить историю техники.

    Перед выдачей истории проверяем, что техника принадлежит организации пользователя.
    """
    asset = get_asset_by_id(
        db,
        organization_id=current_user.organization_id,
        asset_id=asset_id,
        include_deleted=True,
    )

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Техника не найдена",
        )

    return list_history_for_asset(
        db,
        organization_id=current_user.organization_id,
        asset_id=asset_id,
    )


def create_manual_history_for_current_user(
    db: Session,
    *,
    current_user: User,
    asset_id: int,
    data: AssetHistoryCreate,
) -> AssetHistory:
    """
    Ручное добавление события в историю.

    Например:
    "Проведена чистка от пыли"
    "Заменён кабель питания"
    "Проверено перед инвентаризацией"
    """
    asset = get_asset_by_id(
        db,
        organization_id=current_user.organization_id,
        asset_id=asset_id,
        include_deleted=True,
    )

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Техника не найдена",
        )

    history_record = create_history_record(
        db,
        organization_id=current_user.organization_id,
        asset_id=asset.id,
        user_id=current_user.id,
        event_type=data.event_type or HISTORY_EVENT_MANUAL_NOTE,
        message=data.message,
    )

    db.commit()
    db.refresh(history_record)

    return history_record