from uuid import uuid4

import pytest

from core.domain.model.courier.courier import (
    DEFAULT_BAG_NAME,
    DEFAULT_BAG_VOLUME,
    Courier,
)
from core.domain.model.kernel.location import Location


class TestCourier:
    def test_create_courier_with_default_bag(self) -> None:
        courier = Courier(
            name="Иван",
            speed=2,
            location=Location(x=1, y=1),
        )

        assert courier.id is not None
        assert courier.name == "Иван"
        assert courier.speed == 2
        assert courier.location == Location(x=1, y=1)
        assert len(courier.storage_places) == 1
        bag = courier.storage_places[0]
        assert bag.name == DEFAULT_BAG_NAME
        assert bag.total_volume == DEFAULT_BAG_VOLUME
        assert bag.order_id is None

    def test_create_courier_with_invalid_name_failed(self) -> None:
        with pytest.raises(
            ValueError,
            match="Имя курьера не может быть пустым.",
        ):
            Courier(
                name="",
                speed=1,
                location=Location(x=1, y=1),
            )

    def test_create_courier_with_invalid_speed_failed(self) -> None:
        with pytest.raises(
            ValueError,
            match="Скорость курьера должна быть больше 0.",
        ):
            Courier(
                name="Иван",
                speed=0,
                location=Location(x=1, y=1),
            )

    def test_add_storage_place(self) -> None:
        courier = Courier(
            name="Иван",
            speed=2,
            location=Location(x=1, y=1),
        )

        new_place = courier.add_storage_place(name="Багажник", total_volume=20)

        assert new_place in courier.storage_places
        assert new_place.name == "Багажник"
        assert new_place.total_volume == 20

    def test_can_take_order_true_when_space_available(self) -> None:
        courier = Courier(
            name="Иван",
            speed=2,
            location=Location(x=1, y=1),
        )

        assert courier.can_take_order(volume=5) is True

    def test_can_take_order_false_when_no_space(self) -> None:
        courier = Courier(
            name="Иван",
            speed=2,
            location=Location(x=1, y=1),
        )
        # Занимаем базовую сумку полностью
        courier.take_order(order_id=uuid4(), volume=DEFAULT_BAG_VOLUME)

        assert courier.can_take_order(volume=1) is False

    def test_take_order_success(self) -> None:
        courier = Courier(
            name="Иван",
            speed=2,
            location=Location(x=1, y=1),
        )
        order_id = uuid4()

        courier.take_order(order_id=order_id, volume=5)

        assert any(place.order_id == order_id for place in courier.storage_places)

    def test_take_order_failed_when_no_space(self) -> None:
        courier = Courier(
            name="Иван",
            speed=2,
            location=Location(x=1, y=1),
        )
        # Занимаем базовую сумку полностью
        courier.take_order(order_id=uuid4(), volume=DEFAULT_BAG_VOLUME)

        with pytest.raises(
            ValueError,
            match="Курьер не может взять заказ: нет свободного места хранения.",
        ):
            courier.take_order(order_id=uuid4(), volume=1)

    def test_complete_order_clears_storage_place(self) -> None:
        courier = Courier(
            name="Иван",
            speed=2,
            location=Location(x=1, y=1),
        )
        order_id = uuid4()
        courier.take_order(order_id=order_id, volume=5)

        courier.complete_order(order_id=order_id)

        assert all(place.order_id is None for place in courier.storage_places)

    def test_complete_order_with_unknown_id_failed(self) -> None:
        courier = Courier(
            name="Иван",
            speed=2,
            location=Location(x=1, y=1),
        )

        with pytest.raises(
            ValueError,
            match="У курьера нет активного заказа с указанным идентификатором.",
        ):
            courier.complete_order(order_id=uuid4())

    def test_calculate_steps_to_location(self) -> None:
        courier = Courier(
            name="Иван",
            speed=2,
            location=Location(x=1, y=1),
        )
        target = Location(x=5, y=5)

        steps = courier.calculate_steps_to_location(target)

        assert steps == 4

    def test_move_changes_location_within_speed(self) -> None:
        courier = Courier(
            name="Иван",
            speed=2,
            location=Location(x=1, y=1),
        )
        target = Location(x=5, y=5)

        courier.move(target=target)

        # Курьер должен сдвинуться ближе к цели, но не дальше своей скорости.
        assert courier.location != Location(x=1, y=1)
        distance_after_move = courier.location.distance_to(target)
        distance_before_move = Location(x=1, y=1).distance_to(target)
        assert distance_after_move < distance_before_move
        assert (
            Location(x=1, y=1).distance_to(courier.location) <= courier.speed
        )

