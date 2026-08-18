from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import DbSession


router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health_check() -> dict[str, str]:
    """
    Простая проверка, что FastAPI-приложение запущено.

    Этот endpoint не проверяет базу.
    """
    return {
        "status": "ok",
        "service": "school-inventory-api",
    }


@router.get("/db")
def database_health_check(db: DbSession) -> dict[str, str]:
    """
    Проверка подключения к базе данных.

    Выполняет простой SQL-запрос SELECT 1.
    Если база недоступна, FastAPI вернёт ошибку.
    """
    db.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "connected",
    }