"""
Иногда возникает необходимость перенаправить вывод в нужное нам место внутри программы по ходу её выполнения.
Реализуйте контекстный менеджер, который принимает два IO-объекта (например, открытые файлы)
и перенаправляет туда стандартные потоки stdout и stderr.

Аргументы контекстного менеджера должны быть непозиционными,
чтобы можно было ещё перенаправить только stdout или только stderr.
"""

"""
Контекстный менеджер для перенаправления stdout и stderr.
"""

import sys
from types import TracebackType
from typing import Type, Literal, IO, Optional


class Redirect:
    """
    Контекстный менеджер для перенаправления stdout и stderr.

    Аргументы контекстного менеджера непозиционные, что позволяет
    перенаправить только stdout, только stderr или оба потока.

    Пример использования:
        with open('stdout.txt', 'w') as stdout_file:
            with Redirect(stdout=stdout_file):
                print('Это будет записано в файл')

        with open('stderr.txt', 'w') as stderr_file:
            with Redirect(stderr=stderr_file):
                raise Exception('Это будет записано в файл ошибок')

        with open('out.txt', 'w') as out, open('err.txt', 'w') as err:
            with Redirect(stdout=out, stderr=err):
                print('В файл out.txt')
                raise Exception('В файл err.txt')
    """

    def __init__(self, stdout: Optional[IO] = None, stderr: Optional[IO] = None) -> None:
        """
        Инициализация контекстного менеджера.

        Args:
            stdout: Объект для перенаправления stdout (опционально)
            stderr: Объект для перенаправления stderr (опционально)
        """
        self._stdout_target = stdout
        self._stderr_target = stderr
        self._original_stdout = None
        self._original_stderr = None

    def __enter__(self):
        """
        Вход в контекстный менеджер.
        Сохраняет оригинальные потоки и перенаправляет их на новые.
        """
        # Сохраняем оригинальные потоки
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr

        # Перенаправляем stdout если указан
        if self._stdout_target is not None:
            sys.stdout = self._stdout_target

        # Перенаправляем stderr если указан
        if self._stderr_target is not None:
            sys.stderr = self._stderr_target

        return self

    def __exit__(
            self,
            exc_type: Type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: TracebackType | None
    ) -> Literal[True] | None:
        """
        Выход из контекстного менеджера.
        Восстанавливает оригинальные потоки.
        """
        # Восстанавливаем stdout
        if self._original_stdout is not None:
            sys.stdout = self._original_stdout

        # Восстанавливаем stderr
        if self._original_stderr is not None:
            sys.stderr = self._original_stderr

        # Не подавляем исключения
        return None
