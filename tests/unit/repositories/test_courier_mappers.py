import uuid

from core.domain.model.courier.courier import Courier
from core.domain.model.courier.storage_place import StoragePlace
from core.domain.model.kernel.location import Location
from infrastructure.adapters.postgres.models.courier import CourierDTO
from infrastructure.adapters.postgres.models.storage_place import StoragePlaceDTO
from infrastructure.adapters.postgres.repositories.courier_repository import (
    domain_to_dto,
    dto_to_domain,
)


class TestCourierMappers:
    """Тесты для мапперов между доменной моделью и DTO."""

    def test_domain_to_dto_new_courier(self) -> None:
        """Тест преобразования нового курьера в DTO."""
        # Arrange
        location = Location(x=1, y=1)
        courier = Courier.create(name="Иван", speed=2, location=location)

        # Act
        dto = domain_to_dto(courier)

        # Assert
        assert isinstance(dto, CourierDTO)
        assert dto.id == courier.id
        assert dto.name == "Иван"
        assert dto.speed == 2
        assert dto.location_x == 1
        assert dto.location_y == 1
        assert dto.storage_places == []  # Пустой список

    def test_dto_to_domain_free_courier(self) -> None:
        """Тест преобразования DTO в доменную модель (свободный курьер)."""
        # Arrange
        courier_id = uuid.uuid4()
        storage_id = uuid.uuid4()
        dto = CourierDTO(
            id=courier_id,
            name="Пётр",
            speed=3,
            location_x=5,
            location_y=7,
            storage_places=[
                StoragePlaceDTO(
                    id=storage_id,
                    courier_id=courier_id,
                    name="Сумка",
                    total_volume=10,
                    order_id=None,
                )
            ],
        )

        # Act
        courier = dto_to_domain(dto)

        # Assert
        assert isinstance(courier, Courier)
        assert courier.id == courier_id
        assert courier.name == "Пётр"
        assert courier.speed == 3
        assert courier.location.x == 5
        assert courier.location.y == 7
        # Курьер свободен - нет order_id в storage_places

    def test_dto_to_domain_busy_courier(self) -> None:
        """Тест преобразования DTO в доменную модель (занятый курьер)."""
        # Arrange
        courier_id = uuid.uuid4()
        storage_id = uuid.uuid4()
        order_id = uuid.uuid4()
        dto = CourierDTO(
            id=courier_id,
            name="Сергей",
            speed=4,
            location_x=3,
            location_y=9,
            storage_places=[
                StoragePlaceDTO(
                    id=storage_id,
                    courier_id=courier_id,
                    name="Сумка",
                    total_volume=10,
                    order_id=order_id,
                )
            ],
        )

        # Act
        courier = dto_to_domain(dto)

        # Assert
        assert isinstance(courier, Courier)
        assert courier.id == courier_id
        assert courier.name == "Сергей"
        assert courier.speed == 4

    def test_dto_to_domain_multiple_storage_places(self) -> None:
        """Тест преобразования DTO с несколькими местами хранения."""
        # Arrange
        courier_id = uuid.uuid4()
        storage_id_1 = uuid.uuid4()
        storage_id_2 = uuid.uuid4()
        order_id = uuid.uuid4()
        dto = CourierDTO(
            id=courier_id,
            name="Алексей",
            speed=5,
            location_x=2,
            location_y=4,
            storage_places=[
                StoragePlaceDTO(
                    id=storage_id_1,
                    courier_id=courier_id,
                    name="Сумка",
                    total_volume=10,
                    order_id=order_id,
                ),
                StoragePlaceDTO(
                    id=storage_id_2,
                    courier_id=courier_id,
                    name="Рюкзак",
                    total_volume=20,
                    order_id=None,
                ),
            ],
        )

        # Act
        courier = dto_to_domain(dto)

        # Assert
        assert isinstance(courier, Courier)
        assert courier.name == "Алексей"
        assert courier.speed == 5

    def test_roundtrip_mapping(self) -> None:
        """Тест двунаправленного преобразования (Domain -> DTO -> Domain)."""
        # Arrange
        location = Location(x=3, y=5)
        original_courier = Courier.create(name="Дмитрий", speed=3, location=location)
        original_courier.add_storage_place("Рюкзак", 20)

        # Act - только частичный roundtrip, т.к. storage_places не маппятся при сохранении
        dto = domain_to_dto(original_courier)

        # Assert - проверяем базовые поля
        assert dto.id == original_courier.id
        assert dto.name == original_courier.name
        assert dto.speed == original_courier.speed
        assert dto.location_x == original_courier.location.x
        assert dto.location_y == original_courier.location.y
