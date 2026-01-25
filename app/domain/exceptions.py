"""Доменные исключения."""


class DomainException(Exception):
    """Базовое исключение домена."""

    pass


class ObjectNotFoundError(DomainException):
    """
    Исключение, возникающее когда объект не найден.

    Attributes:
        param_name: Имя параметра, по которому искали объект.
        object_id: Идентификатор объекта, который не был найден.
        cause: Причина ошибки (опционально).
    """

    def __init__(
        self,
        param_name: str,
        object_id: str | int | None = None,
        cause: Exception | None = None,
    ) -> None:
        """
        Инициализирует исключение.

        Args:
            param_name: Имя параметра, по которому искали объект.
            object_id: Идентификатор объекта, который не был найден.
            cause: Причина ошибки (опционально).
        """
        self.param_name = param_name
        self.object_id = object_id
        self.cause = cause
        message = f"Object not found: param is {param_name}"
        if object_id is not None:
            message += f", ID is {object_id}"
        if cause is not None:
            message += f" (cause: {cause})"
        super().__init__(message)


class ValueIsInvalidError(DomainException):
    """
    Исключение, возникающее когда значение невалидно.

    Attributes:
        param_name: Имя параметра с невалидным значением.
        value: Невалидное значение.
    """

    def __init__(self, param_name: str, value: str | None = None) -> None:
        """
        Инициализирует исключение.

        Args:
            param_name: Имя параметра с невалидным значением.
            value: Невалидное значение.
        """
        self.param_name = param_name
        self.value = value
        message = f"Value is invalid: param is {param_name}"
        if value is not None:
            message += f", value is {value}"
        super().__init__(message)


class ValueIsRequiredError(DomainException):
    """
    Исключение, возникающее когда обязательное значение отсутствует.

    Attributes:
        param_name: Имя параметра, который обязателен.
    """

    def __init__(self, param_name: str) -> None:
        """
        Инициализирует исключение.

        Args:
            param_name: Имя параметра, который обязателен.
        """
        self.param_name = param_name
        super().__init__(f"Value is required: param is {param_name}")


class ValueIsOutOfRangeError(DomainException):
    """
    Исключение, возникающее когда значение выходит за допустимые границы.

    Attributes:
        param_name: Имя параметра.
        value: Значение, которое вышло за границы.
        min_value: Минимальное допустимое значение (опционально).
        max_value: Максимальное допустимое значение (опционально).
    """

    def __init__(
        self,
        param_name: str,
        value: str | int | float | None = None,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
    ) -> None:
        """
        Инициализирует исключение.

        Args:
            param_name: Имя параметра.
            value: Значение, которое вышло за границы.
            min_value: Минимальное допустимое значение (опционально).
            max_value: Максимальное допустимое значение (опционально).
        """
        self.param_name = param_name
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        message = f"Value is out of range: param is {param_name}"
        if value is not None:
            message += f", value is {value}"
        if min_value is not None:
            message += f", min is {min_value}"
        if max_value is not None:
            message += f", max is {max_value}"
        super().__init__(message)


class VersionIsInvalidError(DomainException):
    """
    Исключение, возникающее когда версия объекта невалидна.

    Attributes:
        param_name: Имя параметра с невалидной версией.
        version: Невалидная версия.
    """

    def __init__(self, param_name: str, version: str | int | None = None) -> None:
        """
        Инициализирует исключение.

        Args:
            param_name: Имя параметра с невалидной версией.
            version: Невалидная версия.
        """
        self.param_name = param_name
        self.version = version
        message = f"Version is invalid: param is {param_name}"
        if version is not None:
            message += f", version is {version}"
        super().__init__(message)
