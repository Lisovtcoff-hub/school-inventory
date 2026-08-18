from datetime import datetime

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=6, max_length=128)
    full_name: str = Field(min_length=2, max_length=255)
    role: str = Field(default="viewer", min_length=2, max_length=50)


class UserRead(BaseModel):
    id: int
    organization_id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None

    model_config = {
        "from_attributes": True,
    }


class UserListResponse(BaseModel):
    items: list[UserRead]
    total: int
