import asyncio
import logging
from collections.abc import Callable, Coroutine
from typing import Any

from config.config import settings
from core.application.event_handlers.order_events import OrderEventsHandler
from core.application.use_cases.commands.assign_order import AssignOrderHandler
from core.application.use_cases.commands.move_couriers import MoveCouriersHandler
from core.domain.services import OrderDispatcher
from infrastructure.adapters.kafka.order_events_producer import KafkaOrderEventsProducer
from infrastructure.adapters.postgres.repositories.base import RepositoryTracker
from infrastructure.adapters.postgres.repositories.courier_repository import (
    CourierRepository,
)
from infrastructure.adapters.postgres.repositories.order_repository import (
    OrderRepository,
)
from infrastructure.adapters.postgres.repositories.outbox_repository import (
    OutboxRepository,
)
from infrastructure.db import async_session_maker

logger = logging.getLogger(__name__)
OUTBOX_BATCH_SIZE = 100


async def run_periodic(
    task: Callable[[], Coroutine[Any, Any, None]],
    interval: float,
    name: str,
) -> None:
    while True:
        try:
            await task()
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Error in periodic task %s", name)
        await asyncio.sleep(interval)


async def assign_orders() -> None:
    async with async_session_maker() as session:
        tracker = RepositoryTracker(session)
        handler = AssignOrderHandler(
            order_repository=OrderRepository(tracker),
            courier_repository=CourierRepository(tracker),
            dispatcher=OrderDispatcher(),
            tracker=tracker,
        )
        result = await handler.handle()
        if result:
            logger.info(
                "Order %s assigned to courier %s",
                result.order_id,
                result.courier_id,
            )


async def move_couriers() -> None:
    async with async_session_maker() as session:
        tracker = RepositoryTracker(session)
        handler = MoveCouriersHandler(
            order_repository=OrderRepository(tracker),
            courier_repository=CourierRepository(tracker),
            tracker=tracker,
            outbox_repository=OutboxRepository(tracker),
        )
        results = await handler.handle()
        for r in results:
            if r.order_completed:
                logger.info(
                    "Courier '%s' (%s) completed delivery at %s",
                    r.courier_name,
                    r.courier_id,
                    r.new_location,
                )
            else:
                logger.info(
                    "Courier '%s' (%s) moved to %s",
                    r.courier_name,
                    r.courier_id,
                    r.new_location,
                )


async def process_outbox_events() -> None:
    async with async_session_maker() as session:
        tracker = RepositoryTracker(session)
        outbox_repository = OutboxRepository(tracker)
        order_events_handler = OrderEventsHandler(
            publisher=KafkaOrderEventsProducer(
                kafka_host=settings.kafka_host,
                topic=settings.kafka_order_changed_topic,
            )
        )

        async with tracker.transaction():
            messages = await outbox_repository.get_unprocessed(limit=OUTBOX_BATCH_SIZE)
            for message in messages:
                try:
                    await order_events_handler.handle(message.event)
                except Exception:
                    logger.exception(
                        "Failed to dispatch outbox event: message_id=%s event_name=%s",
                        message.id,
                        message.event.name,
                    )
                    continue

                await outbox_repository.mark_processed(message.id)
