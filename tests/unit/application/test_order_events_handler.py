from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from core.application.event_handlers.order_events import OrderEventsHandler
from core.domain.events.order import (
    OrderCompletedDomainEvent,
    OrderCreatedDomainEvent,
)


@pytest.mark.asyncio
async def test_order_created_event_calls_created_publisher() -> None:
    publisher = AsyncMock()
    handler = OrderEventsHandler(publisher=publisher)
    event = OrderCreatedDomainEvent(order_id=uuid4())

    await handler.handle(event)

    publisher.publish_order_created.assert_called_once_with(order_id=event.order_id)
    publisher.publish_order_completed.assert_not_called()


@pytest.mark.asyncio
async def test_order_completed_event_calls_completed_publisher() -> None:
    publisher = AsyncMock()
    handler = OrderEventsHandler(publisher=publisher)
    event = OrderCompletedDomainEvent(order_id=uuid4(), courier_id=uuid4())

    await handler.handle(event)

    publisher.publish_order_completed.assert_called_once_with(
        order_id=event.order_id,
        courier_id=event.courier_id,
    )
    publisher.publish_order_created.assert_not_called()
