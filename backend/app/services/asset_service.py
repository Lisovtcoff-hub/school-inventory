from math import ceil

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.constants import (
    ALLOWED_ASSET_STATUSES,
    ALLOWED_ASSET_TYPES,
    ALLOWED_OWNERSHIP_TYPES,
    ALLOWED_REPORT_CATEGORIES,
    ALLOWED_USER_CATEGORIES,
    HISTORY_EVENT_CREATED,
    HISTORY_EVENT_DELETED,
    TRACKED_ASSET_HISTORY_FIELDS,
    USER_ROLE_ADMIN,
    USER_ROLE_EDITOR,
)
from app.db.models.asset import Asset
from app.db.models.user import User
from app.repositories.asset_repository import (
    count_assets_by_organization,
    create_asset,
    get_asset_by_code,
    get_asset_by_id,
    get_next_local_number,
    get_asset_stats,
    list_assets,
    soft_delete_asset,
    update_asset,
)
from app.repositories.history_repository import create_history_record
from app.repositories.organization_repository import get_organization_by_id
from app.services.license_service import ensure_license_allows_write
from app.schemas.asset import AssetCreate, AssetListResponse, AssetStatsResponse, AssetUpdate


def _ensure_can_modify_assets(user: User) -> None:
    """
    admin и editor могут создавать/редактировать/удалять.
    viewer — только смотреть.
    """
    if user.role not in {USER_ROLE_ADMIN, USER_ROLE_EDITOR}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для изменения техники",
        )


def _validate_asset_type(asset_type: str) -> None:
    if asset_type not in ALLOWED_ASSET_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый тип техники: {asset_type}",
        )


def _validate_asset_status(asset_status: str) -> None:
    if asset_status not in ALLOWED_ASSET_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый статус техники: {asset_status}",
        )


def _validate_user_category(user_category: str | None) -> None:
    if user_category is None:
        return

    if user_category not in ALLOWED_USER_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимая категория пользователя техники: {user_category}",
        )




def _validate_report_category(report_category: str | None) -> None:
    if report_category is None:
        return

    if report_category not in ALLOWED_REPORT_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимая категория для отчётов: {report_category}",
        )


def _validate_ownership_type(ownership_type: str | None) -> None:
    if ownership_type is None:
        return

    if ownership_type not in ALLOWED_OWNERSHIP_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый тип владения техникой: {ownership_type}",
        )

def _build_asset_code(
    *,
    organization_public_id: str,
    local_number: int,
) -> str:
    """
    Генерирует 16-значный код техники.
    """
    return f"{organization_public_id}{local_number:08d}"


def _value_to_str(value: object) -> str | None:
    """
    Приводит значение к строке для хранения в истории.

    В asset_history поля old_value и new_value текстовые,
    поэтому int/None/строки приводим к единому формату.
    """
    if value is None:
        return None

    return str(value)


def _build_change_message(
    *,
    field_name: str,
    old_value: object,
    new_value: object,
) -> str:
    """
    Создаёт человекочитаемое сообщение для истории.
    """
    field_titles = {
        "status": "Состояние",
        "room": "Кабинет",
        "responsible_person": "Ответственный",
        "user_category": "Категория пользователя",
        "os": "ОС",
        "description": "Описание",
    }

    title = field_titles.get(field_name, field_name)

    return (
        f'{title} изменено с "{_value_to_str(old_value)}" '
        f'на "{_value_to_str(new_value)}"'
    )


def _ensure_license_allows_asset_creation(db: Session, *, organization_id: int) -> None:
    license_code = ensure_license_allows_write(
        db,
        organization_id=organization_id,
    )

    if license_code is None or license_code.max_assets is None:
        return

    current_assets_count = count_assets_by_organization(
        db,
        organization_id=organization_id,
    )

    if current_assets_count >= license_code.max_assets:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Превышен лимит техники по лицензии",
        )


def create_asset_for_current_user(
    db: Session,
    *,
    current_user: User,
    data: AssetCreate,
) -> Asset:
    _ensure_can_modify_assets(current_user)
    _ensure_license_allows_asset_creation(
        db,
        organization_id=current_user.organization_id,
    )

    _validate_asset_type(data.type)
    _validate_asset_status(data.status)
    _validate_user_category(data.user_category)
    _validate_report_category(data.report_category)
    _validate_ownership_type(data.ownership_type)

    organization = get_organization_by_id(
        db,
        current_user.organization_id,
    )

    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Организация не найдена",
        )

    last_integrity_error: IntegrityError | None = None

    for _ in range(3):
        local_number = get_next_local_number(
            db,
            organization_id=current_user.organization_id,
        )

        asset_code = _build_asset_code(
            organization_public_id=organization.public_id,
            local_number=local_number,
        )

        try:
            asset = create_asset(
                db,
                organization_id=current_user.organization_id,
                asset_code=asset_code,
                local_number=local_number,
                type=data.type,
                name=data.name,
                manufacturer=data.manufacturer,
                model=data.model,
                serial_number=data.serial_number,
                inventory_number=data.inventory_number,
                commissioning_year=data.commissioning_year,
                room=data.room,
                responsible_person=data.responsible_person,
                user_category=data.user_category,
                status=data.status,
                os=data.os,
                description=data.description,
                report_category=data.report_category,
                is_used_for_education=data.is_used_for_education,
                is_available_for_students=data.is_available_for_students,
                has_lan=data.has_lan,
                has_internet=data.has_internet,
                has_intranet=data.has_intranet,
                received_in_current_year=data.received_in_current_year,
                ownership_type=data.ownership_type,
                include_in_reports=data.include_in_reports,
            )

            create_history_record(
                db,
                organization_id=current_user.organization_id,
                asset_id=asset.id,
                user_id=current_user.id,
                event_type=HISTORY_EVENT_CREATED,
                message=f'Техника "{asset.name}" добавлена в систему',
            )

            db.commit()
            db.refresh(asset)

            return asset

        except IntegrityError as exc:
            db.rollback()
            last_integrity_error = exc

    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=(
            "Конфликт локального номера техники при одновременном создании. "
            "Повторите сохранение."
        ),
    ) from last_integrity_error


def get_assets_for_current_user(
    db: Session,
    *,
    current_user: User,
    search: str | None,
    type: str | None,
    status: str | None,
    room: str | None,
    responsible_person: str | None,
    user_category: str | None,
    os: str | None,
    commissioning_year: int | None,
    page: int,
    page_size: int,
    sort_by: str,
    sort_order: str,
) -> AssetListResponse:
    if type is not None:
        _validate_asset_type(type)

    if status is not None:
        _validate_asset_status(status)

    if user_category is not None:
        _validate_user_category(user_category)

    assets, total = list_assets(
        db,
        organization_id=current_user.organization_id,
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

    pages = ceil(total / page_size) if total else 0

    return AssetListResponse(
        items=assets,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


def get_asset_stats_for_current_user(
    db: Session,
    *,
    current_user: User,
) -> AssetStatsResponse:
    stats = get_asset_stats(
        db,
        organization_id=current_user.organization_id,
    )

    return AssetStatsResponse(
        total=int(stats["total"]),
        by_status=dict(stats["by_status"]),
        by_type=dict(stats["by_type"]),
        by_report_category=dict(stats["by_report_category"]),
    )


def get_asset_for_current_user(
    db: Session,
    *,
    current_user: User,
    asset_id: int,
) -> Asset:
    asset = get_asset_by_id(
        db,
        organization_id=current_user.organization_id,
        asset_id=asset_id,
    )

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Техника не найдена",
        )

    return asset


def get_asset_by_code_for_current_user(
    db: Session,
    *,
    current_user: User,
    asset_code: str,
) -> Asset:
    asset = get_asset_by_code(
        db,
        organization_id=current_user.organization_id,
        asset_code=asset_code,
    )

    if asset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Техника не найдена",
        )

    return asset


def update_asset_for_current_user(
    db: Session,
    *,
    current_user: User,
    asset_id: int,
    data: AssetUpdate,
) -> Asset:
    _ensure_can_modify_assets(current_user)

    asset = get_asset_for_current_user(
        db,
        current_user=current_user,
        asset_id=asset_id,
    )

    update_data = data.model_dump(exclude_unset=True)

    if "type" in update_data and update_data["type"] is not None:
        _validate_asset_type(update_data["type"])

    if "status" in update_data and update_data["status"] is not None:
        _validate_asset_status(update_data["status"])

    if "user_category" in update_data:
        _validate_user_category(update_data["user_category"])

    if "report_category" in update_data:
        _validate_report_category(update_data["report_category"])

    if "ownership_type" in update_data:
        _validate_ownership_type(update_data["ownership_type"])

    if not update_data:
        return asset

    changes_for_history: list[dict[str, object]] = []

    for field_name, event_type in TRACKED_ASSET_HISTORY_FIELDS.items():
        if field_name not in update_data:
            continue

        old_value = getattr(asset, field_name)
        new_value = update_data[field_name]

        if old_value == new_value:
            continue

        changes_for_history.append(
            {
                "field_name": field_name,
                "event_type": event_type,
                "old_value": old_value,
                "new_value": new_value,
                "message": _build_change_message(
                    field_name=field_name,
                    old_value=old_value,
                    new_value=new_value,
                ),
            }
        )

    try:
        updated_asset = update_asset(
            db,
            asset=asset,
            update_data=update_data,
        )

        for change in changes_for_history:
            create_history_record(
                db,
                organization_id=current_user.organization_id,
                asset_id=asset.id,
                user_id=current_user.id,
                event_type=str(change["event_type"]),
                field_name=str(change["field_name"]),
                old_value=_value_to_str(change["old_value"]),
                new_value=_value_to_str(change["new_value"]),
                message=str(change["message"]),
            )

        db.commit()
        db.refresh(updated_asset)

        return updated_asset

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Конфликт данных при обновлении техники",
        )


def soft_delete_asset_for_current_user(
    db: Session,
    *,
    current_user: User,
    asset_id: int,
) -> Asset:
    _ensure_can_modify_assets(current_user)

    asset = get_asset_for_current_user(
        db,
        current_user=current_user,
        asset_id=asset_id,
    )

    deleted_asset = soft_delete_asset(db, asset)

    create_history_record(
        db,
        organization_id=current_user.organization_id,
        asset_id=asset.id,
        user_id=current_user.id,
        event_type=HISTORY_EVENT_DELETED,
        message=f'Техника "{asset.name}" удалена из активного списка',
    )

    db.commit()
    db.refresh(deleted_asset)

    return deleted_asset