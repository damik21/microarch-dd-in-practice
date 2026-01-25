"""Медиатор для публикации и обработки доменных событий."""

from typing import Callable

from app.domain.events.base import DomainEvent


class Mediatr:
    """
    Медиатор для обработки доменных событий.

    Позволяет подписываться на события и публиковать их.
    """

    def __init__(self) -> None:
        """Инициализирует медиатор."""
        self._handlers: dict[str, list[Callable[[DomainEvent], None]]] = {}

    def subscribe(
        self,
        handler: Callable[[DomainEvent], None],
        *event_types: type[DomainEvent],
    ) -> None:
        """
        Подписывает обработчик на указанные типы событий.

        Args:
            handler: Функция-обработчик события.
            *event_types: Типы событий, на которые подписывается обработчик.
        """
        for event_type in event_types:
            event_name = event_type.__name__
            if event_name not in self._handlers:
                self._handlers[event_name] = []
            self._handlers[event_name].append(handler)

    async def publish(self, event: DomainEvent) -> None:
        """
        Публикует доменное событие, вызывая все подписанные обработчики.

        Args:
            event: Доменное событие для публикации.

        Raises:
            Exception: Если какой-либо обработчик вызвал исключение.
        """
        import inspect

        event_name = event.get_name()
        handlers = self._handlers.get(event_name, [])

        for handler in handlers:
            if not callable(handler):
                continue

            # Проверяем, является ли обработчик корутиной
            if inspect.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
