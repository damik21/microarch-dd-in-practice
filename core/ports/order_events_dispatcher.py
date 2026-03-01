from __future__ import annotations

from abc import ABC, abstractmethod

from core.domain.events.order import (
    OrderCompletedDomainEvent,
    OrderCreatedDomainEvent,
)


class OrderEventsDispatcherInterface(ABC):
    @abstractmethod
    async def handle(
        self,
        event: OrderCreatedDomainEvent | OrderCompletedDomainEvent,
    ) -> None:
        raise NotImplementedError
