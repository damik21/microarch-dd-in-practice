from __future__ import annotations

from enum import Enum
from uuid import UUID, uuid4

from core.domain.model.kernel.location import Location


class OrderStatus(Enum):
    CREATED = "CREATED"
    ASSIGNED = "ASSIGNED"
    COMPLETED = "COMPLETED"


class Order:
    __id: UUID
    __location: Location
    __volume: int
    __courier_id: UUID | None
    __status: OrderStatus

    @classmethod
    def create(
        cls,
        id: UUID,
        location: Location,
        volume: int,
    ) -> Order:
        if volume <= 0:
            raise ValueError("Объём заказа должен быть больше 0.")
        return cls._new(
            id=id,
            location=location,
            volume=volume,
            courier_id=None,
            status=OrderStatus.CREATED,
        )

    @classmethod
    def _new(
        cls,
        id: UUID,
        location: Location,
        volume: int,
        courier_id: UUID | None,
        status: OrderStatus,
    ) -> Order:
        instance = object.__new__(cls)
        instance.__id = id
        instance._Order__location = location
        instance._Order__volume = volume
        instance._Order__courier_id = courier_id
        instance._Order__status = status
        return instance

    def __init__(
        self,
        id: UUID,
        location: Location | None = None,
        volume: int = 0,
        courier_id: UUID | None = None,
        status: OrderStatus = OrderStatus.CREATED,
    ) -> None:
        raise TypeError("Используйте Order.create() для создания экземпляра.")

    @property
    def location(self) -> Location:
        return self.__location

    @property
    def volume(self) -> int:
        return self.__volume

    @property
    def courier_id(self) -> UUID | None:
        return self.__courier_id

    @property
    def status(self) -> OrderStatus:
        return self.__status

    @property
    def id(self) -> UUID:
        return self.__id

    def assign(self, courier_id: UUID) -> None:
        if self.__status is OrderStatus.ASSIGNED:
            raise ValueError("Заказ уже назначен на курьера.")
        if self.__status is OrderStatus.COMPLETED:
            raise ValueError("Нельзя назначить завершённый заказ.")

        self.__courier_id = courier_id
        self.__status = OrderStatus.ASSIGNED

    def complete(self) -> None:
        if self.__status is not OrderStatus.ASSIGNED:
            raise ValueError("Завершить можно только назначенный заказ.")

        self.__status = OrderStatus.COMPLETED

