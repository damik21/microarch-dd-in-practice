from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.adapters.postgres.repositories.tracker import Tracker


class RepositoryTracker(Tracker):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._in_transaction = False
        self._tracked: set[object] = set()

    def tx(self) -> AsyncSession | None:
        """Получить текущую транзакцию."""
        return self._session if self._in_transaction else None

    def db(self) -> AsyncSession:
        """Получить сессию БД."""
        return self._session

    def in_tx(self) -> bool:
        """Проверить, открыта ли транзакция."""
        return self._in_transaction

    def track(self, aggregate: object) -> None:
        """Отследить изменения агрегата."""
        self._tracked.add(aggregate)

    async def begin(self) -> None:
        """Начать транзакцию."""
        if not self._in_transaction:
            await self._session.begin()
            self._in_transaction = True

    async def commit(self) -> None:
        """Зафиксировать транзакцию."""
        if self._in_transaction:
            await self._session.commit()
            self._in_transaction = False
            self._tracked.clear()

    async def rollback(self) -> None:
        """Откатить транзакцию."""
        if self._in_transaction:
            await self._session.rollback()
            self._in_transaction = False
            self._tracked.clear()
