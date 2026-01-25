"""Базовый класс для доменных событий."""

from abc import ABC, abstractmethod
from uuid import UUID, uuid4


class DomainEvent(ABC):
    """
    Интерфейс доменного события.

    Все доменные события должны реализовывать этот интерфейс.
    """

    def __init__(self, event_id: UUID | None = None) -> None:
        """
        Инициализирует доменное событие.

        Args:
            event_id: Уникальный идентификатор события. Если не указан, генерируется автоматически.
        """
        self._id = event_id if event_id is not None else uuid4()

    @property
    def id(self) -> UUID:
        """
        Возвращает идентификатор события.

        Returns:
            UUID события.
        """
        return self._id

    @abstractmethod
    def get_name(self) -> str:
        """
        Возвращает имя типа события.

        Returns:
            Имя типа события (обычно имя класса).
        """
        pass
