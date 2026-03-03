from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from core.domain.events.order import OrderCreatedDomainEvent
from infrastructure.adapters.postgres.models.outbox import OutboxDTO
from infrastructure.adapters.postgres.repositories.outbox_repository import (
    OutboxRepository,
)


class TestOutboxRepository:
    @pytest.mark.asyncio
    async def test_get_unprocessed_logs_invalid_event_and_continues(self) -> None:
        valid_order_id = uuid4()
        valid_dto = OutboxDTO(
            id=uuid4(),
            event_name="OrderCreatedDomainEvent",
            payload={"order_id": str(valid_order_id)},
            processed_at=None,
        )
        invalid_dto = OutboxDTO(
            id=uuid4(),
            event_name="UnknownEvent",
            payload={"order_id": str(uuid4())},
            processed_at=None,
        )

        result = MagicMock()
        result.scalars.return_value.all.return_value = [valid_dto, invalid_dto]

        session = AsyncMock()
        session.execute.return_value = result

        tracker = MagicMock()
        tracker.tx.return_value = None
        tracker.db.return_value = session
        tracker.in_tx.return_value = False

        repository = OutboxRepository(tracker)

        with patch(
            "infrastructure.adapters.postgres.repositories.outbox_repository.logger"
        ) as mock_logger:
            messages = await repository.get_unprocessed(limit=100)

        assert len(messages) == 1
        message = messages[0]
        assert message.id == valid_dto.id
        assert isinstance(message.event, OrderCreatedDomainEvent)
        assert message.event.order_id == valid_order_id
        mock_logger.exception.assert_called_once()
