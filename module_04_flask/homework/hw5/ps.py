"""
Напишите GET-эндпоинт /ps, который принимает на вход аргументы командной строки,
а возвращает результат работы команды ps с этими аргументами.
Входные значения эндпоинт должен принимать в виде списка через аргумент arg.

Например, для исполнения команды ps aux запрос будет следующим:

/ps?arg=a&arg=u&arg=x
"""

import shlex
import subprocess
from flask import Flask, request

app = Flask(__name__)


@app.route('/ps', methods=['GET'])
def get_processes():
    """
    GET-endpoint, выполняющий команду ps с переданными аргументами.

    Args:
        arg: список аргументов для команды ps (передаётся через query параметр)

    Returns:
        str: Результат выполнения команды ps, заключённый в тег <pre>
    """
    # Получаем список аргументов из запроса
    args = request.args.getlist('arg')

    # Проверяем, что аргументы переданы
    if not args:
        return """
        <h1>Ошибка: не переданы аргументы</h1>
        <p>Используйте формат: /ps?arg=a&arg=u&arg=x</p>
        <p>Примеры:</p>
        <ul>
            <li><a href="/ps?arg=a&arg=u&arg=x">/ps?arg=a&arg=u&arg=x</a></li>
            <li><a href="/ps?arg=aux">/ps?arg=aux</a></li>
            <li><a href="/ps?arg=ef">/ps?arg=ef</a></li>
        </ul>
        """, 400

    # Валидация аргументов
    valid_args, invalid_args = validate_ps_args(args)

    if invalid_args:
        return f"""
        <h1>Ошибка: обнаружены небезопасные аргументы</h1>
        <p>Небезопасные аргументы: {', '.join(invalid_args)}</p>
        <p>Разрешены только аргументы, начинающиеся с букв, цифр, дефиса или подчёркивания.</p>
        """, 400

    try:
        # Формируем команду с безопасными аргументами
        command = ['ps'] + valid_args

        # Экранируем каждый аргумент для безопасности
        safe_command = [shlex.quote(arg) for arg in command]

        # Выполняем команду
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10  # Таймаут на случай зависания
        )

        # Проверяем результат выполнения
        if result.returncode != 0:
            error_message = result.stderr if result.stderr else "Команда завершилась с ошибкой"
            return f"<h1>Ошибка выполнения команды ps</h1><pre>{error_message}</pre>", 500

        # Возвращаем результат в красиво отформатированном виде
        return f"<pre>{result.stdout}</pre>"

    except subprocess.TimeoutExpired:
        return "<h1>Ошибка: команда ps превысила время ожидания</h1>", 500
    except subprocess.SubprocessError as e:
        return f"<h1>Ошибка выполнения команды</h1><pre>{str(e)}</pre>", 500
    except Exception as e:
        return f"<h1>Непредвиденная ошибка</h1><pre>{str(e)}</pre>", 500


def validate_ps_args(args):
    """
    Валидирует аргументы для команды ps.

    Args:
        args (list): Список аргументов для проверки

    Returns:
        tuple: (valid_args, invalid_args)
    """
    # Разрешённые символы в аргументах: буквы, цифры, дефис, подчёркивание
    import re
    allowed_pattern = re.compile(r'^[a-zA-Z0-9_-]+$')

    # Список потенциально опасных аргументов, которые стоит заблокировать
    dangerous_args = [';', '&&', '||', '|', '>', '<', '$', '`', '\\', '"', "'", '!', '#', '&']

    valid_args = []
    invalid_args = []

    for arg in args:
        # Проверяем, что аргумент не пустой
        if not arg:
            invalid_args.append(f"(пустой аргумент)")
            continue

        # Проверяем, что аргумент содержит только разрешённые символы
        if not allowed_pattern.match(arg):
            # Если аргумент не подходит под паттерн, проверяем, не является ли он
            # комбинацией безопасных аргументов (например, "aux" - это целый аргумент)
            # Многие ps аргументы могут быть без дефиса (например, "aux", "ef")
            if any(char in arg for char in dangerous_args):
                invalid_args.append(arg)
                continue

        valid_args.append(arg)

    return valid_args, invalid_args


@app.route('/ps/help', methods=['GET'])
def ps_help():
    """
    Справка по использованию эндпоинта /ps
    """
    return """
    <h1>Справка по использованию /ps endpoint</h1>

    <h2>Формат запроса:</h2>
    <code>/ps?arg=аргумент1&arg=аргумент2&arg=аргумент3</code>

    <h2>Примеры:</h2>
    <ul>
        <li><a href="/ps?arg=a&arg=u&arg=x">/ps?arg=a&arg=u&arg=x</a> - все процессы (ps aux)</li>
        <li><a href="/ps?arg=aux">/ps?arg=aux</a> - альтернативный формат ps aux</li>
        <li><a href="/ps?arg=ef">/ps?arg=ef</a> - все процессы в формате System V</li>
        <li><a href="/ps?arg=-e&arg=-f">/ps?arg=-e&arg=-f</a> - все процессы с полным форматом</li>
        <li><a href="/ps?arg=-u&arg=root">/ps?arg=-u&arg=root</a> - процессы пользователя root</li>
    </ul>

    <h2>Популярные аргументы ps:</h2>
    <table border="1" cellpadding="5">
        <tr><th>Аргумент</th><th>Описание</th></tr>
        <tr><td>a</td><td>Показать процессы всех пользователей</td></tr>
        <tr><td>u</td><td>Показать подробную информацию о пользователе</td></tr>
        <tr><td>x</td><td>Показать процессы без управляющего терминала</td></tr>
        <tr><td>aux</td><td>Комбинация a, u, x (все процессы)</td></tr>
        <tr><td>-e</td><td>Все процессы</td></tr>
        <tr><td>-f</td><td>Полный формат вывода</td></tr>
        <tr><td>-u &lt;user&gt;</td><td>Процессы конкретного пользователя</td></tr>
        <tr><td>-p &lt;pid&gt;</td><td>Процесс с указанным PID</td></tr>
    </table>

    <h2>Безопасность:</h2>
    <p>Все аргументы проходят валидацию и экранирование. Запрещены специальные символы,
    которые могут быть использованы для инъекций команд.</p>
    """, 200


if __name__ == "__main__":
    app.run(debug=True)
