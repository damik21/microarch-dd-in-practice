from uuid import uuid4

import pytest

from core.domain.model.courier.courier import Courier, DEFAULT_BAG_VOLUME
from core.domain.model.kernel.location import Location
from core.domain.model.order.order import Order, OrderStatus
from core.domain.services.order_dispatcher import OrderDispatcher


class TestOrderDispatcher:
    def test_dispatch_selects_fastest_courier(self) -> None:
        order = Order(id=uuid4(), location=Location(x=5, y=5), volume=5)

        # Курьер ближе к заказу (меньше шагов)
        close_courier = Courier.create(
            name="Близкий",
            speed=1,
            location=Location(x=4, y=4),  # Расстояние: 2, шагов: 2
        )
        # Курьер дальше от заказа
        far_courier = Courier.create(
            name="Далёкий",
            speed=1,
            location=Location(x=1, y=1),  # Расстояние: 8, шагов: 8
        )

        dispatcher = OrderDispatcher()


        result = dispatcher.dispatch(order, [far_courier, close_courier])


        assert result is not None
        assert result.id == close_courier.id
        assert order.status == OrderStatus.ASSIGNED
        assert order.courier_id == close_courier.id

    def test_dispatch_considers_courier_speed(self) -> None:
        order = Order(id=uuid4(), location=Location(x=10, y=10), volume=3)

        # Быстрый курьер дальше, но доставит быстрее
        fast_courier = Courier.create(
            name="Быстрый",
            speed=5,
            location=Location(x=1, y=1),  # Расстояние: 18, шагов: 4
        )
        # Медленный курьер ближе, но доставит дольше
        slow_courier = Courier.create(
            name="Медленный",
            speed=1,
            location=Location(x=5, y=5),  # Расстояние: 10, шагов: 10
        )

        dispatcher = OrderDispatcher()


        result = dispatcher.dispatch(order, [slow_courier, fast_courier])


        assert result is not None
        assert result.id == fast_courier.id

    def test_dispatch_returns_none_when_no_couriers(self) -> None:
        order = Order(id=uuid4(), location=Location(x=5, y=5), volume=5)
        dispatcher = OrderDispatcher()


        result = dispatcher.dispatch(order, [])


        assert result is None
        assert order.status == OrderStatus.CREATED

    def test_dispatch_returns_none_when_no_courier_can_take_order(self) -> None:
        order = Order(id=uuid4(), location=Location(x=5, y=5), volume=15)

        courier = Courier.create(
            name="Курьер",
            speed=2,
            location=Location(x=1, y=1),
        )  # Сумка вмещает только 10

        dispatcher = OrderDispatcher()


        result = dispatcher.dispatch(order, [courier])


        assert result is None
        assert order.status == OrderStatus.CREATED

    def test_dispatch_skips_occupied_couriers(self) -> None:
        order = Order(id=uuid4(), location=Location(x=5, y=5), volume=5)

        # Занятый курьер (ближе к заказу)
        occupied_courier = Courier.create(
            name="Занятый",
            speed=1,
            location=Location(x=5, y=4),  # Расстояние: 1
        )
        occupied_courier.take_order(order_id=uuid4(), volume=DEFAULT_BAG_VOLUME)

        # Свободный курьер (дальше от заказа)
        free_courier = Courier.create(
            name="Свободный",
            speed=1,
            location=Location(x=1, y=1),  # Расстояние: 8
        )

        dispatcher = OrderDispatcher()


        result = dispatcher.dispatch(order, [occupied_courier, free_courier])


        assert result is not None
        assert result.id == free_courier.id

    def test_dispatch_assigns_courier_to_order(self) -> None:
        order = Order(id=uuid4(), location=Location(x=5, y=5), volume=5)
        courier = Courier.create(
            name="Курьер",
            speed=2,
            location=Location(x=1, y=1),
        )

        dispatcher = OrderDispatcher()


        result = dispatcher.dispatch(order, [courier])


        assert result is not None
        assert order.courier_id == courier.id
        assert order.status == OrderStatus.ASSIGNED

    def test_dispatch_courier_takes_order(self) -> None:
        order = Order(id=uuid4(), location=Location(x=5, y=5), volume=5)
        courier = Courier.create(
            name="Курьер",
            speed=2,
            location=Location(x=1, y=1),
        )

        dispatcher = OrderDispatcher()


        dispatcher.dispatch(order, [courier])


        storage_places = courier._Courier__storage_places
        assert any(place.order_id == order.id for place in storage_places)

    def test_dispatch_with_multiple_eligible_couriers_equal_distance(self) -> None:
        order = Order(id=uuid4(), location=Location(x=5, y=5), volume=3)

        courier1 = Courier.create(
            name="Первый",
            speed=1,
            location=Location(x=3, y=5),  # Расстояние: 2
        )
        courier2 = Courier.create(
            name="Второй",
            speed=1,
            location=Location(x=5, y=3),  # Расстояние: 2
        )

        dispatcher = OrderDispatcher()


        result = dispatcher.dispatch(order, [courier1, courier2])

        assert result is not None
        # Один из курьеров должен быть выбран
        assert result.id in [courier1.id, courier2.id]
        assert order.status == OrderStatus.ASSIGNED
