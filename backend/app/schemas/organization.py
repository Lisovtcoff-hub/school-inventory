from datetime import datetime

from pydantic import BaseModel, Field


class OrganizationRead(BaseModel):
    id: int
    public_id: str
    name: str

    inn: str | None
    kpp: str | None
    ogrn: str | None
    address: str | None

    director_name: str | None
    responsible_person: str | None

    email: str | None
    phone: str | None

    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class OrganizationUpdate(BaseModel):
    """
    Обновление профиля текущей организации.

    public_id и is_active пользователь через этот endpoint не меняет.
    """

    name: str | None = Field(default=None, min_length=2, max_length=255)

    inn: str | None = Field(default=None, max_length=20)
    kpp: str | None = Field(default=None, max_length=20)
    ogrn: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=500)

    director_name: str | None = Field(default=None, max_length=255)
    responsible_person: str | None = Field(default=None, max_length=255)

    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=50)
