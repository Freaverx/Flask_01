import unittest
from module_03_ci_culture_beginning.homework.hw1.hello_word_with_name import app
from freezegun import freeze_time


class TestHelloWorldApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()
        self.base_url = '/hello-world/'

    def test_can_get_correct_username_with_name(self):
        username = 'username'
        response = self.app.get(self.base_url + username)
        response_text = response.data.decode()
        self.assertTrue(username in response_text)

    def test_can_get_correct_weekday(self):
        """Тест корректности вернувшегося дня недели"""
        username = 'username'
        test_dates = {
            '2024-03-25': 'понедельник',
            '2024-03-26': 'вторник',
            '2024-03-27': 'среда',
            '2024-03-28': 'четверг',
            '2024-03-29': 'пятница',
            '2024-03-30': 'суббота',
            '2024-03-31': 'воскресенье',
        }

        for date_str, expected_weekday in test_dates.items():
            with freeze_time(date_str):
                response = self.app.get(self.base_url + username)
                response_text = response.data.decode()

                self.assertTrue(username in response_text)
                self.assertIn(expected_weekday, response_text)
                self.assertIn(f'Хорошего {expected_weekday}!', response_text)


if __name__ == '__main__':
    unittest.main()