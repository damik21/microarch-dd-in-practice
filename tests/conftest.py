from collections.abc import AsyncGenerator
from typing import Any

import pytest
from sqlalchemy import NullPool, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config.config import settings
from infrastructure.adapters.postgres.models.base import Base


# Тестовый движок с отдельной базой данных
TEST_DATABASE_URL = settings.database_url.replace(
    f"/{settings.db_name}",
    f"/{settings.db_name}_test",
)

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

_DATABASE_AVAILABLE: bool | None = None


def _is_database_available() -> bool:
    """Проверить доступность базы данных."""
    global _DATABASE_AVAILABLE

    if _DATABASE_AVAILABLE is not None:
        return _DATABASE_AVAILABLE

    import socket

    try:
        # Проверяем TCP соединение с БД
        sock = socket.create_connection(
            (settings.db_host, int(settings.db_port)), timeout=1
        )
        sock.close()
        _DATABASE_AVAILABLE = True
        return True
    except OSError:
        _DATABASE_AVAILABLE = False
        return False


async def _clean_tables() -> None:
    """Очистить все таблицы через TRUNCATE."""
    async with test_engine.begin() as conn:
        # Отключаем проверки внешних ключей
        await conn.execute(text("SET session_replication_role = 'replica'"))
        # Очищаем все таблицы в правильном порядке
        await conn.execute(text("TRUNCATE TABLE orders, storage_places, couriers CASCADE"))
        # Включаем проверки обратно
        await conn.execute(text("SET session_replication_role = 'origin'"))


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession]:
    """Создать новую сессию БД для каждого теста."""
    if not _is_database_available():
        pytest.skip("База данных недоступна")

    # Создаём все таблицы (если не существуют)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Очищаем таблицы перед тестом
    await _clean_tables()

    # Создаём сессию
    async with TestSessionLocal() as session:
        yield session

    # Очищаем таблицы после теста
    await _clean_tables()


@pytest.fixture
def tracker(db_session: AsyncSession) -> Any:
    """Создать Tracker для тестов."""
    from infrastructure.adapters.postgres.repositories.base import RepositoryTracker

    return RepositoryTracker(db_session)


@pytest.fixture
def mock_tracker() -> Any:
    """Создать мок Tracker для тестов без БД."""
    from infrastructure.adapters.postgres.repositories.base import RepositoryTracker
    from unittest.mock import AsyncMock, MagicMock

    # Создаём мок сессии
    mock_session = MagicMock(spec=AsyncSession)
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.begin = MagicMock()
    mock_session.begin.return_value.__aenter__.return_value = mock_session
    mock_session.begin.return_value.__aexit__ = AsyncMock()

    return RepositoryTracker(mock_session)
