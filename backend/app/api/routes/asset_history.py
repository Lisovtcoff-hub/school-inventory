from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.asset_history import AssetHistoryCreate, AssetHistoryRead
from app.services.history_service import (
    create_manual_history_for_current_user,
    get_asset_history_for_current_user,
)


router = APIRouter(prefix="/assets", tags=["asset history"])


@router.get("/{asset_id}/history", response_model=list[AssetHistoryRead])
def get_asset_history(
    asset_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> list[AssetHistoryRead]:
    """
    Получить историю конкретной техники.
    """
    return get_asset_history_for_current_user(
        db,
        current_user=current_user,
        asset_id=asset_id,
    )


@router.post("/{asset_id}/history", response_model=AssetHistoryRead)
def create_asset_history_record(
    asset_id: int,
    data: AssetHistoryCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> AssetHistoryRead:
    """
    Добавить ручную запись в историю техники.
    """
    return create_manual_history_for_current_user(
        db,
        current_user=current_user,
        asset_id=asset_id,
        data=data,
    )