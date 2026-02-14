from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from core.domain.model.kernel.location import Location
from core.ports.courier_repository import CourierRepositoryInterface


@dataclass(frozen=True)
class CourierDTO:
    id: UUID
    name: str
    location: Location


class GetCouriersHandler:
    def __init__(self, courier_repository: CourierRepositoryInterface) -> None:
        self._courier_repository = courier_repository

    async def handle(self) -> list[CourierDTO]:
        couriers = await self._courier_repository.get_all()
        return [CourierDTO(id=c.id, name=c.name, location=c.location) for c in couriers]
