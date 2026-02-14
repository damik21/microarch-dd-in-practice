import asyncio
import logging
from collections.abc import Callable, Coroutine
from typing import Any

from core.application.use_cases.commands.assign_order import AssignOrderHandler
from core.application.use_cases.commands.move_couriers import MoveCouriersHandler
from core.domain.services import OrderDispatcher
from infrastructure.adapters.postgres.repositories.base import RepositoryTracker
from infrastructure.adapters.postgres.repositories.courier_repository import (
    CourierRepository,
)
from infrastructure.adapters.postgres.repositories.order_repository import (
    OrderRepository,
)
from infrastructure.db import async_session_maker

logger = logging.getLogger(__name__)


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
