"""
Alembic environment configuration.

- Uses async SQLAlchemy engine (asyncpg) for online migrations.
- Reads DATABASE_URL from app.config.Settings (env var / .env file).
- All feature models must be imported here so Alembic can detect schema changes.
- All PostgreSQL schemas are created before any table DDL.
"""
import asyncio
import logging
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool, text
from sqlalchemy.ext.asyncio import async_engine_from_config

# ── App imports ───────────────────────────────────────────────────────────────
from app.config import get_settings
from app.database import Base

# Feature model imports — must be here for autogenerate to detect all tables.
# Phase 2 (active):
from app.features.core import models as core_models          # noqa: F401
from app.features.core import geo_models as core_geo_models  # noqa: F401
# Phase 3:
# from app.features.auth import models as auth_models          # noqa: F401
# Phase 4:
# from app.features.academic import models as academic_models  # noqa: F401
# from app.features.academic import guardian_models            # noqa: F401
# from app.features.academic import enrollment_models          # noqa: F401
# Phase 5:
# from app.features.exam import models as exam_models          # noqa: F401

logger = logging.getLogger("alembic.env")

# ── Alembic Config ────────────────────────────────────────────────────────────
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override sqlalchemy.url from settings
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata

# PostgreSQL schemas managed by this project
_MANAGED_SCHEMAS = ["core", "auth", "academic", "exam"]


# ── Schema creation helper ────────────────────────────────────────────────────

def _create_schemas(connection) -> None:
    for schema in _MANAGED_SCHEMAS:
        connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))


# ── Offline migration ─────────────────────────────────────────────────────────

def run_migrations_offline() -> None:
    """Emit SQL to stdout — no live DB connection needed."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online migration ──────────────────────────────────────────────────────────

def do_run_migrations(connection) -> None:
    _create_schemas(connection)
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,
        version_table_schema="public",
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    from sqlalchemy.ext.asyncio import create_async_engine

    # Use settings URL directly — avoids the alembic.ini placeholder being picked up
    connectable = create_async_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
        await connection.commit()  # ← required: asyncpg never auto-commits DDL
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


# ── Entry point ───────────────────────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
