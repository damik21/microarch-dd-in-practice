from __future__ import annotations

from uuid import UUID, uuid4

from core.domain.exceptions.courier import OrderVolumeIncorrect
from core.domain.exceptions.storage_place import (
    StorageCannotStoreOrder,
    StoragePlaceNameIncorrect,
    StoragePlaceTotalValueIncorrect,
)


class StoragePlace:
    id: UUID
    __name: str
    __total_volume: int
    __order_id: UUID | None = None

    @classmethod
    def create(
        cls,
        name: str,
        total_volume: int,
        order_id: UUID | None = None,
    ) -> StoragePlace:
        if not name.strip():
            raise StoragePlaceNameIncorrect(
                "Название места хранения не может быть пустым."
            )
        if total_volume <= 0:
            raise StoragePlaceTotalValueIncorrect(
                "Допустимый объём места хранения должен быть больше 0."
            )
        return cls._new(name=name, total_volume=total_volume, order_id=order_id)

    @classmethod
    def _new(
        cls,
        name: str,
        total_volume: int,
        order_id: UUID | None = None,
    ) -> StoragePlace:
        instance = object.__new__(cls)
        instance.id = uuid4()
        instance.__name = name
        instance.__total_volume = total_volume
        instance.__order_id = order_id
        return instance

    def __init__(
        self,
        name: str = "",
        total_volume: int = 0,
        order_id: UUID | None = None,
    ) -> None:
        raise TypeError("Используйте StoragePlace.create() для создания экземпляра.")

    @property
    def order_id(self) -> UUID | None:
        return self.__order_id

    @property
    def name(self) -> str:
        """Получить название места хранения."""
        return self.__name

    @property
    def total_volume(self) -> int:
        """Получить общий объём места хранения."""
        return self.__total_volume

    def equals(self, other: object) -> bool:
        if not isinstance(other, StoragePlace):
            return False
        return self.id == other.id

    def is_occupied(self) -> bool:
        return self.__order_id is not None

    def can_store(self, volume: int) -> bool:
        if volume <= 0:
            raise OrderVolumeIncorrect("Объём заказа должен быть больше 0.")

        if self.is_occupied():
            return False

        return volume <= self.__total_volume

    def store(self, order_id: UUID, volume: int) -> None:
        if not self.can_store(volume):
            raise StorageCannotStoreOrder(
                "Невозможно поместить заказ в место хранения: "
                "место уже занято или объём заказа превышает допустимый."
            )

        self.__order_id = order_id

    def clear(self) -> None:
        self.__order_id = None
