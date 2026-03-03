from __future__ import annotations

from core.domain.events.order import (
    OrderCreatedDomainEvent,
    OrderDomainEvent,
)
from core.ports.order_events_dispatcher import OrderEventsDispatcherInterface
from core.ports.order_events_publisher import OrderEventsPublisherInterface


class OrderEventsHandler(OrderEventsDispatcherInterface):
    def __init__(self, publisher: OrderEventsPublisherInterface) -> None:
        self._publisher = publisher

    async def handle(
        self,
        event: OrderDomainEvent,
    ) -> None:
        if isinstance(event, OrderCreatedDomainEvent):
            await self._publisher.publish_order_created(order_id=event.order_id)
            return

        await self._publisher.publish_order_completed(
            order_id=event.order_id,
            courier_id=event.courier_id,
        )
