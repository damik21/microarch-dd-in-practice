from abc import ABC, abstractmethod

from sqlalchemy import ScalarResult
from sqlalchemy.ext.asyncio import AsyncSession


class Tracker(ABC):
    @abstractmethod
    def tx(self) -> AsyncSession | None:
        raise NotImplementedError

    @abstractmethod
    def db(self) -> AsyncSession:
        raise NotImplementedError

    @abstractmethod
    def in_tx(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def track(self, aggregate: object) -> None:
        raise NotImplementedError

    @abstractmethod
    async def begin(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError
