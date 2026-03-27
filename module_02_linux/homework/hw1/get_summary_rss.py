"""
С помощью команды ps можно посмотреть список запущенных процессов.
С флагами aux эта команда выведет информацию обо всех процессах, запущенных в системе.

Запустите эту команду и сохраните выданный результат в файл:

$ ps aux > output_file.txt

Столбец RSS показывает информацию о потребляемой памяти в байтах.

Напишите функцию get_summary_rss, которая на вход принимает путь до файла с результатом выполнения команды ps aux,
а возвращает суммарный объём потребляемой памяти в человекочитаемом формате.
Это означает, что ответ надо перевести в байты, килобайты, мегабайты и так далее.
"""

import os


def get_summary_rss(file_path):
    """
    Функция для подсчёта суммарного объёма потребляемой памяти из файла ps aux

    Args:
        file_path (str): Путь к файлу с выводом команды ps aux

    Returns:
        str: Суммарный объём памяти в человекочитаемом формате
    """
    total_rss_bytes = 0

    try:
        with open(file_path, 'r') as file:
            # Пропускаем заголовок (первую строку)
            lines = file.readlines()[1:]

            for line in lines:
                # Разбиваем строку по пробельным символам
                columns = line.split()

                # RSS находится в 6-м столбце (индекс 5)
                # В ps aux столбцы: USER PID %CPU %MEM VSZ RSS TTY STAT START TIME COMMAND
                if len(columns) > 5:
                    try:
                        rss_value = int(columns[5])
                        total_rss_bytes += rss_value
                    except ValueError:
                        # Пропускаем строки, где RSS не является числом
                        continue

    except FileNotFoundError:
        return f"Ошибка: файл '{file_path}' не найден"
    except Exception as e:
        return f"Ошибка при чтении файла: {e}"

    # Преобразуем байты в человекочитаемый формат
    return format_bytes(total_rss_bytes)


def format_bytes(bytes_value):
    """
    Преобразует байты в человекочитаемый формат

    Args:
        bytes_value (int): Количество байт

    Returns:
        str: Человекочитаемое представление размера
    """
    if bytes_value == 0:
        return "0 B"

    # Единицы измерения
    units = ['B', 'KiB', 'MiB', 'GiB', 'TiB']
    unit_index = 0

    # Пока значение больше 1024 и не превысили максимальную единицу
    while bytes_value >= 1024 and unit_index < len(units) - 1:
        bytes_value /= 1024.0
        unit_index += 1

    # Форматируем с одним знаком после запятой
    return f"{bytes_value:.1f} {units[unit_index]}"


if __name__ == '__main__':
    # Путь к файлу с выводом ps aux
    file_path = 'output_file.txt'

    # Проверяем, существует ли файл
    if not os.path.exists(file_path):
        print(f"Файл '{file_path}' не найден.")
        print("Сначала выполните команду: ps aux > output_file.txt")
    else:
        # Вызываем функцию и выводим результат
        summary = get_summary_rss(file_path)
        print(f"Суммарный объём потребляемой памяти: {summary}")
