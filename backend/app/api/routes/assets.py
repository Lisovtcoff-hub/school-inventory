from fastapi import APIRouter, Query

from app.api.deps import CurrentUser, DbSession
from app.schemas.asset import (
    AssetCreate,
    AssetDeleteResponse,
    AssetListResponse,
    AssetRead,
    AssetStatsResponse,
    AssetUpdate,
)
from app.services.asset_service import (
    create_asset_for_current_user,
    get_asset_by_code_for_current_user,
    get_asset_for_current_user,
    get_assets_for_current_user,
    get_asset_stats_for_current_user,
    soft_delete_asset_for_current_user,
    update_asset_for_current_user,
)


router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("", response_model=AssetRead)
def create_asset(
    data: AssetCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> AssetRead:
    """
    Создать новую единицу техники.

    Backend сам:
    - берёт organization_id из текущего пользователя;
    - генерирует local_number;
    - генерирует asset_code.
    """
    return create_asset_for_current_user(
        db,
        current_user=current_user,
        data=data,
    )


@router.get("", response_model=AssetListResponse)
def get_assets(
    db: DbSession,
    current_user: CurrentUser,
    search: str | None = Query(default=None),
    type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    room: str | None = Query(default=None),
    responsible_person: str | None = Query(default=None),
    user_category: str | None = Query(default=None),
    os: str | None = Query(default=None),
    commissioning_year: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc", pattern="^(asc|desc)$"),
) -> AssetListResponse:
    """
    Получить список техники текущей организации.

    Поддерживает:
    - поиск;
    - фильтры;
    - пагинацию;
    - сортировку.
    """
    return get_assets_for_current_user(
        db,
        current_user=current_user,
        search=search,
        type=type,
        status=status,
        room=room,
        responsible_person=responsible_person,
        user_category=user_category,
        os=os,
        commissioning_year=commissioning_year,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/stats", response_model=AssetStatsResponse)
def get_asset_stats(
    db: DbSession,
    current_user: CurrentUser,
) -> AssetStatsResponse:
    """
    Получить статистику по всей активной технике текущей организации.

    В отличие от списка /assets, этот endpoint не зависит от пагинации
    и подходит для dashboard.
    """
    return get_asset_stats_for_current_user(
        db,
        current_user=current_user,
    )


@router.get("/by-code/{asset_code}", response_model=AssetRead)
def get_asset_by_code(
    asset_code: str,
    db: DbSession,
    current_user: CurrentUser,
) -> AssetRead:
    """
    Получить карточку техники по 16-значному коду.

    Этот endpoint понадобится для QR-сканера.
    """
    return get_asset_by_code_for_current_user(
        db,
        current_user=current_user,
        asset_code=asset_code,
    )


@router.get("/{asset_id}", response_model=AssetRead)
def get_asset(
    asset_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> AssetRead:
    """
    Получить карточку техники по id.
    """
    return get_asset_for_current_user(
        db,
        current_user=current_user,
        asset_id=asset_id,
    )


@router.put("/{asset_id}", response_model=AssetRead)
def update_asset(
    asset_id: int,
    data: AssetUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> AssetRead:
    """
    Обновить карточку техники.
    """
    return update_asset_for_current_user(
        db,
        current_user=current_user,
        asset_id=asset_id,
        data=data,
    )


@router.delete("/{asset_id}", response_model=AssetDeleteResponse)
def delete_asset(
    asset_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> AssetDeleteResponse:
    """
    Мягко удалить технику.

    Запись остаётся в базе, но получает deleted_at.
    В обычном списке такая техника больше не показывается.
    """
    deleted_asset = soft_delete_asset_for_current_user(
        db,
        current_user=current_user,
        asset_id=asset_id,
    )

    return AssetDeleteResponse(
        message="Техника удалена из активного списка",
        asset_id=deleted_asset.id,
    )