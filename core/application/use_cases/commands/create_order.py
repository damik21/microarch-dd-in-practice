from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from core.domain.model.order.order import Order
from core.ports.geo_service_client import GeoServiceClientInterface
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
        geo_service_client: GeoServiceClientInterface,
    ) -> None:
        self._order_repository = order_repository
        self._tracker = tracker
        self._geo_service_client = geo_service_client

    async def handle(self, command: CreateOrderCommand) -> None:
        location = await self._geo_service_client.get_location(command.street)
        order = Order.create(
            id=command.order_id,
            location=location,
            volume=command.volume,
        )
        async with self._tracker.transaction():
            await self._order_repository.add(order)
