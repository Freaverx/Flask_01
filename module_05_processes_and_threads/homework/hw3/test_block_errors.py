import unittest
from block_errors import BlockErrors


class TestBlockErrors(unittest.TestCase):
    """Тесты для контекстного менеджера BlockErrors"""

    # ==================== Тесты игнорирования ошибок ====================

    def test_ignore_specific_error(self):
        """Тест: игнорирование конкретного типа ошибки"""
        executed = False

        with BlockErrors({ZeroDivisionError}):
            a = 1 / 0
            executed = True

        self.assertTrue(executed, "Код после ошибки должен выполниться")

    def test_ignore_multiple_errors(self):
        """Тест: игнорирование нескольких типов ошибок"""
        executed = False

        with BlockErrors({ZeroDivisionError, TypeError}):
            a = 1 / 0
            executed = True

        self.assertTrue(executed)

    def test_ignore_base_exception(self):
        """Тест: игнорирование базового класса Exception"""
        executed = False

        with BlockErrors({Exception}):
            a = 1 / 0
            executed = True

        self.assertTrue(executed)

    def test_ignore_child_exception(self):
        """Тест: игнорирование дочернего исключения"""
        executed = False

        with BlockErrors({ArithmeticError}):  # Родитель ZeroDivisionError
            a = 1 / 0
            executed = True

        self.assertTrue(executed, "Дочернее исключение должно игнорироваться")

    def test_ignore_key_error(self):
        """Тест: игнорирование KeyError"""
        executed = False

        with BlockErrors({KeyError}):
            d = {}
            x = d['nonexistent']
            executed = True

        self.assertTrue(executed)

    def test_ignore_multiple_errors_in_one_block(self):
        """Тест: игнорирование разных ошибок в одном блоке"""
        results = []

        with BlockErrors({ZeroDivisionError, KeyError, ValueError}):
            # Первая ошибка
            try:
                a = 1 / 0
            except ZeroDivisionError:
                results.append("ZeroDivisionError caught and ignored")

            # Вторая ошибка
            try:
                d = {}
                x = d['key']
            except KeyError:
                results.append("KeyError caught and ignored")

            # Третья ошибка
            try:
                int('abc')
            except ValueError:
                results.append("ValueError caught and ignored")

        self.assertEqual(len(results), 3)

    # ==================== Тесты проброса ошибок ====================

    def test_propagate_unexpected_error(self):
        """Тест: проброс неожидаемого исключения"""
        with self.assertRaises(TypeError):
            with BlockErrors({ZeroDivisionError}):
                a = 1 / '0'  # TypeError не в списке игнорируемых

    def test_propagate_error_not_in_list(self):
        """Тест: проброс ошибки, не входящей в список"""
        with self.assertRaises(ValueError):
            with BlockErrors({ZeroDivisionError, TypeError}):
                int('abc')  # ValueError не в списке

    def test_no_exception_no_propagation(self):
        """Тест: без исключений всё работает нормально"""
        result = None

        with BlockErrors({ZeroDivisionError}):
            result = 2 + 2

        self.assertEqual(result, 4)

    # ==================== Тесты вложенных блоков ====================

    def test_nested_blocks_outer_ignores(self):
        """Тест: вложенные блоки, внешний игнорирует"""
        outer_executed = False
        inner_executed = False

        with BlockErrors({TypeError}):
            try:
                with BlockErrors({ZeroDivisionError}):
                    a = 1 / '0'  # TypeError
                    inner_executed = True
            except TypeError:
                pass
            outer_executed = True

        self.assertFalse(inner_executed)
        self.assertTrue(outer_executed)

    def test_nested_blocks_inner_ignores_outer_propagates(self):
        """Тест: внутренний блок игнорирует, внешний пробрасывает"""
        outer_executed = False

        try:
            with BlockErrors({TypeError}):
                with BlockErrors({ZeroDivisionError}):
                    a = 1 / 0  # ZeroDivisionError
                outer_executed = True
        except ZeroDivisionError:
            pass

        self.assertFalse(outer_executed)

    def test_nested_blocks_both_ignore(self):
        """Тест: оба блока игнорируют"""
        inner_executed = False
        outer_executed = False

        with BlockErrors({TypeError}):
            with BlockErrors({ZeroDivisionError}):
                a = 1 / 0
                inner_executed = True
            outer_executed = True

        self.assertTrue(inner_executed)
        self.assertTrue(outer_executed)

    def test_deep_nested_blocks(self):
        """Тест: глубоко вложенные блоки"""
        results = []

        with BlockErrors({ValueError}):
            results.append("Level 1")
            with BlockErrors({TypeError}):
                results.append("Level 2")
                with BlockErrors({ZeroDivisionError}):
                    a = 1 / 0  # ZeroDivisionError игнорируется
                    results.append("Level 3")
                results.append("Level 2 end")
            results.append("Level 1 end")

        self.assertEqual(len(results), 4)
        self.assertEqual(results[0], "Level 1")
        self.assertEqual(results[1], "Level 2")
        self.assertEqual(results[2], "Level 3")
        self.assertEqual(results[3], "Level 2 end")

    # ==================== Тесты с разными типами коллекций ====================

    def test_with_set(self):
        """Тест с set"""
        executed = False

        with BlockErrors({ZeroDivisionError}):
            a = 1 / 0
            executed = True

        self.assertTrue(executed)

    def test_with_list(self):
        """Тест с list"""
        executed = False

        with BlockErrors([ZeroDivisionError]):
            a = 1 / 0
            executed = True

        self.assertTrue(executed)

    def test_with_tuple(self):
        """Тест с tuple"""
        executed = False

        with BlockErrors((ZeroDivisionError,)):
            a = 1 / 0
            executed = True

        self.assertTrue(executed)

    # ==================== Тесты с пользовательскими исключениями ====================

    class CustomError(Exception):
        pass

    class ChildCustomError(CustomError):
        pass

    def test_custom_exception_ignore(self):
        """Тест: игнорирование пользовательского исключения"""
        executed = False

        with BlockErrors({self.CustomError}):
            raise self.CustomError("Test error")
            executed = True

        self.assertTrue(executed)

    def test_custom_child_exception_ignore(self):
        """Тест: игнорирование дочернего пользовательского исключения"""
        executed = False

        with BlockErrors({self.CustomError}):
            raise self.ChildCustomError("Test error")
            executed = True

        self.assertTrue(executed)

    def test_custom_exception_propagate(self):
        """Тест: проброс пользовательского исключения"""
        with self.assertRaises(self.CustomError):
            with BlockErrors({ZeroDivisionError}):
                raise self.CustomError("Test error")

    # ==================== Тесты с несколькими исключениями ====================

    def test_multiple_exceptions_same_block(self):
        """Тест: несколько исключений в одном блоке"""
        counter = 0

        with BlockErrors({ZeroDivisionError, ValueError}):
            try:
                a = 1 / 0
            except ZeroDivisionError:
                counter += 1

            try:
                int('abc')
            except ValueError:
                counter += 1

        self.assertEqual(counter, 2)

    # ==================== Тесты с пустым списком ошибок ====================

    def test_empty_error_list(self):
        """Тест: пустой список ошибок (все ошибки пробрасываются)"""
        with self.assertRaises(ZeroDivisionError):
            with BlockErrors({}):
                a = 1 / 0


if __name__ == '__main__':
    unittest.main(verbosity=2)
