from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.application.use_cases.commands.add_storage_place import AddStoragePlaceHandler
from core.application.use_cases.commands.assign_order import AssignOrderHandler
from core.application.use_cases.commands.create_courier import CreateCourierHandler
from core.application.use_cases.commands.create_order import CreateOrderHandler
from core.application.use_cases.commands.move_couriers import MoveCouriersHandler
from core.application.use_cases.queries.get_active_orders import GetActiveOrdersHandler
from core.application.use_cases.queries.get_couriers import GetCouriersHandler
from core.domain.services import OrderDispatcher
from core.ports import OrderDispatcherInterface
from infrastructure.adapters.postgres.repositories.base import RepositoryTracker
from infrastructure.adapters.postgres.repositories.courier_repository import (
    CourierRepository,
)
from infrastructure.adapters.postgres.repositories.order_repository import (
    OrderRepository,
)
from infrastructure.adapters.postgres.repositories.tracker import Tracker
from infrastructure.db import async_session_maker


def get_order_dispatcher() -> OrderDispatcherInterface:
    return OrderDispatcher()


async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_maker() as session:
        yield session


async def get_tracker(session: AsyncSession = Depends(get_session)) -> Tracker:
    return RepositoryTracker(session)


async def get_create_order_handler(
    tracker: Tracker = Depends(get_tracker),
) -> CreateOrderHandler:
    return CreateOrderHandler(
        order_repository=OrderRepository(tracker), tracker=tracker
    )


async def get_create_courier_handler(
    tracker: Tracker = Depends(get_tracker),
) -> CreateCourierHandler:
    return CreateCourierHandler(
        courier_repository=CourierRepository(tracker), tracker=tracker
    )


async def get_add_storage_place_handler(
    tracker: Tracker = Depends(get_tracker),
) -> AddStoragePlaceHandler:
    return AddStoragePlaceHandler(
        courier_repository=CourierRepository(tracker), tracker=tracker
    )


async def get_assign_order_handler(
    tracker: Tracker = Depends(get_tracker),
    dispatcher: OrderDispatcherInterface = Depends(get_order_dispatcher),
) -> AssignOrderHandler:
    return AssignOrderHandler(
        order_repository=OrderRepository(tracker),
        courier_repository=CourierRepository(tracker),
        dispatcher=dispatcher,
        tracker=tracker,
    )


async def get_move_couriers_handler(
    tracker: Tracker = Depends(get_tracker),
) -> MoveCouriersHandler:
    return MoveCouriersHandler(
        order_repository=OrderRepository(tracker),
        courier_repository=CourierRepository(tracker),
        tracker=tracker,
    )


async def get_get_couriers_handler(
    tracker: Tracker = Depends(get_tracker),
) -> GetCouriersHandler:
    return GetCouriersHandler(courier_repository=CourierRepository(tracker))


async def get_get_active_orders_handler(
    tracker: Tracker = Depends(get_tracker),
) -> GetActiveOrdersHandler:
    return GetActiveOrdersHandler(order_repository=OrderRepository(tracker))
