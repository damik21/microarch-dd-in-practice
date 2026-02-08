from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.adapters.postgres.models.base import Base

if TYPE_CHECKING:
    from infrastructure.adapters.postgres.models.storage_place import StoragePlaceDTO


class CourierDTO(Base):  # type: ignore[misc]
    __tablename__ = "couriers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    speed: Mapped[int] = mapped_column(Integer, nullable=False)
    location_x: Mapped[int] = mapped_column(Integer, nullable=False)
    location_y: Mapped[int] = mapped_column(Integer, nullable=False)

    storage_places: Mapped[list[StoragePlaceDTO]] = relationship(
        "StoragePlaceDTO",
        back_populates="courier",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
