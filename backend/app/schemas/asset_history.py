from datetime import datetime

from pydantic import BaseModel, Field


class AssetHistoryCreate(BaseModel):
    """
    Схема для ручного добавления события в историю техники.
    """

    event_type: str = Field(default="manual_note", min_length=2, max_length=100)
    message: str = Field(min_length=1)


class AssetHistoryRead(BaseModel):
    id: int
    organization_id: int
    asset_id: int
    user_id: int | None

    event_type: str
    field_name: str | None
    old_value: str | None
    new_value: str | None
    message: str

    created_at: datetime

    model_config = {
        "from_attributes": True
    }