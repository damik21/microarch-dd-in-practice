from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.domain.model.kernel.location import Location
from core.domain.model.order.order import Order, OrderStatus
from core.ports.order_repository import OrderRepositoryInterface

from infrastructure.adapters.postgres.models.order import OrderDTO
from infrastructure.adapters.postgres.repositories.base import RepositoryTracker

if TYPE_CHECKING:
    from infrastructure.adapters.postgres.repositories.tracker import Tracker


def domain_to_dto(order: Order) -> OrderDTO:
    return OrderDTO(
        id=order.id,
        courier_id=order.courier_id,
        location_x=order.location.x,
        location_y=order.location.y,
        volume=order.volume,
        status=order.status,
    )


def dto_to_domain(dto: OrderDTO) -> Order:
    location = Location(x=dto.location_x, y=dto.location_y)
    # Используем _new для восстановления из БД
    return Order._new(
        id=dto.id,
        location=location,
        volume=dto.volume,
        courier_id=dto.courier_id,
        status=dto.status,
    )


class OrderRepository(OrderRepositoryInterface):
    def __init__(self, tracker: Tracker) -> None:
        if tracker is None:
            raise ValueError("tracker не может быть None")
        self._tracker = tracker

    async def add(self, order: Order) -> None:
        self._tracker.track(order)

        dto = domain_to_dto(order)
        session = self._tracker.db()

        # Проверяем, открыта ли транзакция
        is_in_transaction = self._tracker.in_tx()
        if not is_in_transaction:
            await self._tracker.begin()

        tx = self._tracker.tx() or session

        try:
            tx.add(dto)
            if not is_in_transaction:
                await self._tracker.commit()
        except Exception:
            if not is_in_transaction:
                await self._tracker.rollback()
            raise

    async def update(self, order: Order) -> None:
        self._tracker.track(order)

        dto = domain_to_dto(order)
        session = self._tracker.db()

        # Проверяем, открыта ли транзакция
        is_in_transaction = self._tracker.in_tx()
        if not is_in_transaction:
            await self._tracker.begin()

        tx = self._tracker.tx() or session

        try:
            # Используем merge для обновления существующей записи
            await session.merge(dto)
            if not is_in_transaction:
                await self._tracker.commit()
        except Exception:
            if not is_in_transaction:
                await self._tracker.rollback()
            raise

    async def get_by_id(self, order_id: str) -> Order | None:
        session = self._get_tx_or_db()

        stmt = select(OrderDTO).where(OrderDTO.id == uuid.UUID(order_id))
        result = await session.execute(stmt)
        dto = result.scalar_one_or_none()

        if dto is None:
            return None

        return dto_to_domain(dto)

    async def get_first_created(self) -> Order | None:
        session = self._get_tx_or_db()

        stmt = (
            select(OrderDTO)
            .where(OrderDTO.status == OrderStatus.CREATED)
            .order_by(OrderDTO.id)
            .limit(1)
        )
        result = await session.execute(stmt)
        dto = result.scalar_one_or_none()

        if dto is None:
            return None

        return dto_to_domain(dto)

    async def get_all_assigned(self) -> list[Order]:
        session = self._get_tx_or_db()

        stmt = select(OrderDTO).where(OrderDTO.status == OrderStatus.ASSIGNED)
        result = await session.execute(stmt)
        dtos = result.scalars().all()

        return [dto_to_domain(dto) for dto in dtos]

    def _get_tx_or_db(self) -> AsyncSession:
        if tx := self._tracker.tx():
            return tx
        return self._tracker.db()
