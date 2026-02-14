from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.domain.model.courier.courier import Courier


class CourierRepositoryInterface(ABC):
    @abstractmethod
    async def add(self, courier: "Courier") -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, courier: "Courier") -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, courier_id: str) -> "Courier | None":
        raise NotImplementedError

    @abstractmethod
    async def get_first_free(self) -> "Courier | None":
        raise NotImplementedError

    @abstractmethod
    async def get_all_busy(self) -> list["Courier"]:
        raise NotImplementedError

    @abstractmethod
    async def get_all_free(self) -> list["Courier"]:
        raise NotImplementedError
