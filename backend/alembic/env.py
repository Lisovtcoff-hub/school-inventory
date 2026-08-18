from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.db.base import Base
import app.db.base_model_imports  # noqa: F401

# Alembic Config object.
config = context.config

# Подключаем логирование из alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Передаём Alembic URL базы из наших настроек.
# То есть Alembic будет брать DATABASE_URL из .env.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Metadata всех моделей.
# Именно по ней Alembic понимает, какие таблицы надо создать.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Offline-режим.

    Alembic генерирует SQL без подключения к базе.
    Используется для генерации SQL без подключения к базе.
    """
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Online-режим.

    Alembic подключается к базе и применяет миграции.
    Это основной режим для нас.
    """
    configuration = config.get_section(config.config_ini_section)

    if configuration is None:
        raise RuntimeError("Alembic configuration section not found")

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()