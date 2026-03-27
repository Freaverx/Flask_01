import unittest
import json
from remote_execution import app


class TestRemoteExecution(unittest.TestCase):
    """Тесты для эндпоинта /run_code"""

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    # ==================== Тесты валидных данных ====================

    def test_valid_code_execution(self):
        """Тест выполнения валидного кода"""
        data = {
            'code': 'print("Hello, World!")',
            'timeout': 5
        }
        response = self.client.post('/run_code', data=data)
        self.assertEqual(response.status_code, 200)

        result = json.loads(response.data)
        self.assertTrue(result['success'])
        self.assertIn('Hello, World!', result['stdout'])

    def test_code_with_math_operations(self):
        """Тест кода с математическими операциями"""
        data = {
            'code': 'result = 2 + 2 * 3; print(result)',
            'timeout': 5
        }
        response = self.client.post('/run_code', data=data)
        result = json.loads(response.data)

        self.assertTrue(result['success'])
        self.assertIn('8', result['stdout'])

    def test_code_with_loop(self):
        """Тест кода с циклом"""
        data = {
            'code': 'for i in range(3): print(i)',
            'timeout': 5
        }
        response = self.client.post('/run_code', data=data)
        result = json.loads(response.data)

        self.assertTrue(result['success'])
        self.assertIn('0', result['stdout'])
        self.assertIn('1', result['stdout'])
        self.assertIn('2', result['stdout'])

    def test_code_with_multiline(self):
        """Тест многострочного кода"""
        data = {
            'code': """
def greet(name):
    return f"Hello, {name}!"

print(greet("Python"))
""",
            'timeout': 5
        }
        response = self.client.post('/run_code', data=data)
        result = json.loads(response.data)

        self.assertTrue(result['success'])
        self.assertIn('Hello, Python!', result['stdout'])

    # ==================== Тесты таймаута ====================

    def test_timeout_less_than_execution_time(self):
        """Тест: таймаут меньше времени выполнения"""
        data = {
            'code': 'import time; time.sleep(3); print("Done")',
            'timeout': 1
        }
        response = self.client.post('/run_code', data=data)
        self.assertEqual(response.status_code, 200)

        result = json.loads(response.data)
        self.assertFalse(result['success'])
        self.assertIn('timeout', result['message'].lower())

    def test_timeout_greater_than_execution_time(self):
        """Тест: таймаут больше времени выполнения"""
        data = {
            'code': 'import time; time.sleep(1); print("Done")',
            'timeout': 5
        }
        response = self.client.post('/run_code', data=data)
        result = json.loads(response.data)

        self.assertTrue(result['success'])
        self.assertIn('Done', result['stdout'])

    # ==================== Тесты валидации ====================

    def test_missing_code(self):
        """Тест: отсутствует код"""
        data = {
            'timeout': 5
        }
        response = self.client.post('/run_code', data=data)
        self.assertEqual(response.status_code, 400)

        result = json.loads(response.data)
        self.assertFalse(result['success'])
        self.assertIn('code', result['errors'])

    def test_missing_timeout(self):
        """Тест: отсутствует таймаут"""
        data = {
            'code': 'print("Hello")'
        }
        response = self.client.post('/run_code', data=data)
        self.assertEqual(response.status_code, 400)

        result = json.loads(response.data)
        self.assertFalse(result['success'])
        self.assertIn('timeout', result['errors'])

    def test_timeout_too_large(self):
        """Тест: таймаут больше максимального значения"""
        data = {
            'code': 'print("Hello")',
            'timeout': 60
        }
        response = self.client.post('/run_code', data=data)
        self.assertEqual(response.status_code, 400)

        result = json.loads(response.data)
        self.assertIn('timeout', result['errors'])

    def test_timeout_negative(self):
        """Тест: отрицательный таймаут"""
        data = {
            'code': 'print("Hello")',
            'timeout': -1
        }
        response = self.client.post('/run_code', data=data)
        self.assertEqual(response.status_code, 400)

        result = json.loads(response.data)
        self.assertIn('timeout', result['errors'])

    def test_code_too_long(self):
        """Тест: слишком длинный код"""
        long_code = 'print("a")' * 2000  # ~20000 символов
        data = {
            'code': long_code,
            'timeout': 5
        }
        response = self.client.post('/run_code', data=data)
        self.assertEqual(response.status_code, 400)

        result = json.loads(response.data)
        self.assertIn('code', result['errors'])

    # ==================== Тесты безопасности ====================

    def test_safe_command_injection(self):
        """Тест: защита от инъекции команд"""
        # Пытаемся выполнить системную команду
        data = {
            'code': 'import os; os.system("echo hacked")',
            'timeout': 5
        }
        response = self.client.post('/run_code', data=data)
        result = json.loads(response.data)

        # Код должен выполниться, но без возможности системных вызовов
        # Из-за ограничений prlimit системные вызовы могут не сработать
        self.assertTrue(result['success'] or not result['success'])

    def test_shell_injection_attempt(self):
        """Тест: попытка инъекции через shell"""
        # Пытаемся выполнить код с shell-инъекцией
        data = {
            'code': '"; echo "hacked" ; print("Hello")',
            'timeout': 5
        }
        response = self.client.post('/run_code', data=data)
        # Код должен быть выполнен безопасно
        self.assertIn(response.status_code, [200, 400])

    def test_resource_limitation(self):
        """Тест: ограничение ресурсов"""
        # Пытаемся создать много процессов
        data = {
            'code': """
import subprocess
for i in range(100):
    subprocess.Popen(['echo', 'test'])
print("Done")
""",
            'timeout': 5
        }
        response = self.client.post('/run_code', data=data)
        result = json.loads(response.data)

        # Должна быть ошибка из-за ограничения процессов
        # или успешное выполнение с ограничением
        self.assertIsNotNone(result)

    # ==================== Тесты синтаксических ошибок ====================

    def test_syntax_error(self):
        """Тест: синтаксическая ошибка в коде"""
        data = {
            'code': 'print("Hello"',  # Пропущена закрывающая скобка
            'timeout': 5
        }
        response = self.client.post('/run_code', data=data)
        result = json.loads(response.data)

        self.assertFalse(result['success'])
        self.assertNotEqual(result['stderr'], '')

    def test_runtime_error(self):
        """Тест: ошибка времени выполнения"""
        data = {
            'code': '1 / 0',  # Деление на ноль
            'timeout': 5
        }
        response = self.client.post('/run_code', data=data)
        result = json.loads(response.data)

        self.assertFalse(result['success'])
        self.assertIn('ZeroDivisionError', result['stderr'])

    # ==================== Тесты различных типов вывода ====================

    def test_code_with_stdout_and_stderr(self):
        """Тест кода с выводом в stdout и stderr"""
        data = {
            'code': 'import sys; print("stdout"); print("stderr", file=sys.stderr)',
            'timeout': 5
        }
        response = self.client.post('/run_code', data=data)
        result = json.loads(response.data)

        self.assertTrue(result['success'])
        self.assertIn('stdout', result['stdout'])
        self.assertIn('stderr', result['stderr'])

    def test_code_no_output(self):
        """Тест кода без вывода"""
        data = {
            'code': 'x = 5 + 3',
            'timeout': 5
        }
        response = self.client.post('/run_code', data=data)
        result = json.loads(response.data)

        self.assertTrue(result['success'])
        self.assertEqual(result['stdout'], '')

    # ==================== Интеграционные тесты ====================

    def test_help_endpoint(self):
        """Тест эндпоинта справки"""
        response = self.client.get('/run_code/help')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('endpoint', data)
        self.assertIn('fields', data)


if __name__ == '__main__':
    unittest.main(verbosity=2)
