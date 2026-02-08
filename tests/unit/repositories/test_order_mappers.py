from uuid import uuid4

from core.domain.model.kernel.location import Location
from core.domain.model.order.order import Order, OrderStatus
from infrastructure.adapters.postgres.models.order import OrderDTO
from infrastructure.adapters.postgres.repositories.order_repository import (
    domain_to_dto,
    dto_to_domain,
)


class TestOrderMappers:
    def test_domain_to_dto_new_order(self) -> None:
        order_id = uuid4()
        location = Location(x=5, y=3)
        order = Order.create(id=order_id, location=location, volume=2)

        dto = domain_to_dto(order)

        assert isinstance(dto, OrderDTO)
        assert dto.id == order_id
        assert dto.courier_id is None
        assert dto.location_x == 5
        assert dto.location_y == 3
        assert dto.volume == 2
        assert dto.status == OrderStatus.CREATED

    def test_domain_to_dto_assigned_order(self) -> None:
        order_id = uuid4()
        location = Location(x=2, y=7)
        order = Order.create(id=order_id, location=location, volume=3)
        courier_id = uuid4()
        order.assign(courier_id)

        dto = domain_to_dto(order)

        assert isinstance(dto, OrderDTO)
        assert dto.id == order_id
        assert dto.courier_id == courier_id
        assert dto.location_x == 2
        assert dto.location_y == 7
        assert dto.volume == 3
        assert dto.status == OrderStatus.ASSIGNED

    def test_domain_to_dto_completed_order(self) -> None:
        order_id = uuid4()
        location = Location(x=1, y=1)
        order = Order.create(id=order_id, location=location, volume=1)
        courier_id = uuid4()
        order.assign(courier_id)
        order.complete()

        dto = domain_to_dto(order)

        assert isinstance(dto, OrderDTO)
        assert dto.id == order_id
        assert dto.courier_id == courier_id
        assert dto.status == OrderStatus.COMPLETED

    def test_dto_to_domain_created_order(self) -> None:
        order_id = uuid4()
        dto = OrderDTO(
            id=order_id,
            courier_id=None,
            location_x=3,
            location_y=8,
            volume=5,
            status=OrderStatus.CREATED,
        )

        order = dto_to_domain(dto)

        assert isinstance(order, Order)
        assert order.id == order_id
        assert order.courier_id is None
        assert order.location.x == 3
        assert order.location.y == 8
        assert order.volume == 5
        assert order.status == OrderStatus.CREATED

    def test_dto_to_domain_assigned_order(self) -> None:
        order_id = uuid4()
        courier_id = uuid4()
        dto = OrderDTO(
            id=order_id,
            courier_id=courier_id,
            location_x=10,
            location_y=2,
            volume=3,
            status=OrderStatus.ASSIGNED,
        )

        order = dto_to_domain(dto)

        assert isinstance(order, Order)
        assert order.id == order_id
        assert order.courier_id == courier_id
        assert order.status == OrderStatus.ASSIGNED

    def test_roundtrip_mapping(self) -> None:
        order_id = uuid4()
        location = Location(x=4, y=6)
        original_order = Order.create(id=order_id, location=location, volume=4)
        courier_id = uuid4()
        original_order.assign(courier_id)

        dto = domain_to_dto(original_order)
        restored_order = dto_to_domain(dto)

        assert restored_order.id == original_order.id
        assert restored_order.courier_id == original_order.courier_id
        assert restored_order.location == original_order.location
        assert restored_order.volume == original_order.volume
        assert restored_order.status == original_order.status
