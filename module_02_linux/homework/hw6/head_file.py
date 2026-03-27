"""
Реализуйте endpoint, который показывает превью файла, принимая на вход два параметра: SIZE (int) и RELATIVE_PATH —
и возвращая первые SIZE символов файла по указанному в RELATIVE_PATH пути.

Endpoint должен вернуть страницу с двумя строками.
В первой строке будет содержаться информация о файле: его абсолютный путь и размер файла в символах,
а во второй строке — первые SIZE символов из файла:

<abs_path> <result_size><br>
<result_text>

где abs_path — написанный жирным абсолютный путь до файла;
result_text — первые SIZE символов файла;
result_size — длина result_text в символах.

Перенос строки осуществляется с помощью HTML-тега <br>.

Пример:

docs/simple.txt:
hello world!

/preview/8/docs/simple.txt
/home/user/module_2/docs/simple.txt 8
hello wo

/preview/100/docs/simple.txt
/home/user/module_2/docs/simple.txt 12
hello world!
"""

import os
from flask import Flask, abort

app = Flask(__name__)

# Определяем базовую директорию проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@app.route('/preview/<int:size>/<path:relative_path>')
def preview_file(size, relative_path):
    """
    Возвращает превью файла: первые size символов

    Args:
        size (int): Количество символов для превью
        relative_path (str): Относительный путь к файлу

    Returns:
        str: HTML-страница с информацией о файле и превью
    """
    # Формируем полный путь к файлу
    file_path = os.path.join(BASE_DIR, relative_path)
    abs_path = os.path.abspath(file_path)

    # Проверяем, существует ли файл
    if not os.path.exists(file_path):
        abort(404, description=f"Файл '{relative_path}' не найден")

    # Проверяем, является ли путь файлом (не директорией)
    if not os.path.isfile(file_path):
        abort(400, description=f"'{relative_path}' не является файлом")

    try:
        # Читаем первые size символов файла без загрузки всего файла
        with open(file_path, 'r', encoding='utf-8') as file:
            # Читаем ровно size символов
            result_text = file.read(size)
            result_size = len(result_text)

        # Формируем ответ
        # Жирный шрифт для абсолютного пути
        return f'<b>{abs_path}</b> {result_size}<br>{result_text}'

    except UnicodeDecodeError:
        # Пробуем прочитать в бинарном режиме, если текстовый не удался
        try:
            with open(file_path, 'rb') as file:
                result_bytes = file.read(size)
                result_text = result_bytes.decode('utf-8', errors='replace')
                result_size = len(result_text)

            return f'<b>{abs_path}</b> {result_size}<br>{result_text}'
        except Exception as e:
            abort(500, description=f"Ошибка при чтении файла: {str(e)}")

    except Exception as e:
        abort(500, description=f"Ошибка при чтении файла: {str(e)}")


if __name__ == '__main__':
    app.run(debug=True)
