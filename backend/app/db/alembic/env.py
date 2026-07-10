"""
Alembic environment configuration.

- Reads DATABASE_URL from the app's Settings (via pydantic-settings / .env).
- Imports all models through app.models so their tables are registered on
  Base.metadata and Alembic can auto-generate migrations with --autogenerate.
- Supports both offline (SQL script) and online (direct DB) migration modes.
"""
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Ensure the backend/ directory is on the path so `app.*` imports resolve
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

from app.config import get_settings

# Import models so Alembic picks up their table definitions
import app.models  # noqa: F401 — registers all models on Base.metadata
from app.core.database import Base

# --------------------------------------------------------------------------
# Alembic config object, providing access to values in alembic.ini
# --------------------------------------------------------------------------
config = context.config

# Override sqlalchemy.url from env (never hardcode credentials in alembic.ini)
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging if present
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# --------------------------------------------------------------------------
# Offline mode: emit SQL script without a live DB connection
# --------------------------------------------------------------------------
def run_migrations_offline() -> None:
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


# --------------------------------------------------------------------------
# Online mode: apply migrations against the live Neon database
# --------------------------------------------------------------------------
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # NullPool avoids idle connection issues with Neon
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
