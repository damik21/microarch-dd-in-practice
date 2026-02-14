from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from core.domain.exceptions.courier import CourierNotFound
from core.ports.courier_repository import CourierRepositoryInterface

if TYPE_CHECKING:
    from infrastructure.adapters.postgres.repositories.tracker import Tracker


@dataclass(frozen=True)
class AddStoragePlaceCommand:
    courier_id: UUID
    name: str
    total_volume: int


class AddStoragePlaceHandler:
    def __init__(
        self,
        courier_repository: CourierRepositoryInterface,
        tracker: Tracker,
    ) -> None:
        self._courier_repository = courier_repository
        self._tracker = tracker

    async def handle(self, command: AddStoragePlaceCommand) -> None:
        courier = await self._courier_repository.get_by_id(str(command.courier_id))
        if courier is None:
            raise CourierNotFound(f"Курьер с id {command.courier_id} не найден.")

        courier.add_storage_place(command.name, command.total_volume)
        async with self._tracker.transaction():
            await self._courier_repository.update(courier)
