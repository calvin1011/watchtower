from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

_engine = None
_session_factory = None


def init_db(database_url: str) -> async_sessionmaker[AsyncSession]:
    global _engine, _session_factory
    url = database_url
    if url.startswith("postgres://"):
        url = "postgresql+asyncpg://" + url[11:]
    elif url.startswith("postgresql://") and "postgresql+asyncpg" not in url:
        url = "postgresql+asyncpg://" + url[13:]
    _engine = create_async_engine(
        url,
        echo=False,
        connect_args={"prepared_statement_cache_size": 0},
    )
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False, class_=AsyncSession)
    return _session_factory


async def get_session():
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db first.")
    async with _session_factory() as session:
        yield session


def session_context():
    """
    Async context manager for use outside FastAPI request scope (e.g. scheduler).

    Usage:
        async with session_context() as session:
            ...
    """
    if _session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db first.")
    return _session_factory()
