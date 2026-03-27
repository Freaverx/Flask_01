import unittest

from module_03_ci_culture_beginning.homework.hw3.accounting import app, storage



class TestAccountingApp(unittest.TestCase):
    """Тесты для приложения учёта финансов"""

    @classmethod
    def setUpClass(cls):
        """Создаём тестовый клиент и заполняем начальные данные"""
        cls.app = app.test_client()
        cls.app.testing = True

        # Очищаем storage перед всеми тестами
        cls._clear_storage()

    @classmethod
    def _clear_storage(cls):
        """Очищает хранилище"""
        storage.clear()

    def setUp(self):
        """Очищаем storage перед каждым тестом"""
        self._clear_storage()

    # ==================== Тесты для /add/ endpoint ====================

    def test_add_valid_expense(self):
        """Тест добавления корректной траты"""
        response = self.app.get('/add/20240322/500')
        self.assertEqual(response.status_code, 200)

        response_text = response.data.decode()
        self.assertIn('Добавлена трата в размере 500 руб.', response_text)
        self.assertIn('2024-03-22', response_text)

        # Проверяем, что данные сохранились в storage
        self.assertEqual(storage[2024][3], 500)

    def test_add_multiple_expenses_same_day(self):
        """Тест добавления нескольких трат за один день"""
        # Добавляем две траты за один день
        self.app.get('/add/20240322/500')
        self.app.get('/add/20240322/300')

        # Проверяем сумму
        self.assertEqual(storage[2024][3], 800)

    def test_add_multiple_expenses_same_month_different_days(self):
        """Тест добавления трат за разные дни одного месяца"""
        self.app.get('/add/20240322/500')
        self.app.get('/add/20240323/300')
        self.app.get('/add/20240324/200')

        # Проверяем сумму за месяц
        self.assertEqual(storage[2024][3], 1000)

    def test_add_multiple_expenses_different_months(self):
        """Тест добавления трат за разные месяцы"""
        self.app.get('/add/20240322/500')
        self.app.get('/add/20240422/300')

        self.assertEqual(storage[2024][3], 500)
        self.assertEqual(storage[2024][4], 300)

    def test_add_expense_with_zero_amount(self):
        """Тест добавления траты с нулевой суммой"""
        response = self.app.get('/add/20240322/0')
        self.assertEqual(response.status_code, 400)

        response_text = response.data.decode()
        self.assertIn('сумма траты должна быть положительным числом', response_text)

        # Проверяем, что данные не сохранились
        self.assertEqual(storage.get(2024, {}).get(3, 0), 0)

    def test_add_expense_with_negative_amount(self):
        """Тест добавления траты с отрицательной суммой"""
        response = self.app.get('/add/20240322/-100')
        self.assertEqual(response.status_code, 400)

        response_text = response.data.decode()
        self.assertIn('сумма траты должна быть положительным числом', response_text)

        # Проверяем, что данные не сохранились
        self.assertEqual(storage.get(2024, {}).get(3, 0), 0)

    def test_add_expense_invalid_date_format(self):
        """Тест добавления траты с неверным форматом даты"""
        test_cases = [
            ('2024032', 'слишком короткая'),
            ('202403221', 'слишком длинная'),
            ('2024-03-22', 'с разделителями'),
            ('22.03.2024', 'в другом формате'),
            ('abcd1234', 'с буквами'),
        ]

        for date_str, description in test_cases:
            with self.subTest(date=date_str, description=description):
                response = self.app.get(f'/add/{date_str}/500')
                self.assertEqual(response.status_code, 400)

                response_text = response.data.decode()
                self.assertIn('неверный формат даты', response_text.lower())

    def test_add_expense_invalid_month(self):
        """Тест добавления траты с неверным месяцем"""
        test_cases = [
            ('20240022', 0, 'месяц 0'),
            ('20241322', 13, 'месяц 13'),
            ('20241522', 15, 'месяц 15'),
        ]

        for date_str, month, description in test_cases:
            with self.subTest(date=date_str, description=description):
                response = self.app.get(f'/add/{date_str}/500')
                self.assertEqual(response.status_code, 400)

                response_text = response.data.decode()
                self.assertIn('месяц должен быть от 1 до 12', response_text)

    def test_add_expense_invalid_day(self):
        """Тест добавления траты с неверным днём"""
        test_cases = [
            ('20240300', 0, 'день 0'),
            ('20240332', 32, 'день 32'),
            ('20240431', 31, '31 апреля'),  # В апреле 30 дней
            ('20240230', 30, '30 февраля'),  # В феврале 28/29 дней
        ]

        for date_str, day, description in test_cases:
            with self.subTest(date=date_str, description=description):
                response = self.app.get(f'/add/{date_str}/500')
                # Ожидаем, что такая дата будет отклонена (или 400, или 500)
                # Flask может попытаться создать datetime и выбросить ValueError
                self.assertIn(response.status_code, [400, 500])

    def test_add_expense_leap_year(self):
        """Тест добавления траты в високосный год (29 февраля)"""
        # 2024 - високосный год
        response = self.app.get('/add/20240229/500')
        self.assertEqual(response.status_code, 200)

        response_text = response.data.decode()
        self.assertIn('Добавлена трата', response_text)

        # Проверяем, что данные сохранились
        self.assertEqual(storage[2024][2], 500)

    def test_add_expense_non_leap_year(self):
        """Тест добавления траты в невисокосный год (29 февраля)"""
        # 2023 - невисокосный год
        response = self.app.get('/add/20230229/500')
        self.assertIn(response.status_code, [400, 500])

    # ==================== Тесты для /calculate/year endpoint ====================

    def test_calculate_year_with_data(self):
        """Тест расчёта за год с данными"""
        # Добавляем тестовые данные
        self.app.get('/add/20240322/500')
        self.app.get('/add/20240323/300')
        self.app.get('/add/20240422/200')
        self.app.get('/add/20240522/100')

        response = self.app.get('/calculate/2024')
        self.assertEqual(response.status_code, 200)

        response_text = response.data.decode()
        self.assertIn('Суммарные траты за 2024 год: 1100 руб.', response_text)

    def test_calculate_year_empty_storage(self):
        """Тест расчёта за год при пустом хранилище"""
        response = self.app.get('/calculate/2024')
        self.assertEqual(response.status_code, 200)

        response_text = response.data.decode()
        self.assertIn('Суммарные траты за 2024 год: 0 руб.', response_text)

    def test_calculate_year_multiple_years(self):
        """Тест расчёта за год с данными за несколько лет"""
        self.app.get('/add/20230322/1000')
        self.app.get('/add/20240322/500')
        self.app.get('/add/20250322/2000')

        # Проверяем 2023 год
        response_2023 = self.app.get('/calculate/2023')
        self.assertIn('Суммарные траты за 2023 год: 1000 руб.', response_2023.data.decode())

        # Проверяем 2024 год
        response_2024 = self.app.get('/calculate/2024')
        self.assertIn('Суммарные траты за 2024 год: 500 руб.', response_2024.data.decode())

        # Проверяем 2025 год
        response_2025 = self.app.get('/calculate/2025')
        self.assertIn('Суммарные траты за 2025 год: 2000 руб.', response_2025.data.decode())

    def test_calculate_year_accumulative(self):
        """Тест, что траты суммируются правильно при добавлении"""
        # Добавляем траты и проверяем после каждого добавления
        self.assertEqual(storage.get(2024, {}).get(3, 0), 0)

        self.app.get('/add/20240322/100')
        response = self.app.get('/calculate/2024')
        self.assertIn('100 руб.', response.data.decode())

        self.app.get('/add/20240323/200')
        response = self.app.get('/calculate/2024')
        self.assertIn('300 руб.', response.data.decode())

        self.app.get('/add/20240324/300')
        response = self.app.get('/calculate/2024')
        self.assertIn('600 руб.', response.data.decode())

    # ==================== Тесты для /calculate/year/month endpoint ====================

    def test_calculate_month_with_data(self):
        """Тест расчёта за месяц с данными"""
        self.app.get('/add/20240322/500')
        self.app.get('/add/20240323/300')
        self.app.get('/add/20240422/200')

        response = self.app.get('/calculate/2024/3')
        self.assertEqual(response.status_code, 200)

        response_text = response.data.decode()
        self.assertIn('Суммарные траты за 2024-03: 800 руб.', response_text)

    def test_calculate_month_empty_storage(self):
        """Тест расчёта за месяц при пустом хранилище"""
        response = self.app.get('/calculate/2024/3')
        self.assertEqual(response.status_code, 200)

        response_text = response.data.decode()
        self.assertIn('Суммарные траты за 2024-03: 0 руб.', response_text)

    def test_calculate_month_invalid_month(self):
        """Тест расчёта за месяц с неверным номером месяца"""
        test_cases = [
            (0, 'месяц 0'),
            (13, 'месяц 13'),
            (-1, 'отрицательный месяц'),
        ]

        for month, description in test_cases:
            with self.subTest(month=month, description=description):
                response = self.app.get(f'/calculate/2024/{month}')
                self.assertEqual(response.status_code, 400)

                response_text = response.data.decode()
                self.assertIn('месяц должен быть от 1 до 12', response_text)

    def test_calculate_month_multiple_months(self):
        """Тест расчёта за разные месяцы"""
        self.app.get('/add/20240322/500')
        self.app.get('/add/20240422/300')
        self.app.get('/add/20240522/200')

        response_mar = self.app.get('/calculate/2024/3')
        self.assertIn('500 руб.', response_mar.data.decode())

        response_apr = self.app.get('/calculate/2024/4')
        self.assertIn('300 руб.', response_apr.data.decode())

        response_may = self.app.get('/calculate/2024/5')
        self.assertIn('200 руб.', response_may.data.decode())

    def test_calculate_month_same_month_different_years(self):
        """Тест расчёта за один и тот же месяц разных лет"""
        self.app.get('/add/20230322/1000')
        self.app.get('/add/20240322/500')
        self.app.get('/add/20250322/2000')

        response_2023 = self.app.get('/calculate/2023/3')
        self.assertIn('1000 руб.', response_2023.data.decode())

        response_2024 = self.app.get('/calculate/2024/3')
        self.assertIn('500 руб.', response_2024.data.decode())

        response_2025 = self.app.get('/calculate/2025/3')
        self.assertIn('2000 руб.', response_2025.data.decode())

    def test_calculate_month_after_deletions(self):
        """Тест расчёта после добавления и удаления (имитация)"""
        # В нашем приложении нет удаления, просто проверяем добавление
        self.app.get('/add/20240322/500')
        self.app.get('/add/20240322/300')

        response = self.app.get('/calculate/2024/3')
        self.assertIn('800 руб.', response.data.decode())

    # ==================== Тесты для интеграции ====================

    def test_full_workflow(self):
        """Тест полного рабочего процесса"""
        # Добавляем траты
        self.app.get('/add/20240322/500')
        self.app.get('/add/20240323/300')
        self.app.get('/add/20240422/200')
        self.app.get('/add/20240423/100')
        self.app.get('/add/20240522/400')

        # Проверяем траты за март
        response_mar = self.app.get('/calculate/2024/3')
        self.assertIn('800 руб.', response_mar.data.decode())

        # Проверяем траты за апрель
        response_apr = self.app.get('/calculate/2024/4')
        self.assertIn('300 руб.', response_apr.data.decode())

        # Проверяем траты за май
        response_may = self.app.get('/calculate/2024/5')
        self.assertIn('400 руб.', response_may.data.decode())

        # Проверяем траты за весь год
        response_year = self.app.get('/calculate/2024')
        self.assertIn('1500 руб.', response_year.data.decode())

    def test_data_persistence_between_requests(self):
        """Тест сохранения данных между запросами"""
        # Первый запрос на добавление
        self.app.get('/add/20240322/500')

        # Второй запрос на получение
        response = self.app.get('/calculate/2024/3')
        self.assertIn('500 руб.', response.data.decode())

        # Третий запрос на добавление ещё
        self.app.get('/add/20240323/300')

        # Четвёртый запрос на проверку суммы
        response = self.app.get('/calculate/2024/3')
        self.assertIn('800 руб.', response.data.decode())

    def test_large_numbers(self):
        """Тест с большими числами"""
        self.app.get('/add/20240322/1000000')
        self.app.get('/add/20240323/2000000')

        response = self.app.get('/calculate/2024/3')
        self.assertIn('3000000 руб.', response.data.decode())

        response_year = self.app.get('/calculate/2024')
        self.assertIn('3000000 руб.', response_year.data.decode())


class TestAccountingAppEdgeCases(unittest.TestCase):
    """Тесты граничных случаев"""

    @classmethod
    def setUpClass(cls):
        cls.app = app.test_client()
        cls.app.testing = True

    def setUp(self):
        """Очищаем storage перед каждым тестом"""
        storage.clear()

    def test_boundary_date_values(self):
        """Тест граничных значений дат"""
        test_cases = [
            ('20240101', 1, 1, '1 января'),
            ('20241231', 12, 31, '31 декабря'),
            ('20240228', 2, 28, '28 февраля (невисокосный)'),
            ('20240229', 2, 29, '29 февраля (високосный)'),
        ]

        for date_str, month, day, description in test_cases:
            with self.subTest(date=date_str, description=description):
                response = self.app.get(f'/add/{date_str}/100')
                if date_str == '20240229':
                    # 2024 - високосный
                    self.assertEqual(response.status_code, 200)
                else:
                    self.assertEqual(response.status_code, 200)

    def test_maximum_integer_value(self):
        """Тест с максимальным значением int"""
        max_int = 2 ** 31 - 1  # 2147483647
        response = self.app.get(f'/add/20240322/{max_int}')
        self.assertEqual(response.status_code, 200)

        response_text = response.data.decode()
        self.assertIn(str(max_int), response_text)


if __name__ == '__main__':
    unittest.main(verbosity=2)