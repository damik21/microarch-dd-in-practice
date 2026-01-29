from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID

from core.domain.model.kernel.location import Location


class OrderStatus(Enum):
    CREATED = "CREATED"
    ASSIGNED = "ASSIGNED"
    COMPLETED = "COMPLETED"


@dataclass
class Order:
    id: UUID
    location: Location
    volume: int
    courier_id: UUID | None = None
    status: OrderStatus = field(default=OrderStatus.CREATED, init=False)

    def __post_init__(self) -> None:
        if self.volume <= 0:
            raise ValueError("Объём заказа должен быть больше 0.")

    def assign(self, courier_id: UUID) -> None:
        if self.status is OrderStatus.ASSIGNED:
            raise ValueError("Заказ уже назначен на курьера.")
        if self.status is OrderStatus.COMPLETED:
            raise ValueError("Нельзя назначить завершённый заказ.")

        self.courier_id = courier_id
        self.status = OrderStatus.ASSIGNED

    def complete(self) -> None:
        if self.status is not OrderStatus.ASSIGNED:
            raise ValueError("Завершить можно только назначенный заказ.")

        self.status = OrderStatus.COMPLETED

