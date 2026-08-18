from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import settings


_FIELD_LABELS = {
    "email": "Email",
    "admin_email": "Email администратора",
    "password": "Пароль",
    "admin_password": "Пароль администратора",
    "full_name": "ФИО",
    "admin_full_name": "ФИО администратора",
    "license_code": "Лицензионный код",
    "organization_name": "Название организации",
    "name": "Название",
    "type": "Тип техники",
    "manufacturer": "Производитель",
    "model": "Модель",
    "serial_number": "Серийный номер",
    "inventory_number": "Инвентарный номер",
    "commissioning_year": "Год ввода",
    "room": "Кабинет/локация",
    "location": "Кабинет/локация",
    "responsible_person": "Ответственный",
    "status": "Статус",
    "os": "Операционная система",
    "description": "Описание",
    "report_category": "Категория для отчёта",
    "ownership_type": "Тип владения",
    "asset_ids": "Выбранная техника",
    "label_width_cm": "Ширина наклейки",
    "label_height_cm": "Высота наклейки",
    "qr_size_cm": "Размер QR-кода",
    "columns": "Количество колонок",
    "message": "Сообщение",
    "event_type": "Тип события",
    "role": "Роль",
    "inn": "ИНН",
    "kpp": "КПП",
    "ogrn": "ОГРН",
    "address": "Адрес",
    "director_name": "Директор",
    "phone": "Телефон",
}


def _field_label(loc: tuple | list | None) -> str:
    if not loc:
        return "данные"
    for part in reversed(loc):
        value = str(part)
        if value not in {"body", "query", "path"}:
            return _FIELD_LABELS.get(value, value.replace("_", " "))
    return "данные"


def _validation_error_to_text(error: dict) -> str:
    error_type = str(error.get("type") or "")
    ctx = error.get("ctx") or {}
    msg = str(error.get("msg") or "")
    field = _field_label(error.get("loc"))

    if error_type == "missing":
        return f"Заполните поле «{field}»."

    field_type = str(ctx.get("field_type") or "").lower()
    is_list_length_error = (
        "list_too_short" in error_type
        or "list_too_long" in error_type
        or (error_type in {"too_short", "too_long"} and field_type == "list")
    )
    if is_list_length_error:
        min_length = ctx.get("min_length") or ctx.get("limit_value")
        if min_length is not None:
            return f"Выберите минимум {min_length} элемент."
        return "Выберите хотя бы один элемент."

    if "string_too_short" in error_type or error_type == "too_short":
        min_length = ctx.get("min_length") or ctx.get("limit_value")
        if min_length is not None:
            return f"Поле «{field}» должно быть не короче {min_length} символов."
        return f"Поле «{field}» заполнено слишком коротко."

    if "string_too_long" in error_type or error_type == "too_long":
        max_length = ctx.get("max_length") or ctx.get("limit_value")
        if max_length is not None:
            return f"Поле «{field}» должно быть не длиннее {max_length} символов."
        return f"Поле «{field}» заполнено слишком длинно."

    if "greater_than_equal" in error_type:
        value = ctx.get("ge") or ctx.get("limit_value")
        if value is not None:
            return f"Поле «{field}» должно быть не меньше {value}."

    if "less_than_equal" in error_type:
        value = ctx.get("le") or ctx.get("limit_value")
        if value is not None:
            return f"Поле «{field}» должно быть не больше {value}."

    if "int_parsing" in error_type or "float_parsing" in error_type:
        return f"Поле «{field}» должно быть числом."

    if "bool_parsing" in error_type:
        return f"Поле «{field}» должно быть выбрано корректно."

    if error_type.startswith("value_error") and msg:
        return msg.removeprefix("Value error, ")

    return f"Проверьте поле «{field}»."


def _validation_errors_to_message(errors: list[dict]) -> str:
    messages: list[str] = []
    for error in errors:
        message = _validation_error_to_text(error)
        if message not in messages:
            messages.append(message)
    if not messages:
        return "Проверьте корректность заполнения формы."
    return "\n".join(messages[:4])


def create_app() -> FastAPI:
    """
    Фабрика приложения.

    Почему через функцию:
    - удобнее тестировать;
    - удобнее расширять;
    - можно создавать приложение с разными настройками.
    """

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="Asset management API for educational organizations.",
    )

    if settings.cors_origins_list:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins_list,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """
        Возвращает совместимый FastAPI detail + человекочитаемое message.

        detail оставляем для разработчиков и обратной совместимости, а frontend
        показывает message, чтобы пользователь не видел сырой Pydantic JSON.
        """

        errors = exc.errors()
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "message": _validation_errors_to_message(errors),
                "detail": errors,
            },
        )

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/health", tags=["health"])
    def root_health_check() -> dict[str, str]:
        """Совместимый health-check без API-префикса."""
        return {
            "status": "ok",
            "service": "school-inventory-api",
        }

    return app


app = create_app()
