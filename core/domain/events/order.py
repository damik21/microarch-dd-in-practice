from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True)
class DomainEvent:
    name: str = field(init=False)

    def __post_init__(self) -> None:
        # Имя события вычисляется автоматически по имени класса.
        object.__setattr__(self, "name", self.__class__.__name__)


@dataclass(frozen=True)
class OrderCreatedDomainEvent(DomainEvent):
    order_id: UUID


@dataclass(frozen=True)
class OrderCompletedDomainEvent(DomainEvent):
    order_id: UUID
    courier_id: UUID


type OrderDomainEvent = OrderCreatedDomainEvent | OrderCompletedDomainEvent
