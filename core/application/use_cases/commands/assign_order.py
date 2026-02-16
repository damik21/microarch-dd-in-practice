from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from core.ports.courier_repository import CourierRepositoryInterface
from core.ports.order_dispatcher import OrderDispatcherInterface
from core.ports.order_repository import OrderRepositoryInterface

if TYPE_CHECKING:
    from infrastructure.adapters.postgres.repositories.tracker import Tracker


@dataclass
class AssignResult:
    order_id: UUID
    courier_id: UUID


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

    async def handle(self) -> AssignResult | None:
        order = await self._order_repository.get_first_created()
        if order is None:
            return None

        couriers = await self._courier_repository.get_all_free()
        if not couriers:
            return None

        courier = self._dispatcher.dispatch(order, couriers)
        if courier is None:
            return None

        async with self._tracker.transaction():
            await self._order_repository.update(order)
            await self._courier_repository.update(courier)

        return AssignResult(order_id=order.id, courier_id=courier.id)
