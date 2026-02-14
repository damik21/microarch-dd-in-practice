from __future__ import annotations

from typing import TYPE_CHECKING

from core.ports.courier_repository import CourierRepositoryInterface
from core.ports.order_repository import OrderRepositoryInterface

if TYPE_CHECKING:
    from infrastructure.adapters.postgres.repositories.tracker import Tracker


class MoveCouriersHandler:
    def __init__(
        self,
        order_repository: OrderRepositoryInterface,
        courier_repository: CourierRepositoryInterface,
        tracker: Tracker,
    ) -> None:
        self._order_repository = order_repository
        self._courier_repository = courier_repository
        self._tracker = tracker

    async def handle(self) -> None:
        orders = await self._order_repository.get_all_assigned()
        if not orders:
            return

        couriers = await self._courier_repository.get_all_busy()
        if not couriers:
            return

        order_by_courier = {order.courier_id: order for order in orders}

        async with self._tracker.transaction():
            for courier in couriers:
                order = order_by_courier.get(courier.id)
                if order is None:
                    continue

                courier.move(order.location)

                if courier.location == order.location:
                    order.complete()
                    courier.complete_order(order.id)
                    await self._order_repository.update(order)

                await self._courier_repository.update(courier)
