from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.domain.model.courier.courier import Courier
from core.domain.model.courier.storage_place import StoragePlace
from core.domain.model.kernel.location import Location
from core.ports.courier_repository import CourierRepositoryInterface
from infrastructure.adapters.postgres.models.courier import CourierDTO
from infrastructure.adapters.postgres.models.storage_place import StoragePlaceDTO

if TYPE_CHECKING:
    from infrastructure.adapters.postgres.repositories.tracker import Tracker


def domain_to_dto(courier: Courier) -> CourierDTO:
    # Создаем DTO без storage_places (они загрузятся через cascade)
    return CourierDTO(
        id=courier.id,
        name=courier.name,
        speed=courier.speed,
        location_x=courier.location.x,
        location_y=courier.location.y,
        storage_places=[],
    )


def storage_place_domain_to_dto(
    storage_place: StoragePlace, courier_id: uuid.UUID
) -> StoragePlaceDTO:
    return StoragePlaceDTO(
        id=storage_place.id,
        courier_id=courier_id,
        name=storage_place.name,
        total_volume=storage_place.total_volume,
        order_id=storage_place.order_id,
    )


def dto_to_domain(dto: CourierDTO) -> Courier:
    location = Location(x=dto.location_x, y=dto.location_y)

    # Преобразуем storage_places из DTO в доменные модели
    storage_places = []
    for sp_dto in dto.storage_places:
        # Используем _new для восстановления из БД
        sp = StoragePlace._new(
            name=sp_dto.name,
            total_volume=sp_dto.total_volume,
            order_id=sp_dto.order_id,
        )
        # Подменяем id на тот, что из БД (вместо сгенерированного в _new)
        sp.id = sp_dto.id
        storage_places.append(sp)

    # Используем _new для восстановления из БД
    courier = Courier._new(
        name=dto.name,
        speed=dto.speed,
        location=location,
        storage_places=storage_places,
    )
    # Подменяем id на тот, что из БД
    courier.id = dto.id
    return courier


class CourierRepository(CourierRepositoryInterface):
    def __init__(self, tracker: Tracker) -> None:
        if tracker is None:
            raise ValueError("tracker не может быть None")
        self._tracker = tracker

    async def add(self, courier: Courier) -> None:
        self._tracker.track(courier)

        dto = domain_to_dto(courier)
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

    async def update(self, courier: Courier) -> None:
        self._tracker.track(courier)

        dto = domain_to_dto(courier)
        session = self._tracker.db()

        # Проверяем, открыта ли транзакция
        is_in_transaction = self._tracker.in_tx()
        if not is_in_transaction:
            await self._tracker.begin()

        try:
            # Используем merge для обновления существующей записи
            await session.merge(dto)
            if not is_in_transaction:
                await self._tracker.commit()
        except Exception:
            if not is_in_transaction:
                await self._tracker.rollback()
            raise

    async def get_by_id(self, courier_id: str) -> Courier | None:
        session = self._get_tx_or_db()

        stmt = (
            select(CourierDTO)
            .options(selectinload(CourierDTO.storage_places))
            .where(CourierDTO.id == uuid.UUID(courier_id))
        )
        result = await session.execute(stmt)
        dto = result.scalar_one_or_none()

        if dto is None:
            return None

        return dto_to_domain(dto)

    async def get_first_free(self) -> Courier | None:
        session = self._get_tx_or_db()

        # Ищем курьеров, у которых все storage_places имеют order_id = None
        # Это сложный запрос, поэтому делаем в два этапа:
        # 1. Получаем всех курьеров с их storage_places
        # 2. Фильтруем в Python

        stmt = (
            select(CourierDTO)
            .options(selectinload(CourierDTO.storage_places))
            .order_by(CourierDTO.id)
        )
        result = await session.execute(stmt)
        dtos = result.scalars().all()

        # Фильтруем свободных курьеров
        for dto in dtos:
            # Курьер свободен, если у него нет order_id ни в одном storage_place
            if all(sp.order_id is None for sp in dto.storage_places):
                return dto_to_domain(dto)

        return None

    async def get_all_busy(self) -> list[Courier]:
        session = self._get_tx_or_db()

        # Ищем курьеров, у которых хотя бы один storage_place имеет order_id != None
        stmt = (
            select(CourierDTO)
            .options(selectinload(CourierDTO.storage_places))
            .order_by(CourierDTO.id)
        )
        result = await session.execute(stmt)
        dtos = result.scalars().all()

        # Фильтруем занятых курьеров
        busy_couriers = []
        for dto in dtos:
            # Курьер занят, если у него есть хотя бы один order_id в storage_places
            if any(sp.order_id is not None for sp in dto.storage_places):
                busy_couriers.append(dto_to_domain(dto))

        return busy_couriers

    async def get_all_free(self) -> list[Courier]:
        session = self._get_tx_or_db()

        stmt = (
            select(CourierDTO)
            .options(selectinload(CourierDTO.storage_places))
            .order_by(CourierDTO.id)
        )
        result = await session.execute(stmt)
        dtos = result.scalars().all()

        free_couriers = []
        for dto in dtos:
            if all(sp.order_id is None for sp in dto.storage_places):
                free_couriers.append(dto_to_domain(dto))

        return free_couriers

    def _get_tx_or_db(self) -> AsyncSession:
        if tx := self._tracker.tx():
            return tx
        return self._tracker.db()
