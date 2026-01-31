from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.domain.model.courier.courier import Courier
    from core.domain.model.order.order import Order


class OrderDispatcherInterface(ABC):
    @abstractmethod
    def dispatch(self, order: Order, couriers: list[Courier]) -> Courier | None:
        pass
