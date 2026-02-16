from typing import Any
from uuid import uuid4

import pytest

from core.domain.model.kernel.location import Location
from core.domain.model.order.order import Order, OrderStatus
from infrastructure.adapters.postgres.repositories.order_repository import (
    OrderRepository,
)


class TestOrderRepository:
    @pytest.mark.asyncio
    async def test_add_order(self, tracker: Any) -> None:
        location = Location(x=3, y=5)
        order_id = uuid4()
        order = Order.create(id=order_id, location=location, volume=2)
        repository = OrderRepository(tracker)

        await repository.add(order)

        from sqlalchemy import select

        from infrastructure.adapters.postgres.models.order import OrderDTO

        session = tracker.db()
        stmt = select(OrderDTO).where(OrderDTO.id == order.id)
        result = await session.execute(stmt)
        dto = result.scalar_one_or_none()

        assert dto is not None
        assert dto.id == order.id
        assert dto.courier_id is None
        assert dto.location_x == 3
        assert dto.location_y == 5
        assert dto.volume == 2
        assert dto.status == OrderStatus.CREATED

    @pytest.mark.asyncio
    async def test_get_by_id_existing_order(self, tracker: Any) -> None:
        location = Location(x=1, y=10)
        order = Order.create(id=uuid4(), location=location, volume=5)
        repository = OrderRepository(tracker)
        await repository.add(order)

        found_order = await repository.get_by_id(str(order.id))

        assert found_order is not None
        assert found_order.id == order.id
        assert found_order.location == location
        assert found_order.volume == 5
        assert found_order.status == OrderStatus.CREATED

    @pytest.mark.asyncio
    async def test_get_by_id_non_existing_order(self, tracker: Any) -> None:
        repository = OrderRepository(tracker)
        found_order = await repository.get_by_id(str(uuid4()))
        assert found_order is None

    @pytest.mark.asyncio
    async def test_update_order_status(self, tracker: Any) -> None:
        from core.domain.model.courier.courier import Courier
        from infrastructure.adapters.postgres.repositories.courier_repository import (
            CourierRepository,
        )

        courier_repo = CourierRepository(tracker)
        order_repo = OrderRepository(tracker)

        courier = Courier.create(name="Тест", speed=2, location=Location(x=1, y=1))
        await courier_repo.add(courier)

        location = Location(x=5, y=2)
        order = Order.create(id=uuid4(), location=location, volume=3)
        await order_repo.add(order)

        order.assign(courier.id)
        await order_repo.update(order)

        found_order = await order_repo.get_by_id(str(order.id))

        assert found_order is not None
        assert found_order.status == OrderStatus.ASSIGNED
        assert found_order.courier_id == courier.id

    @pytest.mark.asyncio
    async def test_get_first_created_when_exists(self, tracker: Any) -> None:
        repository = OrderRepository(tracker)

        order1 = Order.create(id=uuid4(), location=Location(x=1, y=1), volume=1)
        await repository.add(order1)

        order2 = Order.create(id=uuid4(), location=Location(x=2, y=2), volume=2)
        await repository.add(order2)

        found_order = await repository.get_first_created()

        assert found_order is not None
        assert found_order.status == OrderStatus.CREATED

    @pytest.mark.asyncio
    async def test_get_first_created_when_none(self, tracker: Any) -> None:
        repository = OrderRepository(tracker)
        found_order = await repository.get_first_created()
        assert found_order is None

    @pytest.mark.asyncio
    async def test_get_all_assigned(self, tracker: Any) -> None:
        from core.domain.model.courier.courier import Courier
        from infrastructure.adapters.postgres.repositories.courier_repository import (
            CourierRepository,
        )

        courier_repo = CourierRepository(tracker)
        order_repo = OrderRepository(tracker)

        courier = Courier.create(name="Тест", speed=2, location=Location(x=1, y=1))
        await courier_repo.add(courier)

        order1 = Order.create(id=uuid4(), location=Location(x=1, y=1), volume=1)
        await order_repo.add(order1)

        order2 = Order.create(id=uuid4(), location=Location(x=2, y=2), volume=2)
        order2.assign(courier.id)
        await order_repo.add(order2)

        order3 = Order.create(id=uuid4(), location=Location(x=3, y=3), volume=3)
        order3.assign(courier.id)
        await order_repo.add(order3)

        assigned_orders = await order_repo.get_all_assigned()

        assert len(assigned_orders) == 2
        assert all(o.status == OrderStatus.ASSIGNED for o in assigned_orders)

    @pytest.mark.asyncio
    async def test_get_all_assigned_when_none(self, tracker: Any) -> None:
        repository = OrderRepository(tracker)
        assigned_orders = await repository.get_all_assigned()
        assert assigned_orders == []

    @pytest.mark.asyncio
    async def test_complete_order(self, tracker: Any) -> None:
        from core.domain.model.courier.courier import Courier
        from infrastructure.adapters.postgres.repositories.courier_repository import (
            CourierRepository,
        )

        courier_repo = CourierRepository(tracker)
        order_repo = OrderRepository(tracker)

        courier = Courier.create(name="Тест", speed=2, location=Location(x=1, y=1))
        await courier_repo.add(courier)

        location = Location(x=4, y=6)
        order = Order.create(id=uuid4(), location=location, volume=4)
        order.assign(courier.id)
        await order_repo.add(order)

        order.complete()
        await order_repo.update(order)

        found_order = await order_repo.get_by_id(str(order.id))
        assert found_order is not None
        assert found_order.status == OrderStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_add_multiple_orders(self, tracker: Any) -> None:
        repository = OrderRepository(tracker)

        orders = [
            Order.create(id=uuid4(), location=Location(x=i, y=i), volume=i)
            for i in range(1, 4)
        ]

        for order in orders:
            await repository.add(order)

        from sqlalchemy import select

        from infrastructure.adapters.postgres.models.order import OrderDTO

        session = tracker.db()
        stmt = select(OrderDTO)
        result = await session.execute(stmt)
        dtos = result.scalars().all()

        assert len(dtos) == 3

    @pytest.mark.asyncio
    async def test_update_order_volume(self, tracker: Any) -> None:
        location = Location(x=7, y=3)
        order = Order.create(id=uuid4(), location=location, volume=2)
        repository = OrderRepository(tracker)
        await repository.add(order)

        order._Order__volume = 5  # type: ignore[attr-defined]
        await repository.update(order)

        found_order = await repository.get_by_id(str(order.id))
        assert found_order is not None
        assert found_order.volume == 5
