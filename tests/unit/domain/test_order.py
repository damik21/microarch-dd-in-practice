from uuid import uuid4

import pytest

from core.domain.model.kernel.location import Location
from core.domain.model.order.order import Order, OrderStatus


class TestOrder:
    def test_create_order_with_valid_data(self) -> None:
        order_id = uuid4()
        location = Location(x=1, y=1)

        order = Order(id=order_id, location=location, volume=5)

        assert order.id == order_id
        assert order.location == location
        assert order.volume == 5
        assert order.courier_id is None
        assert order.status is OrderStatus.CREATED
        
    def test_create_order_with_invalid_volume_failed(self) -> None:
        order_id = uuid4()
        location = Location(x=1, y=1)

        with pytest.raises(
            ValueError,
            match="Объём заказа должен быть больше 0.",
        ):
            Order(id=order_id, location=location, volume=0)

    def test_assign_sets_courier_and_status(self) -> None:
        order = Order(id=uuid4(), location=Location(x=1, y=1), volume=5)
        courier_id = uuid4()

        order.assign(courier_id=courier_id)

        assert order.courier_id == courier_id
        assert order.status is OrderStatus.ASSIGNED

    def test_assign_twice_failed(self) -> None:
        order = Order(id=uuid4(), location=Location(x=1, y=1), volume=5)
        courier_id = uuid4()
        order.assign(courier_id=courier_id)

        with pytest.raises(
            ValueError,
            match="Заказ уже назначен на курьера.",
        ):
            order.assign(courier_id=uuid4())

    def test_assign_completed_order_failed(self) -> None:
        order = Order(id=uuid4(), location=Location(x=1, y=1), volume=5)
        courier_id = uuid4()
        order.assign(courier_id=courier_id)
        order.complete()

        with pytest.raises(
            ValueError,
            match="Нельзя назначить завершённый заказ.",
        ):
            order.assign(courier_id=uuid4())

    def test_complete_assigned_order_success(self) -> None:
        order = Order(id=uuid4(), location=Location(x=1, y=1), volume=5)
        courier_id = uuid4()
        order.assign(courier_id=courier_id)

        order.complete()

        assert order.status is OrderStatus.COMPLETED

    def test_complete_not_assigned_order_failed(self) -> None:
        order = Order(id=uuid4(), location=Location(x=1, y=1), volume=5)

        with pytest.raises(
            ValueError,
            match="Завершить можно только назначенный заказ.",
        ):
            order.complete()

