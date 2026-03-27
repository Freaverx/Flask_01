"""
Консольная утилита lsof (List Open Files) выводит информацию о том, какие файлы используют какие-либо процессы.
Эта команда может рассказать много интересного, так как в Unix-подобных системах всё является файлом.

Но нам пока нужна лишь одна из её возможностей.
Запуск lsof -i :port выдаст список процессов, занимающих введённый порт.
Например, lsof -i :5000.

Как мы с вами выяснили, наш сервер отказывается запускаться, если кто-то занял его порт. Напишите функцию,
которая на вход принимает порт и запускает по нему сервер. Если порт будет занят,
она должна найти процесс по этому порту, завершить его и попытаться запустить сервер ещё раз.
"""
import os
import signal
import subprocess
from typing import List
from flask import Flask

app = Flask(__name__)


def get_pids(port: int) -> List[int]:
    """
    Возвращает список PID процессов, занимающих переданный порт
    @param port: порт
    @return: список PID процессов, занимающих порт
    """
    if not isinstance(port, int):
        raise ValueError("Port must be an integer")

    if port < 1 or port > 65535:
        raise ValueError("Port must be between 1 and 65535")

    pids: List[int] = []

    try:
        # Используем lsof для поиска процессов на порту
        result = subprocess.run(
            ['lsof', '-ti', f':{port}'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0 and result.stdout:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        pid = int(line.strip())
                        pids.append(pid)
                    except ValueError:
                        continue

    except subprocess.TimeoutExpired:
        print(f"Timeout while checking port {port}")
    except FileNotFoundError:
        print("lsof command not found. Please install lsof.")
    except Exception as e:
        print(f"Error getting PIDs: {e}")

    return pids


def free_port(port: int) -> None:
    """
    Завершает процессы, занимающие переданный порт
    @param port: порт
    """
    pids: List[int] = get_pids(port)

    for pid in pids:
        try:
            # Отправляем сигнал SIGTERM для graceful shutdown
            os.kill(pid, signal.SIGTERM)
            print(f"Sent SIGTERM to process {pid}")

            # Ждём немного для завершения процесса
            import time
            time.sleep(0.5)

            # Проверяем, завершился ли процесс
            try:
                os.kill(pid, 0)  # Проверяем существование процесса
                # Если процесс ещё жив, отправляем SIGKILL
                os.kill(pid, signal.SIGKILL)
                print(f"Sent SIGKILL to process {pid}")
            except ProcessLookupError:
                print(f"Process {pid} terminated successfully")

        except ProcessLookupError:
            print(f"Process {pid} already terminated")
        except PermissionError:
            print(f"Permission denied to kill process {pid}")
        except Exception as e:
            print(f"Error killing process {pid}: {e}")


def run(port: int) -> None:
    """
    Запускает flask-приложение по переданному порту.
    Если порт занят каким-либо процессом, завершает его.
    @param port: порт
    """
    # Проверяем, занят ли порт
    pids = get_pids(port)

    if pids:
        print(f"Port {port} is occupied by processes: {pids}")
        print(f"Attempting to free port {port}...")
        free_port(port)
        print(f"Port {port} freed")
    else:
        print(f"Port {port} is free")

    # Запускаем приложение
    print(f"Starting Flask app on port {port}...")
    app.run(port=port, debug=False)


if __name__ == '__main__':
    run(5000)
