"""Pytest configuration and fixtures."""

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.database import Base
from config.config import settings


@pytest.fixture
async def db_session():
    """
    Фикстура для создания тестовой сессии БД.

    Yields:
        AsyncSession: Тестовая сессия базы данных.
    """
    # Создаём in-memory базу для тестов (или используем testcontainers)
    # Для простоты используем те же настройки, но можно переопределить
    engine = create_async_engine(
        settings.database_url.replace("/delivery", "/test_delivery"),
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()
