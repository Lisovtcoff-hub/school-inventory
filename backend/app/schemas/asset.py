from datetime import datetime

from pydantic import BaseModel, Field


class AssetBase(BaseModel):
    type: str = Field(min_length=2, max_length=100)
    name: str = Field(min_length=2, max_length=255)

    manufacturer: str | None = Field(default=None, max_length=255)
    model: str | None = Field(default=None, max_length=255)

    serial_number: str | None = Field(default=None, max_length=255)
    inventory_number: str | None = Field(default=None, max_length=255)

    commissioning_year: int | None = Field(default=None, ge=1990, le=2100)

    room: str | None = Field(default=None, max_length=100)
    responsible_person: str | None = Field(default=None, max_length=255)
    user_category: str | None = Field(default=None, max_length=100)

    status: str = Field(default="in_use", max_length=100)
    os: str | None = Field(default=None, max_length=255)

    description: str | None = None

    # Поля для отчётности ОО-2 и будущих отчётов.
    report_category: str | None = Field(default=None, max_length=100)
    is_used_for_education: bool = False
    is_available_for_students: bool = False
    has_lan: bool = False
    has_internet: bool = False
    has_intranet: bool = False
    received_in_current_year: bool = False
    ownership_type: str | None = Field(default=None, max_length=50)
    include_in_reports: bool = True


class AssetCreate(AssetBase):
    """
    Схема создания техники.

    organization_id, asset_code и local_number пользователь не отправляет.
    Backend генерирует их сам.
    """

    pass


class AssetUpdate(BaseModel):
    """
    Схема обновления техники.

    Все поля optional, чтобы можно было обновлять только часть карточки.
    """

    type: str | None = Field(default=None, min_length=2, max_length=100)
    name: str | None = Field(default=None, min_length=2, max_length=255)

    manufacturer: str | None = Field(default=None, max_length=255)
    model: str | None = Field(default=None, max_length=255)

    serial_number: str | None = Field(default=None, max_length=255)
    inventory_number: str | None = Field(default=None, max_length=255)

    commissioning_year: int | None = Field(default=None, ge=1990, le=2100)

    room: str | None = Field(default=None, max_length=100)
    responsible_person: str | None = Field(default=None, max_length=255)
    user_category: str | None = Field(default=None, max_length=100)

    status: str | None = Field(default=None, max_length=100)
    os: str | None = Field(default=None, max_length=255)

    description: str | None = None

    report_category: str | None = Field(default=None, max_length=100)
    is_used_for_education: bool | None = None
    is_available_for_students: bool | None = None
    has_lan: bool | None = None
    has_internet: bool | None = None
    has_intranet: bool | None = None
    received_in_current_year: bool | None = None
    ownership_type: str | None = Field(default=None, max_length=50)
    include_in_reports: bool | None = None


class AssetRead(BaseModel):
    id: int
    organization_id: int

    asset_code: str
    local_number: int

    type: str
    name: str

    manufacturer: str | None
    model: str | None

    serial_number: str | None
    inventory_number: str | None

    commissioning_year: int | None

    room: str | None
    responsible_person: str | None
    user_category: str | None

    status: str
    os: str | None
    description: str | None

    report_category: str | None
    is_used_for_education: bool
    is_available_for_students: bool
    has_lan: bool
    has_internet: bool
    has_intranet: bool
    received_in_current_year: bool
    ownership_type: str | None
    include_in_reports: bool

    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None

    model_config = {
        "from_attributes": True
    }


class AssetListResponse(BaseModel):
    items: list[AssetRead]
    total: int
    page: int
    page_size: int
    pages: int


class AssetStatsResponse(BaseModel):
    total: int
    by_status: dict[str, int]
    by_type: dict[str, int]
    by_report_category: dict[str, int]


class AssetDeleteResponse(BaseModel):
    message: str
    asset_id: int