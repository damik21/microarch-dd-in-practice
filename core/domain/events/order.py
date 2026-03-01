from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class OrderCreatedDomainEvent:
    order_id: UUID


@dataclass(frozen=True)
class OrderCompletedDomainEvent:
    order_id: UUID
    courier_id: UUID
