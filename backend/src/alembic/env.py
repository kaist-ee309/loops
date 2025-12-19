import asyncio
import os
import ssl
from logging.config import fileConfig

import certifi
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlmodel import SQLModel

from alembic import context

# Import app config to get database URL
from app.config import settings

# Import all models to ensure they are registered with SQLModel
from app.models import *  # noqa: F401, F403

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override the sqlalchemy.url with the one from our settings
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate support
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

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


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with the given connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    db_url = make_url(settings.database_url)
    connect_args = {}
    # Supabase Postgres requires SSL. For asyncpg, pass ssl=True via connect_args.
    if (
        db_url.host
        and (db_url.host.endswith("supabase.co") or db_url.host.endswith("supabase.com"))
    ) or ("sslmode" in db_url.query or "ssl" in db_url.query):
        # Default: verify using certifi CA bundle (avoids macOS Python cert store issues).
        ca_file = os.getenv("DB_SSL_CA_FILE")
        no_verify = os.getenv("DB_SSL_NO_VERIFY") in {"1", "true", "TRUE", "yes", "YES"}

        if no_verify:
            # Last-resort for corporate MITM/self-signed chains.
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        else:
            ctx = ssl.create_default_context(cafile=ca_file or certifi.where())

        connect_args = {"ssl": ctx}

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
