import unittest

from io import StringIO
from module_03_ci_culture_beginning.homework.hw2.decrypt import decrypt


class TestDecryptBasic(unittest.TestCase):
    """Базовые тесты дешифратора"""

    def test_decrypt_single_dot(self):
        """Тесты с одной точкой"""
        test_cases = [
            ('абра-кадабра.', 'абра-кадабра'),
            ('hello world.', 'hello world'),
            ('test.', 'test'),
            ('a.', 'a'),
            ('привет.', 'привет'),
        ]

        for encrypted, expected in test_cases:
            with self.subTest(encrypted=encrypted):
                result = decrypt(encrypted)
                self.assertEqual(result, expected)

    def test_decrypt_double_dot(self):
        """Тесты с двумя точками"""
        test_cases = [
            ('абраа..-кадабра', 'абра-кадабра'),
            ('hello.. world', 'he world'),
            ('a..b', 'b'),
            ('ab..', ''),
            ('1..2', '2'),
        ]

        for encrypted, expected in test_cases:
            with self.subTest(encrypted=encrypted):
                result = decrypt(encrypted)
                self.assertEqual(result, expected)

    def test_decrypt_three_dots(self):
        """Тесты с тремя точками"""
        test_cases = [
            ('абрау...-кадабра', 'абра-кадабра'),
            ('abc...def', 'adef'),
            ('1...2...3', '3'),
            ('test...', ''),
        ]

        for encrypted, expected in test_cases:
            with self.subTest(encrypted=encrypted):
                result = decrypt(encrypted)
                self.assertEqual(result, expected)

    def test_decrypt_mixed_dots(self):
        """Тесты со смешанными точками"""
        test_cases = [
            ('абраа..-.кадабра', 'абра-кадабра'),
            ('a..b.c', 'bc'),
            ('ab...c.d', 'd'),
            ('1..2.3', '23'),
            ('a.b..c', 'ac'),
        ]

        for encrypted, expected in test_cases:
            with self.subTest(encrypted=encrypted):
                result = decrypt(encrypted)
                self.assertEqual(result, expected)


class TestDecryptFromAssignment(unittest.TestCase):
    """Тесты из задания"""

    def test_examples_from_assignment(self):
        """Все примеры из условия задачи"""
        test_cases = [
            ('абра-кадабра.', 'абра-кадабра'),
            ('абраа..-кадабра', 'абра-кадабра'),
            ('абраа..-.кадабра', 'абра-кадабра'),
            ('абра--..кадабра', 'абра-кадабра'),
            ('абрау...-кадабра', 'абра-кадабра'),
            ('абра........', ''),
            ('абр......a.', 'a'),
            ('1..2.3', '23'),
            ('.', ''),
            ('1.......................', ''),
        ]

        for encrypted, expected in test_cases:
            with self.subTest(encrypted=encrypted, expected=expected):
                result = decrypt(encrypted)
                self.assertEqual(result, expected)


class TestDecryptEdgeCases(unittest.TestCase):
    """Тесты граничных случаев"""

    def test_empty_string(self):
        """Тест пустой строки"""
        self.assertEqual(decrypt(''), '')

    def test_only_dots(self):
        """Тесты с только точками"""
        test_cases = [
            ('.', ''),
            ('..', ''),
            ('...', ''),
            ('....', ''),
            ('........', ''),
            ('.......................', ''),
        ]

        for dots in test_cases:
            with self.subTest(dots=dots[0]):
                result = decrypt(dots[0])
                self.assertEqual(result, dots[1])

    def test_no_dots(self):
        """Тесты без точек"""
        test_cases = [
            ('hello', 'hello'),
            ('world', 'world'),
            ('привет', 'привет'),
            ('12345', '12345'),
            ('a-b-c', 'a-b-c'),
        ]

        for encrypted, expected in test_cases:
            with self.subTest(encrypted=encrypted):
                result = decrypt(encrypted)
                self.assertEqual(result, expected)

    def test_consecutive_double_dots(self):
        """Тесты с последовательными двойными точками"""
        test_cases = [
            ('a..b..c', 'c'),
            ('ab..cd..', ''),
            ('1..2..3..4', '4'),
            ('a..b..c..d..', ''),
        ]

        for encrypted, expected in test_cases:
            with self.subTest(encrypted=encrypted):
                result = decrypt(encrypted)
                self.assertEqual(result, expected)

    def test_dots_at_beginning(self):
        """Тесты с точками в начале строки"""
        test_cases = [
            ('.a', 'a'),
            ('..a', 'a'),
            ('...a', 'a'),
            ('..a..b', 'b'),
        ]

        for encrypted, expected in test_cases:
            with self.subTest(encrypted=encrypted):
                result = decrypt(encrypted)
                self.assertEqual(result, expected)

    def test_dots_at_end(self):
        """Тесты с точками в конце строки"""
        test_cases = [
            ('a.', 'a'),
            ('a..', ''),
            ('a...', ''),
            ('ab..', ''),
        ]

        for encrypted, expected in test_cases:
            with self.subTest(encrypted=encrypted):
                result = decrypt(encrypted)
                self.assertEqual(result, expected)

    def test_dots_in_middle(self):
        """Тесты с точками в середине строки"""
        test_cases = [
            ('he.llo', 'hello'),
            ('he..llo', 'hlo'),
            ('he...llo', 'hlo'),
            ('he....llo', 'hlo'),
        ]

        for encrypted, expected in test_cases:
            with self.subTest(encrypted=encrypted):
                result = decrypt(encrypted)
                self.assertEqual(result, expected)

    def test_special_characters(self):
        """Тесты со специальными символами"""
        test_cases = [
            ('абра-кадабра.', 'абра-кадабра'),
            ('абра--..кадабра', 'абра-кадабра'),
            ('hello-world.', 'hello-world'),
            ('test_123..', ''),
            ('a@b.c', 'a@c'),
        ]

        for encrypted, expected in test_cases:
            with self.subTest(encrypted=encrypted):
                result = decrypt(encrypted)
                self.assertEqual(result, expected)

    def test_long_string(self):
        """Тесты с длинными строками"""
        # Создаём длинную строку для тестирования производительности
        long_string = 'a' * 1000 + '..' * 500
        expected = ''  # Каждые две точки удаляют символ

        with self.subTest(description="Long string with many dots"):
            result = decrypt(long_string)
            self.assertEqual(result, expected)

        # Строка с чередованием символов и точек
        alternating = ''.join([f'{i}..' for i in range(100)])
        expected = ''  # Каждый символ удаляется следующей двойной точкой

        with self.subTest(description="Alternating pattern"):
            result = decrypt(alternating)
            self.assertEqual(result, expected)


class TestDecryptComplexScenarios(unittest.TestCase):
    """Тесты сложных сценариев"""

    def test_multiple_rules_combined(self):
        """Тесты с комбинацией различных правил"""
        test_cases = [
            ('a.b..c.d..e', 'ace'),  # a, b удаляется, c, d удаляется, e
            ('1.2..3.4..5', '135'),  # 1, 2 удаляется, 3, 4 удаляется, 5
            ('ab.cd..ef.gh..', 'abef'),  # ab, cd удаляется, ef, gh удаляется
            ('test..123.456..789', 't123789'),  # te удаляется, st... (сложный случай)
        ]

        for encrypted, expected in test_cases:
            with self.subTest(encrypted=encrypted):
                result = decrypt(encrypted)
                self.assertEqual(result, expected)

    def test_nested_deletions(self):
        """Тесты с вложенными удалениями"""
        test_cases = [
            ('a..b..c', 'c'),  # Удаляем a, затем b
            ('ab..c..d', 'd'),  # Удаляем ab, затем c
            ('a.b..c', 'ac'),  # a, b удаляется, c
            ('a..b.c', 'bc'),  # a удаляется, b, c
        ]

        for encrypted, expected in test_cases:
            with self.subTest(encrypted=encrypted):
                result = decrypt(encrypted)
                self.assertEqual(result, expected)

    def test_sequential_processing(self):
        """Тесты последовательной обработки"""
        # Проверяем, что обработка идёт слева направо
        test_cases = [
            ('a..b', 'b'),  # a удаляется
            ('a..b..', ''),  # a и b удаляются
            ('a..b.c', 'bc'),  # a удаляется, b, c
            ('a.b..c', 'ac'),  # a, b удаляется, c
        ]

        for encrypted, expected in test_cases:
            with self.subTest(encrypted=encrypted):
                result = decrypt(encrypted)
                self.assertEqual(result, expected)


class TestDecryptInputOutput(unittest.TestCase):
    """Тесты ввода-вывода дешифратора"""

    def test_stdin_reading(self):
        """Тест чтения из стандартного ввода"""
        from module_03_ci_culture_beginning.homework.hw2.decrypt import decrypt
        import sys

        # Сохраняем оригинальный stdin
        original_stdin = sys.stdin

        try:
            # Подменяем stdin тестовыми данными
            test_input = 'абраа..-.кадабра\n'
            sys.stdin = StringIO(test_input)

            # Читаем данные
            encrypted = sys.stdin.read().strip()
            result = decrypt(encrypted)

            self.assertEqual(result, 'абра-кадабра')
        finally:
            # Восстанавливаем stdin
            sys.stdin = original_stdin


if __name__ == '__main__':
    # Запуск с подробным выводом
    unittest.main(verbosity=2)