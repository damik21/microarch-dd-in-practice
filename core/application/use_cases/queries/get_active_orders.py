from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from core.domain.model.kernel.location import Location
from core.ports.order_repository import OrderRepositoryInterface


@dataclass(frozen=True)
class OrderDTO:
    id: UUID
    location: Location


class GetActiveOrdersHandler:
    def __init__(self, order_repository: OrderRepositoryInterface) -> None:
        self._order_repository = order_repository

    async def handle(self) -> list[OrderDTO]:
        orders = await self._order_repository.get_all_not_completed()
        return [OrderDTO(id=o.id, location=o.location) for o in orders]
