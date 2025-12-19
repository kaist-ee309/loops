import os
import ssl
from collections.abc import AsyncGenerator
from pathlib import Path

import certifi
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings

# Import all models here to ensure they are registered with SQLModel
from app.models import *  # noqa: F401, F403

# Supabase root CA certificate path (relative to project root)
_SUPABASE_CA_CERT = Path(__file__).resolve().parents[2] / "certs" / "prod-ca-2021.crt"

# Create async engine
_db_url = make_url(settings.database_url)
_connect_args = {}
# Supabase Postgres requires SSL. For asyncpg, pass ssl=True via connect_args.
if (
    _db_url.host and (_db_url.host.endswith("supabase.co") or _db_url.host.endswith("supabase.com"))
) or ("sslmode" in _db_url.query or "ssl" in _db_url.query):
    ca_file = os.getenv("DB_SSL_CA_FILE")
    no_verify = os.getenv("DB_SSL_NO_VERIFY") in {"1", "true", "TRUE", "yes", "YES"}

    if no_verify:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    elif ca_file:
        ctx = ssl.create_default_context(cafile=ca_file)
    elif _SUPABASE_CA_CERT.exists():
        # Use Supabase's self-signed root CA certificate
        ctx = ssl.create_default_context(cafile=str(_SUPABASE_CA_CERT))
    else:
        # Fallback to certifi (won't work with Supabase's self-signed cert)
        ctx = ssl.create_default_context(cafile=certifi.where())

    _connect_args = {"ssl": ctx}

engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args=_connect_args,
)

# Create async session factory using SQLModel's AsyncSession
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.

    Usage:
        @router.get("/items")
        async def get_items(session: AsyncSession = Depends(get_session)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
