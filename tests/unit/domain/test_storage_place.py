from uuid import uuid4

import pytest

from core.domain.exceptions.courier import OrderVolumeIncorrect
from core.domain.exceptions.storage_place import (
    StorageCannotStoreOrder,
    StoragePlaceNameIncorrect,
    StoragePlaceTotalValueIncorrect,
)
from core.domain.model.courier.storage_place import StoragePlace


class TestStoragePlace:
    def test_create_with_invalid_total_volume_failed(self) -> None:
        with pytest.raises(
            StoragePlaceTotalValueIncorrect,
            match="Допустимый объём места хранения должен быть больше 0.",
        ):
            StoragePlace.create(name="Рюкзак", total_volume=0)
        with pytest.raises(
            StoragePlaceTotalValueIncorrect,
            match="Допустимый объём места хранения должен быть больше 0.",
        ):
            StoragePlace.create(name="Рюкзак", total_volume=-1)

    def test_create_with_invalid_name_failed(self) -> None:
        with pytest.raises(
            StoragePlaceNameIncorrect,
            match="Название места хранения не может быть пустым.",
        ):
            StoragePlace.create(name="", total_volume=10)

    def test_can_store_and_store_order_success(self) -> None:
        storage_place = StoragePlace.create(
            name="Рюкзак",
            total_volume=10,
        )

        order_id = uuid4()
        assert storage_place.can_store(volume=5) is True

        storage_place.store(order_id=order_id, volume=5)

        assert storage_place.order_id == order_id
        assert storage_place.is_occupied() is True

    def test_is_occupied_false_for_new_storage_place(self) -> None:
        storage_place = StoragePlace.create(
            name="Рюкзак",
            total_volume=10,
        )

        assert storage_place.is_occupied() is False

    def test_can_store_with_invalid_volume_failed(self) -> None:
        storage_place = StoragePlace.create(
            name="Рюкзак",
            total_volume=10,
        )

        with pytest.raises(
            OrderVolumeIncorrect,
            match="Объём заказа должен быть больше 0.",
        ):
            storage_place.can_store(volume=0)

    def test_can_store_returns_false_when_volume_too_big(self) -> None:
        storage_place = StoragePlace.create(
            name="Рюкзак",
            total_volume=10,
        )

        assert storage_place.can_store(volume=11) is False

    def test_store_when_occupied_failed(self) -> None:
        first_order_id = uuid4()
        second_order_id = uuid4()

        storage_place = StoragePlace.create(
            name="Рюкзак",
            total_volume=10,
        )
        storage_place.store(order_id=first_order_id, volume=5)

        with pytest.raises(
            StorageCannotStoreOrder,
            match=(
                "Невозможно поместить заказ в место хранения: "
                "место уже занято или объём заказа превышает допустимый."
            ),
        ):
            storage_place.store(order_id=second_order_id, volume=5)

    def test_store_when_volume_too_big_failed(self) -> None:
        storage_place = StoragePlace.create(
            name="Рюкзак",
            total_volume=10,
        )
        order_id = uuid4()

        with pytest.raises(
            StorageCannotStoreOrder,
            match=(
                "Невозможно поместить заказ в место хранения: "
                "место уже занято или объём заказа превышает допустимый."
            ),
        ):
            storage_place.store(order_id=order_id, volume=11)

    def test_clear_makes_storage_empty(self) -> None:
        storage_place = StoragePlace.create(
            name="Рюкзак",
            total_volume=10,
            order_id=uuid4(),
        )

        assert storage_place.is_occupied() is True

        storage_place.clear()

        assert storage_place.order_id is None
        assert storage_place.is_occupied() is False

    def test_equals_compares_by_id(self) -> None:
        storage_place_1 = StoragePlace.create(
            name="Рюкзак",
            total_volume=10,
        )
        storage_place_2 = StoragePlace.create(
            name="Багажник",
            total_volume=20,
        )

        assert storage_place_1.equals(storage_place_2) is False
        assert storage_place_1.equals(storage_place_1) is True
