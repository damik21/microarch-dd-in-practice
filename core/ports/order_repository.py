from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.domain.model.order.order import Order


class OrderRepositoryInterface(ABC):
    @abstractmethod
    async def add(self, order: "Order") -> None:
        """Добавить новый заказ.

        Args:
            order: Доменная модель заказа.
        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, order: "Order") -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, order_id: str) -> "Order | None":
        raise NotImplementedError

    @abstractmethod
    async def get_first_created(self) -> "Order | None":
        raise NotImplementedError

    @abstractmethod
    async def get_all_assigned(self) -> list["Order"]:
        raise NotImplementedError

    @abstractmethod
    async def get_all_not_completed(self) -> list["Order"]:
        raise NotImplementedError
