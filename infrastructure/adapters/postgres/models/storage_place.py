from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.adapters.postgres.models.base import Base

if TYPE_CHECKING:
    from infrastructure.adapters.postgres.models.courier import CourierDTO


class StoragePlaceDTO(Base):  # type: ignore[misc]
    __tablename__ = "storage_places"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    courier_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("couriers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    total_volume: Mapped[int] = mapped_column(Integer, nullable=False)
    order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        default=None,
    )

    courier: Mapped["CourierDTO"] = relationship(
        "CourierDTO",
        back_populates="storage_places",
    )
