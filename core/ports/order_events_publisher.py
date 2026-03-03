from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID


class OrderEventsPublisherInterface(ABC):
    @abstractmethod
    async def publish_order_created(self, order_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def publish_order_completed(self, order_id: UUID, courier_id: UUID) -> None:
        raise NotImplementedError
