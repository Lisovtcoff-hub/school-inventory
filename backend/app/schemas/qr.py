from pydantic import BaseModel, Field, model_validator


class QRLabelsPdfRequest(BaseModel):
    """
    Запрос на генерацию PDF-листа с QR-кодами.

    asset_ids:
    ID техники, которую пользователь выбрал галочками.

    label_width_cm / label_height_cm:
    физический размер одной наклейки на листе.
    Например, 5 x 5 см.

    qr_size_cm:
    физический размер самого QR-кода внутри наклейки.

    columns:
    сколько наклеек размещать в одной строке.
    Если не передать, backend рассчитает количество колонок автоматически.
    """

    asset_ids: list[int] = Field(min_length=1, max_length=200)

    label_width_cm: float = Field(default=5.0, ge=2.0, le=12.0)
    label_height_cm: float = Field(default=5.5, ge=2.0, le=12.0)
    qr_size_cm: float = Field(default=3.0, ge=1.5, le=8.0)

    columns: int | None = Field(default=None, ge=1, le=5)

    include_asset_code: bool = True
    include_asset_name: bool = True
    include_room: bool = True

    @model_validator(mode="after")
    def validate_sizes(self):
        if self.qr_size_cm > self.label_width_cm:
            raise ValueError("QR-код не может быть шире наклейки")

        if self.qr_size_cm > self.label_height_cm:
            raise ValueError("QR-код не может быть выше наклейки")

        return self
