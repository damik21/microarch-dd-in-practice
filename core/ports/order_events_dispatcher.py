from __future__ import annotations

from abc import ABC, abstractmethod

from core.domain.events.order import OrderDomainEvent


class OrderEventsDispatcherInterface(ABC):
    @abstractmethod
    async def handle(
        self,
        event: OrderDomainEvent,
    ) -> None:
        raise NotImplementedError
