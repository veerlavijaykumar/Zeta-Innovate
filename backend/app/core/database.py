"""Database connection and session management."""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

import urllib.parse

db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine_kwargs = {"echo": settings.DEBUG}

if not db_url.startswith("sqlite"):
    connect_args = {}
    # asyncpg does not accept ?sslmode=... or ?channel_binding=... in the query string
    if "?" in db_url:
        parsed = urllib.parse.urlparse(db_url)
        query_params = urllib.parse.parse_qs(parsed.query)
        if "sslmode" in query_params or "channel_binding" in query_params or "neon.tech" in db_url or "supabase" in db_url:
            connect_args["ssl"] = True
        # Clean unsupported query parameters for asyncpg
        clean_query = "&".join(
            f"{k}={v[0]}" for k, v in query_params.items()
            if k not in ["sslmode", "channel_binding"]
        )
        db_url = urllib.parse.urlunparse(parsed._replace(query=clean_query))
    elif "neon.tech" in db_url or "supabase" in db_url:
        connect_args["ssl"] = True

    if "neon.tech" in db_url or "pooler" in db_url:
        connect_args["statement_cache_size"] = 0
        connect_args["prepared_statement_cache_size"] = 0

    engine_kwargs.update({
        "pool_size": 20,
        "max_overflow": 10,
        "pool_pre_ping": True,
        "pool_recycle": 300,
    })
    if connect_args:
        engine_kwargs["connect_args"] = connect_args

engine = create_async_engine(
    db_url,
    **engine_kwargs
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


async def get_db() -> AsyncSession:
    """Dependency that yields a database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    import app.models  # noqa: F401 - ensure models are registered with Base.metadata
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
