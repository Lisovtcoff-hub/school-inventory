from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.asset_history import AssetHistory


def create_history_record(
    db: Session,
    *,
    organization_id: int,
    asset_id: int,
    user_id: int | None,
    event_type: str,
    message: str,
    field_name: str | None = None,
    old_value: str | None = None,
    new_value: str | None = None,
) -> AssetHistory:
    """
    Создаёт запись истории техники.

    commit здесь не делаем специально.
    commit должен быть в service-слое, чтобы можно было сохранить
    технику и историю одной транзакцией.
    """
    history_record = AssetHistory(
        organization_id=organization_id,
        asset_id=asset_id,
        user_id=user_id,
        event_type=event_type,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value,
        message=message,
    )

    db.add(history_record)
    db.flush()

    return history_record


def list_history_for_asset(
    db: Session,
    *,
    organization_id: int,
    asset_id: int,
) -> list[AssetHistory]:
    """
    Возвращает историю конкретной техники.
    """
    statement = (
        select(AssetHistory)
        .where(
            AssetHistory.organization_id == organization_id,
            AssetHistory.asset_id == asset_id,
        )
        .order_by(AssetHistory.created_at.desc())
    )

    return list(db.scalars(statement).all())