"""Модель сообщения outbox."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class OutboxMessage(Base):
    """
    Модель сообщения outbox для транзакционной рассылки событий.

    Attributes:
        id: Уникальный идентификатор сообщения.
        name: Имя типа доменного события.
        payload: JSON payload события.
        occurred_at_utc: Время возникновения события (UTC).
        processed_at_utc: Время обработки сообщения (UTC). None, если ещё не обработано.
    """

    __tablename__ = "outbox"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    occurred_at_utc: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    processed_at_utc: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
