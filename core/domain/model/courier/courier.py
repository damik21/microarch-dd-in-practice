import math
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from core.domain.model.courier.storage_place import StoragePlace
from core.domain.model.kernel.location import Location


DEFAULT_BAG_NAME: str = "Сумка"
DEFAULT_BAG_VOLUME: int = 10


@dataclass
class Courier:
    id: UUID = field(default_factory=uuid4, init=False)
    name: str
    speed: int
    location: Location
    storage_places: list[StoragePlace] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Имя курьера не может быть пустым.")

        if self.speed <= 0:
            raise ValueError("Скорость курьера должна быть больше 0.")

        # Каждый курьер всегда имеет базовое место хранения "Сумка".
        default_bag = StoragePlace(name=DEFAULT_BAG_NAME, total_volume=DEFAULT_BAG_VOLUME)
        self.storage_places.append(default_bag)

    def add_storage_place(self, name: str, total_volume: int) -> StoragePlace:
        storage_place = StoragePlace(name=name, total_volume=total_volume)
        self.storage_places.append(storage_place)
        return storage_place

    def can_take_order(self, volume: int) -> bool:
        return any(place.can_store(volume) for place in self.storage_places)

    def take_order(self, order_id: UUID, volume: int) -> None:
        for place in self.storage_places:
            if place.can_store(volume):
                place.store(order_id=order_id, volume=volume)
                return

        raise ValueError("Курьер не может взять заказ: нет свободного места хранения.")

    def complete_order(self, order_id: UUID) -> None:
        for place in self.storage_places:
            if place.order_id == order_id:
                place.clear()
                return

        raise ValueError("У курьера нет активного заказа с указанным идентификатором.")

    def calculate_steps_to_location(self, target: Location) -> int:
        distance = self.location.distance_to(target)
        return int(math.ceil(distance / self.speed))

    def move(self, target: Location) -> None:
        """Перемещает курьера в сторону указанной локации.

        За один вызов метод перемещает курьера не более чем на его скорость
        (в тактах) с учётом ограничений по осям X и Y.
        """

        dx = float(target.x - self.location.x)
        dy = float(target.y - self.location.y)
        remaining_range = float(self.speed)

        if abs(dx) > remaining_range:
            dx = math.copysign(remaining_range, dx)
        remaining_range -= abs(dx)

        if abs(dy) > remaining_range:
            dy = math.copysign(remaining_range, dy)

        new_x = self.location.x + int(dx)
        new_y = self.location.y + int(dy)

        self.location = Location(x=new_x, y=new_y)
