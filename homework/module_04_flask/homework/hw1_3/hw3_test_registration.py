"""
Для каждого поля и валидатора в эндпоинте /registration напишите юнит-тест,
который проверит корректность работы валидатора. Таким образом, нужно проверить, что существуют наборы данных,
которые проходят валидацию, и такие, которые валидацию не проходят.
"""

import unittest
from hw1_registration import app


class TestRegistrationForm(unittest.TestCase):
    """Тесты для формы регистрации"""

    def setUp(self):
        """Подготовка к тестам"""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    # ==================== Тесты для поля email ====================

    def test_email_valid_cases(self):
        """Тест валидных email адресов"""
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user+label@example.com",
            "user@subdomain.example.com",
            "user@example.co.uk",
            "user123@example.com",
            "user_name@example.com"
        ]

        for email in valid_emails:
            with self.subTest(email=email):
                data = {
                    'email': email,
                    'phone': 1234567890,
                    'name': 'Test User',
                    'address': 'Test Address',
                    'index': 123456,
                    'comment': 'Test comment'
                }
                response = self.client.post('/registration', data=data)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Successfully registered', response.data)

    def test_email_invalid_cases(self):
        """Тест невалидных email адресов"""
        invalid_emails = [
            ("invalid-email", "отсутствует @"),
            ("user@", "отсутствует домен"),
            ("@example.com", "отсутствует имя пользователя"),
            ("user@example", "неполный домен"),
            ("user name@example.com", "содержит пробел"),
            ("", "пустое поле"),
            (None, "None значение"),
        ]

        for email, description in invalid_emails:
            with self.subTest(email=email, description=description):
                data = {
                    'email': email if email is not None else '',
                    'phone': 1234567890,
                    'name': 'Test User',
                    'address': 'Test Address',
                    'index': 123456,
                    'comment': 'Test comment'
                }
                response = self.client.post('/registration', data=data)
                self.assertEqual(response.status_code, 400)
                self.assertIn(b'email', response.data)

    def test_email_required(self):
        """Тест обязательности поля email"""
        data = {
            'phone': 1234567890,
            'name': 'Test User',
            'address': 'Test Address',
            'index': 123456,
            'comment': 'Test comment'
        }
        response = self.client.post('/registration', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'email', response.data)

    # ==================== Тесты для поля phone ====================

    def test_phone_valid_cases(self):
        """Тест валидных номеров телефона"""
        valid_phones = [
            1234567890,
            9999999999,
            1111111111,
            1234567890,
        ]

        for phone in valid_phones:
            with self.subTest(phone=phone):
                data = {
                    'email': 'user@example.com',
                    'phone': phone,
                    'name': 'Test User',
                    'address': 'Test Address',
                    'index': 123456,
                    'comment': 'Test comment'
                }
                response = self.client.post('/registration', data=data)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Successfully registered', response.data)

    def test_phone_invalid_length(self):
        """Тест телефонов с некорректной длиной"""
        invalid_phones = [
            (123456789, 9, "меньше 10"),
            (12345678901, 11, "больше 10"),
            (1, 1, "слишком короткий"),
            (123456789012, 12, "слишком длинный"),
            (0, 1, "ноль"),
        ]

        for phone, length, description in invalid_phones:
            with self.subTest(phone=phone, length=length, description=description):
                data = {
                    'email': 'user@example.com',
                    'phone': phone,
                    'name': 'Test User',
                    'address': 'Test Address',
                    'index': 123456,
                    'comment': 'Test comment'
                }
                response = self.client.post('/registration', data=data)
                self.assertEqual(response.status_code, 400)
                self.assertIn(b'phone', response.data)

    def test_phone_negative_number(self):
        """Тест отрицательного номера телефона"""
        data = {
            'email': 'user@example.com',
            'phone': -123456789,
            'name': 'Test User',
            'address': 'Test Address',
            'index': 123456,
            'comment': 'Test comment'
        }
        response = self.client.post('/registration', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'phone', response.data)

    def test_phone_with_leading_zeros(self):
        """Тест телефона с ведущими нулями (целые числа не сохраняют ведущие нули)"""
        # IntegerField не сохраняет ведущие нули, поэтому проверяем только длину
        data = {
            'email': 'user@example.com',
            'phone': 12345678,  # 8 цифр
            'name': 'Test User',
            'address': 'Test Address',
            'index': 123456,
            'comment': 'Test comment'
        }
        response = self.client.post('/registration', data=data)
        self.assertEqual(response.status_code, 400)

    def test_phone_required(self):
        """Тест обязательности поля phone"""
        data = {
            'email': 'user@example.com',
            'name': 'Test User',
            'address': 'Test Address',
            'index': 123456,
            'comment': 'Test comment'
        }
        response = self.client.post('/registration', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'phone', response.data)

    # ==================== Тесты для поля name ====================

    def test_name_valid_cases(self):
        """Тест валидных имен"""
        valid_names = [
            "Иван Петров",
            "John Doe",
            "Мария",
            "Jean-Luc",
            "Anna-Maria",
            "Test User 123",
        ]

        for name in valid_names:
            with self.subTest(name=name):
                data = {
                    'email': 'user@example.com',
                    'phone': 1234567890,
                    'name': name,
                    'address': 'Test Address',
                    'index': 123456,
                    'comment': 'Test comment'
                }
                response = self.client.post('/registration', data=data)
                self.assertEqual(response.status_code, 200)

    def test_name_empty(self):
        """Тест пустого имени"""
        data = {
            'email': 'user@example.com',
            'phone': 1234567890,
            'name': '',
            'address': 'Test Address',
            'index': 123456,
            'comment': 'Test comment'
        }
        response = self.client.post('/registration', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'name', response.data)

    def test_name_missing(self):
        """Тест отсутствия имени"""
        data = {
            'email': 'user@example.com',
            'phone': 1234567890,
            'address': 'Test Address',
            'index': 123456,
            'comment': 'Test comment'
        }
        response = self.client.post('/registration', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'name', response.data)

    # ==================== Тесты для поля address ====================

    def test_address_valid_cases(self):
        """Тест валидных адресов"""
        valid_addresses = [
            "г. Москва, ул. Тверская, д. 1",
            "Saint Petersburg, Nevsky Prospect, 1",
            "123 Main St, Apt 4B",
            "г. Новосибирск, ул. Ленина, 10",
            "Улица Пушкина, дом Колотушкина",
        ]

        for address in valid_addresses:
            with self.subTest(address=address):
                data = {
                    'email': 'user@example.com',
                    'phone': 1234567890,
                    'name': 'Test User',
                    'address': address,
                    'index': 123456,
                    'comment': 'Test comment'
                }
                response = self.client.post('/registration', data=data)
                self.assertEqual(response.status_code, 200)

    def test_address_empty(self):
        """Тест пустого адреса"""
        data = {
            'email': 'user@example.com',
            'phone': 1234567890,
            'name': 'Test User',
            'address': '',
            'index': 123456,
            'comment': 'Test comment'
        }
        response = self.client.post('/registration', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'address', response.data)

    def test_address_missing(self):
        """Тест отсутствия адреса"""
        data = {
            'email': 'user@example.com',
            'phone': 1234567890,
            'name': 'Test User',
            'index': 123456,
            'comment': 'Test comment'
        }
        response = self.client.post('/registration', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'address', response.data)

    # ==================== Тесты для поля index ====================

    def test_index_valid_cases(self):
        """Тест валидных индексов"""
        valid_indices = [
            123456,
            999999,
            100000,
            555555,
            123456,
        ]

        for index in valid_indices:
            with self.subTest(index=index):
                data = {
                    'email': 'user@example.com',
                    'phone': 1234567890,
                    'name': 'Test User',
                    'address': 'Test Address',
                    'index': index,
                    'comment': 'Test comment'
                }
                response = self.client.post('/registration', data=data)
                self.assertEqual(response.status_code, 200)

    def test_index_invalid_range(self):
        """Тест индексов с некорректным диапазоном"""
        invalid_indices = [
            (12345, 5, "меньше 6 цифр"),
            (99999, 5, "5 цифр"),
            (1000000, 7, "7 цифр"),
            (9999999, 7, "7 цифр"),
            (0, 1, "ноль"),
        ]

        for index, length, description in invalid_indices:
            with self.subTest(index=index, length=length, description=description):
                data = {
                    'email': 'user@example.com',
                    'phone': 1234567890,
                    'name': 'Test User',
                    'address': 'Test Address',
                    'index': index,
                    'comment': 'Test comment'
                }
                response = self.client.post('/registration', data=data)
                self.assertEqual(response.status_code, 400)
                self.assertIn(b'index', response.data)

    def test_index_negative(self):
        """Тест отрицательного индекса"""
        data = {
            'email': 'user@example.com',
            'phone': 1234567890,
            'name': 'Test User',
            'address': 'Test Address',
            'index': -123456,
            'comment': 'Test comment'
        }
        response = self.client.post('/registration', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'index', response.data)

    def test_index_required(self):
        """Тест обязательности поля index"""
        data = {
            'email': 'user@example.com',
            'phone': 1234567890,
            'name': 'Test User',
            'address': 'Test Address',
            'comment': 'Test comment'
        }
        response = self.client.post('/registration', data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'index', response.data)

    # ==================== Тесты для поля comment ====================

    def test_comment_optional(self):
        """Тест, что поле comment необязательно"""
        data = {
            'email': 'user@example.com',
            'phone': 1234567890,
            'name': 'Test User',
            'address': 'Test Address',
            'index': 123456,
            # comment отсутствует
        }
        response = self.client.post('/registration', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Successfully registered', response.data)

    def test_comment_empty_string(self):
        """Тест пустого комментария"""
        data = {
            'email': 'user@example.com',
            'phone': 1234567890,
            'name': 'Test User',
            'address': 'Test Address',
            'index': 123456,
            'comment': ''
        }
        response = self.client.post('/registration', data=data)
        self.assertEqual(response.status_code, 200)

    def test_comment_long_text(self):
        """Тест длинного комментария"""
        long_comment = "A" * 1000  # длинный текст
        data = {
            'email': 'user@example.com',
            'phone': 1234567890,
            'name': 'Test User',
            'address': 'Test Address',
            'index': 123456,
            'comment': long_comment
        }
        response = self.client.post('/registration', data=data)
        self.assertEqual(response.status_code, 200)

    # ==================== Интеграционные тесты ====================

    def test_all_fields_valid(self):
        """Тест всех полей с валидными данными"""
        data = {
            'email': 'user@example.com',
            'phone': 1234567890,
            'name': 'Иван Петров',
            'address': 'г. Москва, ул. Ленина, д. 1',
            'index': 123456,
            'comment': 'Пожелания: позвонить после 18:00'
        }
        response = self.client.post('/registration', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Successfully registered user user@example.com with phone +71234567890', response.data)

    def test_multiple_invalid_fields(self):
        """Тест с несколькими невалидными полями"""
        data = {
            'email': 'invalid-email',
            'phone': 123,  # слишком короткий
            'name': '',
            'address': '',
            'index': 12,  # слишком короткий
            'comment': 'Test comment'
        }
        response = self.client.post('/registration', data=data)
        self.assertEqual(response.status_code, 400)

        # Проверяем, что все ошибки присутствуют
        response_text = response.data.decode()
        self.assertIn('email', response_text)
        self.assertIn('phone', response_text)
        self.assertIn('name', response_text)
        self.assertIn('address', response_text)
        self.assertIn('index', response_text)


if __name__ == '__main__':
    unittest.main(verbosity=2)
