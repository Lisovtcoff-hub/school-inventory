"""
Импорт всех моделей для Alembic.

Этот файл нужен только для того, чтобы Alembic видел все модели
при автогенерации миграций.

Важно:
не импортировать этот файл внутри app/db/base.py,
иначе будет circular import.
"""

from app.db.models.asset import Asset
from app.db.models.asset_history import AssetHistory
from app.db.models.license import LicenseCode
from app.db.models.organization import Organization
from app.db.models.user import User


__all__ = [
    "Organization",
    "User",
    "LicenseCode",
    "Asset",
    "AssetHistory",
]