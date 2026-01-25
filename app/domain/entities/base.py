"""Базовые классы для доменных сущностей."""

from typing import TYPE_CHECKING, Generic, TypeVar
from uuid import UUID

if TYPE_CHECKING:
    from app.domain.events.base import DomainEvent

ID = TypeVar("ID", bound=UUID | str | int)


class BaseEntity(Generic[ID]):
    """
    Базовая сущность домена.

    Attributes:
        _id: Уникальный идентификатор сущности.
    """

    def __init__(self, entity_id: ID) -> None:
        """
        Инициализирует базовую сущность.

        Args:
            entity_id: Уникальный идентификатор сущности.
        """
        self._id = entity_id

    @property
    def id(self) -> ID:
        """
        Возвращает идентификатор сущности.

        Returns:
            Идентификатор сущности.
        """
        return self._id

    def __eq__(self, other: object) -> bool:
        """
        Сравнивает две сущности по идентификатору.

        Args:
            other: Другая сущность для сравнения.

        Returns:
            True, если идентификаторы совпадают, иначе False.
        """
        if not isinstance(other, BaseEntity):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        """
        Возвращает хеш сущности на основе идентификатора.

        Returns:
            Хеш идентификатора.
        """
        return hash(self._id)


class BaseAggregate(BaseEntity[ID], Generic[ID]):
    """
    Базовый агрегат домена.

    Агрегат может генерировать доменные события.

    Attributes:
        _domain_events: Список доменных событий, которые произошли в агрегате.
    """

    def __init__(self, aggregate_id: ID) -> None:
        """
        Инициализирует базовый агрегат.

        Args:
            aggregate_id: Уникальный идентификатор агрегата.
        """
        super().__init__(aggregate_id)
        self._domain_events: list["DomainEvent"] = []

    def raise_domain_event(self, event: "DomainEvent") -> None:
        """
        Добавляет доменное событие в список событий агрегата.

        Args:
            event: Доменное событие для добавления.
        """
        self._domain_events.append(event)

    def get_domain_events(self) -> list["DomainEvent"]:
        """
        Возвращает список всех доменных событий агрегата.

        Returns:
            Список доменных событий.
        """
        return self._domain_events.copy()

    def clear_domain_events(self) -> None:
        """Очищает список доменных событий агрегата."""
        self._domain_events.clear()
