from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from core.ports.courier_repository import CourierRepositoryInterface
from core.ports.order_repository import OrderRepositoryInterface

if TYPE_CHECKING:
    from infrastructure.adapters.postgres.repositories.tracker import Tracker


@dataclass
class MoveResult:
    courier_id: UUID
    courier_name: str
    new_location: tuple[int, int]
    order_completed: bool


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

    async def handle(self) -> list[MoveResult]:
        results: list[MoveResult] = []

        orders = await self._order_repository.get_all_assigned()
        if not orders:
            return results

        couriers = await self._courier_repository.get_all()
        if not couriers:
            return results

        order_by_courier = {order.courier_id: order for order in orders}

        async with self._tracker.transaction():
            for courier in couriers:
                order = order_by_courier.get(courier.id)
                if order is None:
                    continue

                courier.move(order.location)

                order_completed = False
                if courier.location == order.location:
                    order.complete()
                    courier.complete_order(order.id)
                    await self._order_repository.update(order)
                    order_completed = True

                await self._courier_repository.update(courier)

                results.append(
                    MoveResult(
                        courier_id=courier.id,
                        courier_name=courier.name,
                        new_location=(courier.location.x, courier.location.y),
                        order_completed=order_completed,
                    )
                )

        return results
