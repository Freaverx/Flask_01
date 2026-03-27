"""
Напишите эндпоинт, который принимает на вход код на Python (строка)
и тайм-аут в секундах (положительное число не больше 30).
Пользователю возвращается результат работы программы, а если время, отведённое на выполнение кода, истекло,
то процесс завершается, после чего отправляется сообщение о том, что исполнение кода не уложилось в данное время.
"""

import subprocess
import shlex
from flask import Flask, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import InputRequired, NumberRange, Length

app = Flask(__name__)
app.config['WTF_CSRF_ENABLED'] = False


class CodeForm(FlaskForm):
    """Форма для выполнения Python кода"""
    code = StringField(
        'code',
        validators=[
            InputRequired(message="Code is required"),
            Length(max=10000, message="Code too long (max 10000 characters)")
        ]
    )
    timeout = IntegerField(
        'timeout',
        validators=[
            InputRequired(message="Timeout is required"),
            NumberRange(min=1, max=30, message="Timeout must be between 1 and 30 seconds")
        ]
    )


def run_python_code_in_subprocess(code: str, timeout: int) -> tuple[str, str, int]:
    """
    Запускает Python код в подпроцессе с ограничениями

    Args:
        code: Python код для выполнения
        timeout: Таймаут в секундах

    Returns:
        tuple: (stdout, stderr, returncode)
    """
    # Экранируем код для безопасной передачи в командную строку
    # Используем base64 для безопасной передачи кода
    import base64

    # Кодируем код в base64 для безопасной передачи
    encoded_code = base64.b64encode(code.encode('utf-8')).decode('ascii')

    # Формируем команду для безопасного выполнения
    # Используем prlimit для ограничения ресурсов
    cmd = [
        'prlimit', '--nproc=10:10', '--cpu=30',
        'python3', '-c',
        f'import base64; exec(base64.b64decode("{encoded_code}").decode("utf-8"))'
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )

        return result.stdout, result.stderr, result.returncode

    except subprocess.TimeoutExpired:
        return "", f"Execution timeout after {timeout} seconds", -1
    except subprocess.SubprocessError as e:
        return "", f"Subprocess error: {e}", -1
    except Exception as e:
        return "", f"Unexpected error: {e}", -1


@app.route('/run_code', methods=['POST'])
def run_code():
    """
    Endpoint для выполнения Python кода
    """
    # Получаем данные из запроса
    form = CodeForm()

    if form.validate_on_submit():
        code = form.code.data
        timeout = form.timeout.data

        # Выполняем код
        stdout, stderr, returncode = run_python_code_in_subprocess(code, timeout)

        # Формируем ответ
        result = {
            'success': returncode == 0 and not stderr,
            'stdout': stdout,
            'stderr': stderr,
            'returncode': returncode
        }

        if timeout > 0 and returncode == -1 and 'timeout' in stderr.lower():
            result['message'] = f'Execution did not complete within {timeout} seconds'

        return jsonify(result), 200

    # Валидация не пройдена
    return jsonify({
        'success': False,
        'errors': form.errors
    }), 400


@app.route('/run_code/help', methods=['GET'])
def help_endpoint():
    """Справка по использованию"""
    return jsonify({
        'endpoint': '/run_code',
        'method': 'POST',
        'fields': {
            'code': {
                'type': 'string',
                'required': True,
                'description': 'Python code to execute',
                'max_length': 10000
            },
            'timeout': {
                'type': 'integer',
                'required': True,
                'description': 'Timeout in seconds',
                'min': 1,
                'max': 30
            }
        },
        'example': {
            'code': 'print("Hello, World!")',
            'timeout': 5
        }
    })


if __name__ == '__main__':
    app.run(debug=True)
