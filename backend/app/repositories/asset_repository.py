from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.utils.datetime import utc_now
from app.db.models.asset import Asset


def get_next_local_number(
    db: Session,
    organization_id: int,
) -> int:
    """
    Получает следующий локальный номер техники внутри организации.

    Если у организации ещё нет техники, вернёт 1.
    """
    statement = select(func.max(Asset.local_number)).where(
        Asset.organization_id == organization_id
    )

    max_number = db.scalar(statement)

    if max_number is None:
        return 1

    return max_number + 1


def create_asset(
    db: Session,
    *,
    organization_id: int,
    asset_code: str,
    local_number: int,
    type: str,
    name: str,
    manufacturer: str | None = None,
    model: str | None = None,
    serial_number: str | None = None,
    inventory_number: str | None = None,
    commissioning_year: int | None = None,
    room: str | None = None,
    responsible_person: str | None = None,
    user_category: str | None = None,
    status: str = "in_use",
    os: str | None = None,
    description: str | None = None,
    report_category: str | None = None,
    is_used_for_education: bool = False,
    is_available_for_students: bool = False,
    has_lan: bool = False,
    has_internet: bool = False,
    has_intranet: bool = False,
    received_in_current_year: bool = False,
    ownership_type: str | None = None,
    include_in_reports: bool = True,
) -> Asset:
    asset = Asset(
        organization_id=organization_id,
        asset_code=asset_code,
        local_number=local_number,
        type=type,
        name=name,
        manufacturer=manufacturer,
        model=model,
        serial_number=serial_number,
        inventory_number=inventory_number,
        commissioning_year=commissioning_year,
        room=room,
        responsible_person=responsible_person,
        user_category=user_category,
        status=status,
        os=os,
        description=description,
        report_category=report_category,
        is_used_for_education=is_used_for_education,
        is_available_for_students=is_available_for_students,
        has_lan=has_lan,
        has_internet=has_internet,
        has_intranet=has_intranet,
        received_in_current_year=received_in_current_year,
        ownership_type=ownership_type,
        include_in_reports=include_in_reports,
    )

    db.add(asset)
    db.flush()

    return asset


def get_asset_by_id(
    db: Session,
    *,
    organization_id: int,
    asset_id: int,
    include_deleted: bool = False,
) -> Asset | None:
    statement = select(Asset).where(
        Asset.id == asset_id,
        Asset.organization_id == organization_id,
    )

    if not include_deleted:
        statement = statement.where(Asset.deleted_at.is_(None))

    return db.scalar(statement)


def get_asset_by_code(
    db: Session,
    *,
    organization_id: int,
    asset_code: str,
    include_deleted: bool = False,
) -> Asset | None:
    statement = select(Asset).where(
        Asset.asset_code == asset_code,
        Asset.organization_id == organization_id,
    )

    if not include_deleted:
        statement = statement.where(Asset.deleted_at.is_(None))

    return db.scalar(statement)


def list_assets(
    db: Session,
    *,
    organization_id: int,
    search: str | None = None,
    type: str | None = None,
    status: str | None = None,
    room: str | None = None,
    responsible_person: str | None = None,
    user_category: str | None = None,
    os: str | None = None,
    commissioning_year: int | None = None,
    page: int = 1,
    page_size: int = 50,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> tuple[list[Asset], int]:
    """
    Возвращает список техники и общее количество записей.

    Важно:
    всегда фильтруем по organization_id.
    Пользователь не должен видеть технику другой школы.
    """
    base_conditions = [
        Asset.organization_id == organization_id,
        Asset.deleted_at.is_(None),
    ]

    if search:
        search_pattern = f"%{search.strip()}%"

        base_conditions.append(
            or_(
                Asset.asset_code.ilike(search_pattern),
                Asset.name.ilike(search_pattern),
                Asset.manufacturer.ilike(search_pattern),
                Asset.model.ilike(search_pattern),
                Asset.serial_number.ilike(search_pattern),
                Asset.inventory_number.ilike(search_pattern),
                Asset.room.ilike(search_pattern),
                Asset.responsible_person.ilike(search_pattern),
                Asset.os.ilike(search_pattern),
            )
        )

    if type:
        base_conditions.append(Asset.type == type)

    if status:
        base_conditions.append(Asset.status == status)

    if room:
        base_conditions.append(Asset.room == room)

    if responsible_person:
        base_conditions.append(Asset.responsible_person.ilike(f"%{responsible_person}%"))

    if user_category:
        base_conditions.append(Asset.user_category == user_category)

    if os:
        base_conditions.append(Asset.os.ilike(f"%{os}%"))

    if commissioning_year:
        base_conditions.append(Asset.commissioning_year == commissioning_year)

    count_statement = select(func.count(Asset.id)).where(*base_conditions)
    total = db.scalar(count_statement) or 0

    allowed_sort_fields = {
        "id": Asset.id,
        "asset_code": Asset.asset_code,
        "name": Asset.name,
        "type": Asset.type,
        "status": Asset.status,
        "room": Asset.room,
        "responsible_person": Asset.responsible_person,
        "created_at": Asset.created_at,
        "updated_at": Asset.updated_at,
        "commissioning_year": Asset.commissioning_year,
    }

    sort_column = allowed_sort_fields.get(sort_by, Asset.created_at)

    if sort_order == "asc":
        order_expression = sort_column.asc()
    else:
        order_expression = sort_column.desc()

    offset = (page - 1) * page_size

    statement = (
        select(Asset)
        .where(*base_conditions)
        .order_by(order_expression)
        .offset(offset)
        .limit(page_size)
    )

    assets = list(db.scalars(statement).all())

    return assets, total


def update_asset(
    db: Session,
    asset: Asset,
    update_data: dict,
) -> Asset:
    """
    Обновляет поля техники.

    update_data должен содержать только те поля, которые реально надо изменить.
    """
    for field_name, value in update_data.items():
        setattr(asset, field_name, value)

    db.flush()

    return asset


def soft_delete_asset(
    db: Session,
    asset: Asset,
) -> Asset:
    """
    Мягкое удаление техники.

    Физически запись из базы не удаляется.
    """
    asset.deleted_at = utc_now()

    db.flush()

    return asset

def get_assets_by_ids(
    db: Session,
    *,
    organization_id: int,
    asset_ids: list[int],
    include_deleted: bool = False,
) -> list[Asset]:
    """
    Возвращает список техники по списку ID.

    Важно:
    фильтруем по organization_id, чтобы пользователь не мог получить
    QR-коды чужой организации.
    """
    statement = select(Asset).where(
        Asset.organization_id == organization_id,
        Asset.id.in_(asset_ids),
    )

    if not include_deleted:
        statement = statement.where(Asset.deleted_at.is_(None))

    statement = statement.order_by(Asset.id.asc())

    return list(db.scalars(statement).all())


def count_assets_by_organization(
    db: Session,
    *,
    organization_id: int,
) -> int:
    statement = select(func.count(Asset.id)).where(
        Asset.organization_id == organization_id,
        Asset.deleted_at.is_(None),
    )
    return db.scalar(statement) or 0


def get_asset_stats(
    db: Session,
    *,
    organization_id: int,
) -> dict[str, object]:
    base_conditions = (
        Asset.organization_id == organization_id,
        Asset.deleted_at.is_(None),
    )

    total = db.scalar(select(func.count(Asset.id)).where(*base_conditions)) or 0

    by_status_rows = db.execute(
        select(Asset.status, func.count(Asset.id))
        .where(*base_conditions)
        .group_by(Asset.status)
    ).all()

    by_type_rows = db.execute(
        select(Asset.type, func.count(Asset.id))
        .where(*base_conditions)
        .group_by(Asset.type)
    ).all()

    by_report_category_rows = db.execute(
        select(Asset.report_category, func.count(Asset.id))
        .where(*base_conditions)
        .where(Asset.report_category.is_not(None))
        .group_by(Asset.report_category)
    ).all()

    return {
        "total": total,
        "by_status": {str(key): int(value) for key, value in by_status_rows if key is not None},
        "by_type": {str(key): int(value) for key, value in by_type_rows if key is not None},
        "by_report_category": {
            str(key): int(value)
            for key, value in by_report_category_rows
            if key is not None
        },
    }



def list_asset_rooms_by_organization(
    db: Session,
    *,
    organization_id: int,
) -> list[str]:
    """Возвращает уникальные непустые кабинеты/локации техники организации."""
    trimmed_room = func.trim(Asset.room)
    statement = (
        select(trimmed_room)
        .where(
            Asset.organization_id == organization_id,
            Asset.deleted_at.is_(None),
            Asset.room.is_not(None),
            trimmed_room != "",
        )
        .distinct()
        .order_by(trimmed_room.asc())
    )

    return [str(room) for room in db.scalars(statement).all() if room]


def list_assets_by_room(
    db: Session,
    *,
    organization_id: int,
    room: str,
) -> list[Asset]:
    """Возвращает всю активную технику выбранного кабинета организации."""
    statement = (
        select(Asset)
        .where(
            Asset.organization_id == organization_id,
            Asset.deleted_at.is_(None),
            Asset.room.is_not(None),
            func.trim(Asset.room) == room.strip(),
        )
        .order_by(Asset.type.asc(), Asset.name.asc(), Asset.local_number.asc())
    )

    return list(db.scalars(statement).all())
