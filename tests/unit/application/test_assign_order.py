from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from core.application.use_cases.commands.assign_order import AssignOrderHandler
from core.domain.model.courier.courier import Courier
from core.domain.model.kernel.location import Location
from core.domain.model.order.order import Order
from infrastructure.adapters.postgres.repositories.tracker import Tracker


class MockTracker(Tracker):
    def tx(self):
        return None

    def db(self):
        return None

    def in_tx(self):
        return False

    def track(self, aggregate):
        pass

    async def begin(self) -> None:
        pass

    async def commit(self) -> None:
        pass

    async def rollback(self) -> None:
        pass


@pytest.fixture
def order_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def courier_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def dispatcher() -> MagicMock:
    return MagicMock()


@pytest.fixture
def tracker() -> MockTracker:
    return MockTracker()


@pytest.fixture
def handler(
    order_repository: AsyncMock,
    courier_repository: AsyncMock,
    dispatcher: MagicMock,
    tracker: MockTracker,
) -> AssignOrderHandler:
    return AssignOrderHandler(
        order_repository=order_repository,
        courier_repository=courier_repository,
        dispatcher=dispatcher,
        tracker=tracker,
    )


@pytest.mark.asyncio
async def test_assign_order_success(
    handler: AssignOrderHandler,
    order_repository: AsyncMock,
    courier_repository: AsyncMock,
    dispatcher: MagicMock,
    tracker: MockTracker,
) -> None:
    order = Order.create(id=uuid4(), location=Location(x=5, y=5), volume=5)
    courier = Courier.create(name="Иван", speed=3, location=Location(x=1, y=1))

    order_repository.get_first_created.return_value = order
    courier_repository.get_all_free.return_value = [courier]
    dispatcher.dispatch.return_value = courier

    with (
        patch.object(tracker, "begin", wraps=tracker.begin) as mock_begin,
        patch.object(tracker, "commit", wraps=tracker.commit) as mock_commit,
    ):
        await handler.handle()

        mock_begin.assert_called_once()
        mock_commit.assert_called_once()

    dispatcher.dispatch.assert_called_once_with(order, [courier])
    order_repository.update.assert_called_once_with(order)
    courier_repository.update.assert_called_once_with(courier)


@pytest.mark.asyncio
async def test_assign_order_no_created_orders(
    handler: AssignOrderHandler,
    order_repository: AsyncMock,
    courier_repository: AsyncMock,
    dispatcher: MagicMock,
) -> None:
    order_repository.get_first_created.return_value = None

    await handler.handle()

    courier_repository.get_all_free.assert_not_called()
    dispatcher.dispatch.assert_not_called()


@pytest.mark.asyncio
async def test_assign_order_no_free_couriers(
    handler: AssignOrderHandler,
    order_repository: AsyncMock,
    courier_repository: AsyncMock,
    dispatcher: MagicMock,
) -> None:
    order = Order.create(id=uuid4(), location=Location(x=5, y=5), volume=5)
    order_repository.get_first_created.return_value = order
    courier_repository.get_all_free.return_value = []

    await handler.handle()

    dispatcher.dispatch.assert_not_called()


@pytest.mark.asyncio
async def test_assign_order_dispatcher_returns_none(
    handler: AssignOrderHandler,
    order_repository: AsyncMock,
    courier_repository: AsyncMock,
    dispatcher: MagicMock,
    tracker: MockTracker,
) -> None:
    order = Order.create(id=uuid4(), location=Location(x=5, y=5), volume=5)
    courier = Courier.create(name="Иван", speed=3, location=Location(x=1, y=1))

    order_repository.get_first_created.return_value = order
    courier_repository.get_all_free.return_value = [courier]
    dispatcher.dispatch.return_value = None

    await handler.handle()

    order_repository.update.assert_not_called()


@pytest.mark.asyncio
async def test_assign_order_rollback_on_error(
    handler: AssignOrderHandler,
    order_repository: AsyncMock,
    courier_repository: AsyncMock,
    dispatcher: MagicMock,
    tracker: MockTracker,
) -> None:
    order = Order.create(id=uuid4(), location=Location(x=5, y=5), volume=5)
    courier = Courier.create(name="Иван", speed=3, location=Location(x=1, y=1))

    order_repository.get_first_created.return_value = order
    courier_repository.get_all_free.return_value = [courier]
    dispatcher.dispatch.return_value = courier
    order_repository.update.side_effect = RuntimeError("DB error")

    with patch.object(tracker, "rollback", wraps=tracker.rollback) as mock_rollback:
        with pytest.raises(RuntimeError, match="DB error"):
            await handler.handle()

        mock_rollback.assert_called_once()
