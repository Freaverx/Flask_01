import unittest
import sys
import io
import tempfile
import os
from redirect import Redirect


class TestRedirect(unittest.TestCase):
    """Тесты для контекстного менеджера Redirect"""

    def setUp(self):
        """Подготовка к тестам"""
        self.stdout_file = io.StringIO()
        self.stderr_file = io.StringIO()

    # ==================== Тесты перенаправления stdout ====================

    def test_redirect_stdout_only(self):
        """Тест: перенаправление только stdout"""
        original_stdout = sys.stdout

        with Redirect(stdout=self.stdout_file):
            print("Hello, stdout!")

        # Проверяем, что stdout восстановлен
        self.assertIs(sys.stdout, original_stdout)

        # Проверяем содержимое файла
        self.stdout_file.seek(0)
        content = self.stdout_file.read()
        self.assertIn("Hello, stdout!", content)

    def test_redirect_stdout_with_multiple_lines(self):
        """Тест: перенаправление stdout с несколькими строками"""
        with Redirect(stdout=self.stdout_file):
            print("Line 1")
            print("Line 2")
            print("Line 3")

        self.stdout_file.seek(0)
        content = self.stdout_file.read()

        self.assertIn("Line 1", content)
        self.assertIn("Line 2", content)
        self.assertIn("Line 3", content)

    def test_redirect_stdout_no_output(self):
        """Тест: перенаправление stdout без вывода"""
        with Redirect(stdout=self.stdout_file):
            pass  # Ничего не выводим

        self.stdout_file.seek(0)
        content = self.stdout_file.read()
        self.assertEqual(content, "")

    # ==================== Тесты перенаправления stderr ====================

    def test_redirect_stderr_only(self):
        """Тест: перенаправление только stderr"""
        original_stderr = sys.stderr

        with Redirect(stderr=self.stderr_file):
            import sys
            print("Error message", file=sys.stderr)

        # Проверяем, что stderr восстановлен
        self.assertIs(sys.stderr, original_stderr)

        # Проверяем содержимое файла
        self.stderr_file.seek(0)
        content = self.stderr_file.read()
        self.assertIn("Error message", content)

    def test_redirect_stderr_with_exception(self):
        """Тест: перенаправление stderr при исключении"""
        try:
            with Redirect(stderr=self.stderr_file):
                raise ValueError("Test exception")
        except ValueError:
            pass

        self.stderr_file.seek(0)
        content = self.stderr_file.read()
        self.assertIn("Test exception", content)

    # ==================== Тесты одновременного перенаправления ====================

    def test_redirect_both_stdout_and_stderr(self):
        """Тест: одновременное перенаправление stdout и stderr"""
        with Redirect(stdout=self.stdout_file, stderr=self.stderr_file):
            print("To stdout")
            import sys
            print("To stderr", file=sys.stderr)

        self.stdout_file.seek(0)
        self.stderr_file.seek(0)

        self.assertIn("To stdout", self.stdout_file.read())
        self.assertIn("To stderr", self.stderr_file.read())

    # ==================== Тесты с реальными файлами ====================

    def test_with_real_file_stdout(self):
        """Тест с реальным файлом для stdout"""
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp_file:
            filename = tmp_file.name

            with Redirect(stdout=tmp_file):
                print("Test output to file")

        # Проверяем содержимое файла
        with open(filename, 'r') as f:
            content = f.read()
            self.assertIn("Test output to file", content)

        # Удаляем временный файл
        os.unlink(filename)

    def test_with_real_file_stderr(self):
        """Тест с реальным файлом для stderr"""
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp_file:
            filename = tmp_file.name

            with Redirect(stderr=tmp_file):
                import sys
                print("Error to file", file=sys.stderr)

        with open(filename, 'r') as f:
            content = f.read()
            self.assertIn("Error to file", content)

        os.unlink(filename)

    def test_with_real_files_both(self):
        """Тест с реальными файлами для обоих потоков"""
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as out_file:
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as err_file:
                out_filename = out_file.name
                err_filename = err_file.name

                with Redirect(stdout=out_file, stderr=err_file):
                    print("Stdout content")
                    import sys
                    print("Stderr content", file=sys.stderr)

        # Проверяем содержимое
        with open(out_filename, 'r') as f:
            self.assertIn("Stdout content", f.read())

        with open(err_filename, 'r') as f:
            self.assertIn("Stderr content", f.read())

        os.unlink(out_filename)
        os.unlink(err_filename)

    # ==================== Тесты вложенных блоков ====================

    def test_nested_redirects(self):
        """Тест: вложенные перенаправления"""
        inner_stdout = io.StringIO()
        outer_stdout = io.StringIO()

        with Redirect(stdout=outer_stdout):
            print("Outer output")

            with Redirect(stdout=inner_stdout):
                print("Inner output")

            print("Back to outer")

        outer_stdout.seek(0)
        inner_stdout.seek(0)

        self.assertIn("Outer output", outer_stdout.read())
        self.assertIn("Back to outer", outer_stdout.read())
        self.assertIn("Inner output", inner_stdout.read())

    def test_nested_redirects_with_stderr(self):
        """Тест: вложенные перенаправления с stderr"""
        inner_stderr = io.StringIO()
        outer_stderr = io.StringIO()

        with Redirect(stderr=outer_stderr):
            import sys
            print("Outer error", file=sys.stderr)

            with Redirect(stderr=inner_stderr):
                print("Inner error", file=sys.stderr)

            print("Back to outer error", file=sys.stderr)

        outer_stderr.seek(0)
        inner_stderr.seek(0)

        outer_content = outer_stderr.read()
        inner_content = inner_stderr.read()

        self.assertIn("Outer error", outer_content)
        self.assertIn("Back to outer error", outer_content)
        self.assertIn("Inner error", inner_content)

    # ==================== Тесты с частичным перенаправлением ====================

    def test_redirect_stdout_only_with_exception(self):
        """Тест: перенаправление только stdout при исключении"""
        original_stdout = sys.stdout

        try:
            with Redirect(stdout=self.stdout_file):
                print("This goes to file")
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Проверяем, что stdout восстановлен
        self.assertIs(sys.stdout, original_stdout)

        # Проверяем содержимое stdout
        self.stdout_file.seek(0)
        self.assertIn("This goes to file", self.stdout_file.read())

    def test_redirect_stderr_only_with_exception(self):
        """Тест: перенаправление только stderr при исключении"""
        original_stderr = sys.stderr

        try:
            with Redirect(stderr=self.stderr_file):
                import sys
                print("Error to file", file=sys.stderr)
                raise ValueError("Test exception")
        except ValueError:
            pass

        self.assertIs(sys.stderr, original_stderr)

        self.stderr_file.seek(0)
        self.assertIn("Error to file", self.stderr_file.read())

    # ==================== Тесты с traceback ====================

    def test_redirect_stderr_with_traceback(self):
        """Тест: перенаправление stderr с traceback"""
        import traceback

        try:
            with Redirect(stderr=self.stderr_file):
                raise ValueError("Exception with traceback")
        except ValueError:
            traceback.print_exc()

        self.stderr_file.seek(0)
        content = self.stderr_file.read()
        self.assertIn("ValueError", content)
        self.assertIn("Exception with traceback", content)

    # ==================== Тесты без аргументов ====================

    def test_no_arguments(self):
        """Тест: контекстный менеджер без аргументов"""
        original_stdout = sys.stdout
        original_stderr = sys.stderr

        with Redirect():
            # Потоки не должны измениться
            self.assertIs(sys.stdout, original_stdout)
            self.assertIs(sys.stderr, original_stderr)

        self.assertIs(sys.stdout, original_stdout)
        self.assertIs(sys.stderr, original_stderr)

    # ==================== Тесты с частичным перенаправлением ====================

    def test_redirect_stdout_only_no_stderr(self):
        """Тест: перенаправление только stdout, stderr не меняется"""
        original_stderr = sys.stderr

        with Redirect(stdout=self.stdout_file):
            self.assertIs(sys.stderr, original_stderr)
            print("To stdout")

        self.assertIs(sys.stderr, original_stderr)

        self.stdout_file.seek(0)
        self.assertIn("To stdout", self.stdout_file.read())

    def test_redirect_stderr_only_no_stdout(self):
        """Тест: перенаправление только stderr, stdout не меняется"""
        original_stdout = sys.stdout

        with Redirect(stderr=self.stderr_file):
            self.assertIs(sys.stdout, original_stdout)
            import sys
            print("To stderr", file=sys.stderr)

        self.assertIs(sys.stdout, original_stdout)

        self.stderr_file.seek(0)
        self.assertIn("To stderr", self.stderr_file.read())


if __name__ == '__main__':
    # Запуск тестов с перенаправлением вывода в файл
    with open('test_results.txt', 'a') as test_file_stream:
        runner = unittest.TextTestRunner(stream=test_file_stream, verbosity=2)
        unittest.main(testRunner=runner, exit=False)

    # Также выводим результаты в консоль
    print("\n" + "=" * 50)
    print("Тесты завершены. Результаты сохранены в test_results.txt")