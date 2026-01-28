from uuid import uuid4

import pytest

from core.domain.model.courier.storage_place import StoragePlace


class TestStoragePlace:
    def test_create_with_invalid_total_volume_failed(self) -> None:
        with pytest.raises(
            ValueError,
            match="Допустимый объём места хранения должен быть больше 0.",
        ):
            StoragePlace(name="Рюкзак", total_volume=0)
        with pytest.raises(
            ValueError,
            match="Допустимый объём места хранения должен быть больше 0.",
        ):
            StoragePlace(name="Рюкзак", total_volume=-1)

    @pytest.mark.parametrize("name", ["", "   "])
    def test_create_with_invalid_name_failed(self, name: str) -> None:
        with pytest.raises(
            ValueError,
            match="Название места хранения не может быть пустым.",
        ):
            StoragePlace(name=name, total_volume=10)

    def test_can_store_and_store_order_success(self) -> None:
        storage_place = StoragePlace(
            name="Рюкзак",
            total_volume=10,
        )

        order_id = uuid4()
        assert storage_place.can_store(volume=5) is True

        storage_place.store(order_id=order_id, volume=5)

        assert storage_place.order_id == order_id
        assert storage_place.is_occupied() is True

    def test_is_occupied_false_for_new_storage_place(self) -> None:
        storage_place = StoragePlace(
            name="Рюкзак",
            total_volume=10,
        )

        assert storage_place.is_occupied() is False

    def test_can_store_with_invalid_volume_failed(self) -> None:
        storage_place = StoragePlace(
            name="Рюкзак",
            total_volume=10,
        )

        with pytest.raises(
            ValueError,
            match="Объём заказа должен быть больше 0.",
        ):
            storage_place.can_store(volume=0)

        with pytest.raises(
            ValueError,
            match="Объём заказа должен быть больше 0.",
        ):
            storage_place.can_store(volume=-1)

    def test_can_store_returns_false_when_volume_too_big(self) -> None:
        storage_place = StoragePlace(
            name="Рюкзак",
            total_volume=10,
        )

        assert storage_place.can_store(volume=11) is False

    def test_store_when_occupied_failed(self) -> None:
        first_order_id = uuid4()
        second_order_id = uuid4()

        storage_place = StoragePlace(
            name="Рюкзак",
            total_volume=10,
        )
        storage_place.store(order_id=first_order_id, volume=5)

        with pytest.raises(
            ValueError,
            match=(
                "Невозможно поместить заказ в место хранения: "
                "место уже занято или объём заказа превышает допустимый."
            ),
        ):
            storage_place.store(order_id=second_order_id, volume=5)

    def test_store_when_volume_too_big_failed(self) -> None:
        storage_place = StoragePlace(
            name="Рюкзак",
            total_volume=10,
        )
        order_id = uuid4()

        with pytest.raises(
            ValueError,
            match=(
                "Невозможно поместить заказ в место хранения: "
                "место уже занято или объём заказа превышает допустимый."
            ),
        ):
            storage_place.store(order_id=order_id, volume=11)

    def test_clear_makes_storage_empty(self) -> None:
        storage_place = StoragePlace(
            name="Рюкзак",
            total_volume=10,
            order_id=uuid4(),
        )

        assert storage_place.is_occupied() is True

        storage_place.clear()

        assert storage_place.order_id is None
        assert storage_place.is_occupied() is False

    def test_equals_compares_by_id(self) -> None:
        storage_place_1 = StoragePlace(
            name="Рюкзак",
            total_volume=10,
        )
        storage_place_2 = StoragePlace(
            name="Багажник",
            total_volume=20,
        )

        assert storage_place_1.equals(storage_place_2) is False
        assert storage_place_1.equals(storage_place_1) is True

    def test_equals_with_non_storage_place_returns_false(self) -> None:
        storage_place = StoragePlace(
            name="Рюкзак",
            total_volume=10,
        )

        assert storage_place.equals(object()) is False

    def test_id_is_generated_and_unique(self) -> None:
        first = StoragePlace(
            name="Рюкзак",
            total_volume=10,
        )
        second = StoragePlace(
            name="Багажник",
            total_volume=20,
        )

        assert first.id is not None
        assert second.id is not None
        assert first.id != second.id
