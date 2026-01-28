from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class StoragePlace:
    id: UUID = field(default_factory=uuid4, init=False)
    name: str
    total_volume: int
    order_id: UUID | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Название места хранения не может быть пустым.")

        if self.total_volume <= 0:
            raise ValueError("Допустимый объём места хранения должен быть больше 0.")

    def equals(self, other: object) -> bool:
        if not isinstance(other, StoragePlace):
            return False
        return self.id == other.id

    def is_occupied(self) -> bool:
        return self.order_id is not None

    def can_store(self, volume: int) -> bool:
        if volume <= 0:
            raise ValueError("Объём заказа должен быть больше 0.")

        if self.is_occupied():
            return False

        return volume <= self.total_volume

    def store(self, order_id: UUID, volume: int) -> None:
        if not self.can_store(volume):
            raise ValueError(
                "Невозможно поместить заказ в место хранения: "
                "место уже занято или объём заказа превышает допустимый."
            )

        self.order_id = order_id

    def clear(self) -> None:
        self.order_id = None
