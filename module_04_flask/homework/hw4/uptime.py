"""
Напишите GET-эндпоинт /uptime, который в ответ на запрос будет выводить строку вида f"Current uptime is {UPTIME}",
где UPTIME — uptime системы (показатель того, как долго текущая система не перезагружалась).

Сделать это можно с помощью команды uptime.
"""

import subprocess
from flask import Flask

app = Flask(__name__)


@app.route('/uptime', methods=['GET'])
def get_uptime():
    """
    GET-endpoint, возвращающий время работы системы.
    """
    try:
        # Используем флаг -p для вывода в удобочитаемом формате
        # uptime -p выводит что-то вроде "up 5 days, 2 hours, 34 minutes"
        result = subprocess.run(['uptime', '-p'], capture_output=True, text=True, check=True)
        uptime_output = result.stdout.strip()

        # Убираем префикс "up "
        if uptime_output.startswith('up '):
            uptime_output = uptime_output[3:]

        return f"Current uptime is {uptime_output}"

    except subprocess.CalledProcessError:
        # Если флаг -p не поддерживается, используем обычный uptime
        result = subprocess.run(['uptime'], capture_output=True, text=True, check=True)
        uptime_output = result.stdout.strip()

        # Простое извлечение времени работы
        import re
        match = re.search(r'up\s+(.*?)(?:,\s+\d+\s+user|,?\s+load average)', uptime_output)
        uptime_str = match.group(1) if match else uptime_output

        return f"Current uptime is {uptime_str}"

    except Exception as e:
        return f"Error getting uptime: {e}", 500


if __name__ == "__main__":
    app.run(debug=True)
