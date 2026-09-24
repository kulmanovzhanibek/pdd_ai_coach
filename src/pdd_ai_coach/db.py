from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from pdd_ai_coach.config import settings

engine = create_async_engine(settings.database_url)
SessionLocal = async_sessionmaker[AsyncSession](engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
