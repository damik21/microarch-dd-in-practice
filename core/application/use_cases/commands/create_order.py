from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from core.domain.model.kernel.location import Location
from core.domain.model.order.order import Order
from core.ports.order_repository import OrderRepositoryInterface

if TYPE_CHECKING:
    from infrastructure.adapters.postgres.repositories.tracker import Tracker


@dataclass(frozen=True)
class CreateOrderCommand:
    order_id: UUID
    street: str
    volume: int


class CreateOrderHandler:
    def __init__(
        self,
        order_repository: OrderRepositoryInterface,
        tracker: Tracker,
    ) -> None:
        self._order_repository = order_repository
        self._tracker = tracker

    async def handle(self, command: CreateOrderCommand) -> None:
        order = Order.create(
            id=command.order_id,
            location=Location.new_random_location(),
            volume=command.volume,
        )
        async with self._tracker.transaction():
            await self._order_repository.add(order)
