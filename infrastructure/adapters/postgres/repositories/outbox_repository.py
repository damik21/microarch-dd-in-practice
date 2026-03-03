from __future__ import annotations

from datetime import UTC, datetime
import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.domain.events.order import (
    OrderCompletedDomainEvent,
    OrderCreatedDomainEvent,
    OrderDomainEvent,
)
from core.ports.outbox_repository import OutboxMessage, OutboxRepositoryInterface
from infrastructure.adapters.postgres.models.outbox import OutboxDTO
from infrastructure.adapters.postgres.repositories.tracker import Tracker

logger = logging.getLogger(__name__)


def domain_event_to_dto(event: OrderDomainEvent) -> OutboxDTO:
    if isinstance(event, OrderCreatedDomainEvent):
        payload = {"order_id": str(event.order_id)}
    else:
        payload = {
            "order_id": str(event.order_id),
            "courier_id": str(event.courier_id),
        }

    return OutboxDTO(
        event_name=event.name,
        payload=payload,
        processed_at=None,
    )


def dto_to_domain_event(dto: OutboxDTO) -> OrderDomainEvent:
    if dto.event_name == OrderCreatedDomainEvent.__name__:
        order_id = UUID(dto.payload["order_id"])
        return OrderCreatedDomainEvent(order_id=order_id)

    if dto.event_name == OrderCompletedDomainEvent.__name__:
        order_id = UUID(dto.payload["order_id"])
        courier_id = UUID(dto.payload["courier_id"])
        return OrderCompletedDomainEvent(order_id=order_id, courier_id=courier_id)

    raise ValueError(f"Неизвестное имя доменного события: {dto.event_name}")


class OutboxRepository(OutboxRepositoryInterface):
    def __init__(self, tracker: Tracker) -> None:
        if tracker is None:
            raise ValueError("tracker не может быть None")
        self._tracker = tracker

    async def add(self, event: OrderDomainEvent) -> None:
        dto = domain_event_to_dto(event)
        session = self._tracker.db()
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

    async def get_unprocessed(self, limit: int) -> list[OutboxMessage]:
        session = self._get_tx_or_db()
        stmt = (
            select(OutboxDTO)
            .where(OutboxDTO.processed_at.is_(None))
            .order_by(OutboxDTO.created_at, OutboxDTO.id)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        result = await session.execute(stmt)
        dtos = result.scalars().all()
        messages: list[OutboxMessage] = []
        for dto in dtos:
            try:
                messages.append(
                    OutboxMessage(
                        id=dto.id,
                        event=dto_to_domain_event(dto),
                    )
                )
            except Exception:
                logger.exception(
                    "Ошибка при десериализации outbox-сообщения: "
                    "message_id=%s event_name=%s",
                    dto.id,
                    dto.event_name,
                )
                continue

        return messages

    async def mark_processed(self, message_id: UUID) -> None:
        session = self._tracker.db()
        is_in_transaction = self._tracker.in_tx()

        if not is_in_transaction:
            await self._tracker.begin()

        tx = self._tracker.tx() or session
        try:
            dto = await tx.get(OutboxDTO, message_id)
            if dto is not None:
                dto.processed_at = datetime.now(UTC)
            if not is_in_transaction:
                await self._tracker.commit()
        except Exception:
            if not is_in_transaction:
                await self._tracker.rollback()
            raise

    def _get_tx_or_db(self) -> AsyncSession:
        if tx := self._tracker.tx():
            return tx
        return self._tracker.db()
