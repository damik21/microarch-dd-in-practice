from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from core.application.use_cases.commands.create_order import (
    CreateOrderCommand,
    CreateOrderHandler,
)
from core.domain.model.kernel.location import Location
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
def geo_service_client() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def tracker() -> MockTracker:
    return MockTracker()


@pytest.fixture
def handler(
    order_repository: AsyncMock,
    geo_service_client: AsyncMock,
    tracker: MockTracker,
) -> CreateOrderHandler:
    return CreateOrderHandler(
        order_repository=order_repository,
        tracker=tracker,
        geo_service_client=geo_service_client,
    )


@pytest.mark.asyncio
async def test_create_order_uses_geo_service(
    handler: CreateOrderHandler,
    order_repository: AsyncMock,
    geo_service_client: AsyncMock,
) -> None:
    geo_service_client.get_location.return_value = Location(x=1, y=1)
    command = CreateOrderCommand(order_id=uuid4(), street="Тестировочная", volume=5)

    await handler.handle(command)

    geo_service_client.get_location.assert_called_once_with("Тестировочная")
    order_repository.add.assert_called_once()
    added_order = order_repository.add.call_args[0][0]
    assert added_order.location == Location(x=1, y=1)


@pytest.mark.asyncio
async def test_create_order_different_streets_give_different_locations(
    handler: CreateOrderHandler,
    order_repository: AsyncMock,
    geo_service_client: AsyncMock,
) -> None:
    geo_service_client.get_location.side_effect = [
        Location(x=3, y=4),
        Location(x=7, y=2),
    ]

    command_1 = CreateOrderCommand(order_id=uuid4(), street="Улица 1", volume=3)
    command_2 = CreateOrderCommand(order_id=uuid4(), street="Улица 2", volume=3)

    await handler.handle(command_1)
    order_1 = order_repository.add.call_args_list[0][0][0]

    await handler.handle(command_2)
    order_2 = order_repository.add.call_args_list[1][0][0]

    assert order_1.location == Location(x=3, y=4)
    assert order_2.location == Location(x=7, y=2)
    assert order_1.location != order_2.location


@pytest.mark.asyncio
async def test_create_order_passes_volume_to_order(
    handler: CreateOrderHandler,
    order_repository: AsyncMock,
    geo_service_client: AsyncMock,
) -> None:
    geo_service_client.get_location.return_value = Location(x=5, y=5)
    command = CreateOrderCommand(order_id=uuid4(), street="Любая улица", volume=8)

    await handler.handle(command)

    added_order = order_repository.add.call_args[0][0]
    assert added_order.volume == 8
