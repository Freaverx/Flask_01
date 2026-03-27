"""
Удобно направлять результат выполнения команды напрямую в программу с помощью конвейера (pipe):

$ ls -l | python3 get_mean_size.py

Напишите функцию get_mean_size, которая на вход принимает результат выполнения команды ls -l,
а возвращает средний размер файла в каталоге.
"""

import sys


def get_mean_size(ls_output_lines):
    """
    Функция для вычисления среднего размера файлов из вывода ls -l

    Args:
        ls_output_lines (list): Список строк с выводом команды ls -l

    Returns:
        float: Средний размер файла в байтах
    """
    total_size = 0
    file_count = 0

    for line in ls_output_lines:
        # Разбиваем строку по пробельным символам
        columns = line.split()

        # В выводе ls -l формат:
        # drwxr-xr-x 2 user group 4096 Mar 22 10:00 directory_name
        # -rw-r--r-- 1 user group 1234 Mar 22 10:00 filename.txt

        # Размер файла находится в 5-м столбце (индекс 4)
        if len(columns) >= 5:
            try:
                # Пропускаем строки, начинающиеся с 'd' (директории)
                # и другие специальные файлы (символические ссылки и т.д.)
                if columns[0].startswith('d'):
                    continue

                # Получаем размер файла
                size = int(columns[4])
                total_size += size
                file_count += 1

            except (ValueError, IndexError):
                # Пропускаем строки, которые не содержат корректный размер
                continue

    if file_count == 0:
        return 0.0

    return total_size / file_count


def format_size(bytes_value):
    """
    Преобразует байты в человекочитаемый формат

    Args:
        bytes_value (float): Количество байт

    Returns:
        str: Человекочитаемое представление размера
    """
    if bytes_value == 0:
        return "0 B"

    units = ['B', 'KiB', 'MiB', 'GiB', 'TiB']
    unit_index = 0

    while bytes_value >= 1024 and unit_index < len(units) - 1:
        bytes_value /= 1024.0
        unit_index += 1

    return f"{bytes_value:.2f} {units[unit_index]}"


if __name__ == '__main__':
    # Читаем все строки из стандартного ввода
    lines = sys.stdin.readlines()

    # Пропускаем первую строку (total или заголовок)
    # В выводе ls -l первая строка может быть "total X" или отсутствовать
    if lines and lines[0].startswith('total'):
        lines = lines[1:]

    # Вычисляем средний размер файла
    mean_size_bytes = get_mean_size(lines)

    # Выводим результат в человекочитаемом формате
    if mean_size_bytes > 0:
        print(f"Средний размер файла: {format_size(mean_size_bytes)}")
    else:
        print("Файлы не найдены или не удалось определить их размер")
