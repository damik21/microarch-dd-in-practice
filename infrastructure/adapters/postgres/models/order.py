import uuid

from sqlalchemy import Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.domain.model.order.order import OrderStatus
from infrastructure.adapters.postgres.models.base import Base


class OrderDTO(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    courier_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("couriers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    location_x: Mapped[int] = mapped_column(Integer, nullable=False)
    location_y: Mapped[int] = mapped_column(Integer, nullable=False)
    volume: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(
            OrderStatus, name="order_status", create_constraint=True, native_enum=False
        ),
        nullable=False,
        default=OrderStatus.CREATED,
    )
