"""Регистрация и декодирование доменных событий для outbox."""

import json
from typing import Type

from app.domain.events.base import DomainEvent
from app.domain.exceptions import ValueIsRequiredError
from app.infrastructure.outbox.message import OutboxMessage


class EventRegistry:
    """
    Реестр доменных событий для outbox паттерна.

    Позволяет регистрировать типы событий и декодировать их из outbox сообщений.
    """

    def __init__(self) -> None:
        """Инициализирует реестр событий."""
        self._event_types: dict[str, Type[DomainEvent]] = {}

    def register_domain_event(self, event_type: Type[DomainEvent]) -> None:
        """
        Регистрирует тип доменного события в реестре.

        Args:
            event_type: Класс доменного события для регистрации.

        Raises:
            ValueIsRequiredError: Если event_type равен None.
        """
        if event_type is None:
            raise ValueIsRequiredError("event_type")

        event_name = event_type.__name__
        self._event_types[event_name] = event_type

    def decode_domain_event(self, outbox_message: OutboxMessage) -> DomainEvent:
        """
        Декодирует доменное событие из outbox сообщения.

        Args:
            outbox_message: Сообщение из outbox.

        Returns:
            Декодированное доменное событие.

        Raises:
            ValueError: Если тип события не зарегистрирован или декодирование не удалось.
        """
        event_type = self._event_types.get(outbox_message.name)
        if event_type is None:
            raise ValueError(f"Unknown event type: {outbox_message.name}")

        try:
            payload_dict = json.loads(outbox_message.payload)
            # Создаём экземпляр события из словаря
            event = event_type(**payload_dict)
            if not isinstance(event, DomainEvent):
                raise ValueError(
                    f"Decoded event does not implement DomainEvent: {outbox_message.name}"
                )
            return event
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            raise ValueError(
                f"Failed to decode event payload: {outbox_message.name}"
            ) from e


def encode_domain_event(event: DomainEvent) -> OutboxMessage:
    """
    Кодирует доменное событие в outbox сообщение.

    Args:
        event: Доменное событие для кодирования.

    Returns:
        Сообщение outbox с закодированным событием.

    Raises:
        ValueError: Если кодирование события не удалось.
    """
    from datetime import datetime, timezone

    try:
        # Сериализуем событие в JSON
        # Используем dict() для Pydantic моделей или __dict__ для обычных классов
        if hasattr(event, "model_dump"):
            payload_dict = event.model_dump()
        elif hasattr(event, "dict"):
            payload_dict = event.dict()
        else:
            payload_dict = {
                k: v
                for k, v in event.__dict__.items()
                if not k.startswith("_")
            }

        payload = json.dumps(payload_dict, default=str)

        return OutboxMessage(
            id=event.id,
            name=event.get_name(),
            payload=payload,
            occurred_at_utc=datetime.now(timezone.utc),
            processed_at_utc=None,
        )
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to encode event: {event.get_name()}") from e
