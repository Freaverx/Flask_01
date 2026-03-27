"""
Реализуйте контекстный менеджер, который будет игнорировать переданные типы исключений, возникающие внутри блока with.
Если выкидывается неожидаемый тип исключения, то он прокидывается выше.
"""

from typing import Collection, Type, Literal
from types import TracebackType


class BlockErrors:
    """
    Контекстный менеджер, игнорирующий указанные типы исключений.

    Пример использования:
        with BlockErrors({ZeroDivisionError, TypeError}):
            a = 1 / 0
        print('Выполнено без ошибок')
    """

    def __init__(self, errors: Collection) -> None:
        """
        Инициализация контекстного менеджера.

        Args:
            errors: Коллекция типов исключений, которые нужно игнорировать
        """
        self.errors = errors
        self._original_exc_info = None

    def __enter__(self) -> None:
        """Вход в контекстный менеджер"""
        return None

    def __exit__(
            self,
            exc_type: Type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: TracebackType | None
    ) -> Literal[True] | None:
        """
        Выход из контекстного менеджера.

        Если возникшее исключение является подклассом одного из указанных
        типов, оно игнорируется (подавляется).

        Returns:
            True если исключение было обработано, иначе None
        """
        # Если нет исключения, просто выходим
        if exc_type is None:
            return None

        # Проверяем, нужно ли игнорировать исключение
        for error_type in self.errors:
            if issubclass(exc_type, error_type):
                # Игнорируем исключение
                return True

        # Пропускаем исключение выше
        return None