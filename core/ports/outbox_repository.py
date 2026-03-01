from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from core.domain.events.order import OrderDomainEvent


@dataclass(frozen=True)
class OutboxMessage:
    id: UUID
    event: OrderDomainEvent


class OutboxRepositoryInterface(ABC):
    @abstractmethod
    async def add(self, event: OrderDomainEvent) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_unprocessed(self, limit: int) -> list[OutboxMessage]:
        raise NotImplementedError

    @abstractmethod
    async def mark_processed(self, message_id: UUID) -> None:
        raise NotImplementedError
