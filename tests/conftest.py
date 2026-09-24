import asyncio
from collections.abc import AsyncIterator, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from pdd_ai_coach.config import settings
from pdd_ai_coach.db import get_session
from pdd_ai_coach.main import app
from pdd_ai_coach.models import Base, RuleRow

test_engine = create_async_engine(settings.test_database_url, poolclass=NullPool)
TestSession = async_sessionmaker(test_engine, expire_on_commit=False)


async def override_get_session() -> AsyncIterator[AsyncSession]:
    async with TestSession() as session:
        yield session


async def reset_database() -> None:
    async with test_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestSession() as session:
        session.add_all(
            [
                RuleRow(number="91", text="При повороте направо или налево водитель уступает дорогу пешеходам.", chapter_number=13, chapter_title="Проезд перекрестков"),
                RuleRow(number="95", text="При повороте налево или развороте водитель уступает дорогу встречным.", chapter_number=13, chapter_title="Проезд перекрестков"),
                RuleRow(number="95-1", text="При повороте налево разъезд встречных осуществляется правыми сторонами.", chapter_number=13, chapter_title="Проезд перекрестков"),
            ]
        )
        await session.commit()


@pytest.fixture(scope="session", autouse=True)
def prepare_database() -> Iterator[None]:
    asyncio.run(reset_database())
    app.dependency_overrides[get_session] = override_get_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client
