from __future__ import annotations

import math
from dataclasses import field
from uuid import UUID, uuid4

from core.domain.exceptions.courier import (
    CourierCannotTakeOrder,
    CourierNameIncorrect,
    CourierSpeedIncorrect,
)
from core.domain.exceptions.storage_place import CourierHasNoSuchOrder
from core.domain.model.courier.storage_place import StoragePlace
from core.domain.model.kernel.location import Location

DEFAULT_BAG_NAME: str = "Сумка"
DEFAULT_BAG_VOLUME: int = 10


class Courier:
    id: UUID = field(default_factory=uuid4, init=False)
    __name: str
    __speed: int
    __location: Location
    __storage_places: list[StoragePlace] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        name: str,
        speed: int,
        location: Location,
    ) -> Courier:
        if not name.strip():
            raise CourierNameIncorrect("Имя курьера не может быть пустым.")
        if speed <= 0:
            raise CourierSpeedIncorrect("Скорость курьера должна быть больше 0.")
        default_bag = StoragePlace.create(
            name=DEFAULT_BAG_NAME, total_volume=DEFAULT_BAG_VOLUME
        )
        return cls._new(
            name=name,
            speed=speed,
            location=location,
            storage_places=[default_bag],
        )

    @classmethod
    def _new(
        cls,
        name: str,
        speed: int,
        location: Location,
        storage_places: list[StoragePlace],
    ) -> Courier:
        instance = object.__new__(cls)
        instance.id = uuid4()
        instance._Courier__name = name
        instance._Courier__speed = speed
        instance._Courier__location = location
        instance._Courier__storage_places = list(storage_places)
        return instance

    def __init__(
        self,
        name: str = "",
        speed: int = 0,
        location: Location | None = None,
        storage_places: list[StoragePlace] | None = None,
    ) -> None:
        raise TypeError("Используйте Courier.create() для создания экземпляра.")

    def add_storage_place(self, name: str, total_volume: int) -> StoragePlace:
        storage_place = StoragePlace.create(name=name, total_volume=total_volume)
        self.__storage_places.append(storage_place)
        return storage_place

    def can_take_order(self, volume: int) -> bool:
        return any(place.can_store(volume) for place in self.__storage_places)

    def take_order(self, order_id: UUID, volume: int) -> None:
        for place in self.__storage_places:
            if place.can_store(volume):
                place.store(order_id=order_id, volume=volume)
                return

        raise CourierCannotTakeOrder(
            "Курьер не может взять заказ: нет свободного места хранения."
        )

    def complete_order(self, order_id: UUID) -> None:
        for place in self.__storage_places:
            if place.order_id == order_id:
                place.clear()
                return

        raise CourierHasNoSuchOrder(
            "У курьера нет активного заказа с указанным идентификатором."
        )

    def calculate_steps_to_location(self, target: Location) -> int:
        distance = self.__location.distance_to(target)
        return int(math.ceil(distance / self.__speed))

    def move(self, target: Location) -> None:
        """Перемещает курьера в сторону указанной локации.

        За один вызов метод перемещает курьера не более чем на его скорость
        (в тактах) с учётом ограничений по осям X и Y.
        """

        dx = float(target.x - self.__location.x)
        dy = float(target.y - self.__location.y)
        remaining_range = float(self.__speed)

        if abs(dx) > remaining_range:
            dx = math.copysign(remaining_range, dx)
        remaining_range -= abs(dx)

        if abs(dy) > remaining_range:
            dy = math.copysign(remaining_range, dy)

        new_x = self.__location.x + int(dx)
        new_y = self.__location.y + int(dy)

        self.__location = Location(x=new_x, y=new_y)
