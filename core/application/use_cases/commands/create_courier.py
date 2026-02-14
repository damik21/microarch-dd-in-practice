from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from core.domain.model.courier.courier import Courier
from core.domain.model.kernel.location import Location
from core.ports.courier_repository import CourierRepositoryInterface

if TYPE_CHECKING:
    from infrastructure.adapters.postgres.repositories.tracker import Tracker


@dataclass(frozen=True)
class CreateCourierCommand:
    name: str
    speed: int


class CreateCourierHandler:
    def __init__(
        self,
        courier_repository: CourierRepositoryInterface,
        tracker: Tracker,
    ) -> None:
        self._courier_repository = courier_repository
        self._tracker = tracker

    async def handle(self, command: CreateCourierCommand) -> None:
        courier = Courier.create(
            name=command.name,
            speed=command.speed,
            location=Location.new_random_location(),
        )
        async with self._tracker.transaction():
            await self._courier_repository.add(courier)
