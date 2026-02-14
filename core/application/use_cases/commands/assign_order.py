from __future__ import annotations

from typing import TYPE_CHECKING

from core.ports.courier_repository import CourierRepositoryInterface
from core.ports.order_dispatcher import OrderDispatcherInterface
from core.ports.order_repository import OrderRepositoryInterface

if TYPE_CHECKING:
    from infrastructure.adapters.postgres.repositories.tracker import Tracker


class AssignOrderHandler:
    def __init__(
        self,
        order_repository: OrderRepositoryInterface,
        courier_repository: CourierRepositoryInterface,
        dispatcher: OrderDispatcherInterface,
        tracker: Tracker,
    ) -> None:
        self._order_repository = order_repository
        self._courier_repository = courier_repository
        self._dispatcher = dispatcher
        self._tracker = tracker

    async def handle(self) -> None:
        order = await self._order_repository.get_first_created()
        if order is None:
            return

        couriers = await self._courier_repository.get_all_free()
        if not couriers:
            return

        courier = self._dispatcher.dispatch(order, couriers)
        if courier is None:
            return

        async with self._tracker.transaction():
            await self._order_repository.update(order)
            await self._courier_repository.update(courier)
