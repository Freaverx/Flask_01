import unittest
import datetime
from freezegun import freeze_time
from module_03_ci_culture_beginning.homework.hw4.person import Person  # предполагаем, что класс находится в файле person.py


class TestPerson(unittest.TestCase):
    """Тесты для класса Person"""

    def setUp(self):
        """Подготовка тестовых данных"""
        self.person1 = Person("Иван Петров", 1990, "Москва, ул. Ленина, д. 1")
        self.person2 = Person("Анна Сидорова", 1995)
        self.person3 = Person("Сергей Иванов", 1985, "")

    # ==================== Тесты для __init__ ====================

    def test_init_with_full_data(self):
        """Тест инициализации с полными данными"""
        person = Person("Тест Тестов", 2000, "г. Москва")
        self.assertEqual(person.name, "Тест Тестов")
        self.assertEqual(person.yob, 2000)
        self.assertEqual(person.address, "г. Москва")

    def test_init_without_address(self):
        """Тест инициализации без адреса"""
        person = Person("Тест Тестов", 2000)
        self.assertEqual(person.name, "Тест Тестов")
        self.assertEqual(person.yob, 2000)
        self.assertEqual(person.address, "")

    def test_init_with_empty_address(self):
        """Тест инициализации с пустым адресом"""
        person = Person("Тест Тестов", 2000, "")
        self.assertEqual(person.name, "Тест Тестов")
        self.assertEqual(person.yob, 2000)
        self.assertEqual(person.address, "")

    # ==================== Тесты для get_age ====================

    @freeze_time("2024-03-22")
    def test_get_age_normal(self):
        """Тест получения возраста для обычного случая"""
        # 2024 - 1990 = 34
        self.assertEqual(self.person1.get_age(), 34)
        # 2024 - 1995 = 29
        self.assertEqual(self.person2.get_age(), 29)
        # 2024 - 1985 = 39
        self.assertEqual(self.person3.get_age(), 39)

    @freeze_time("2024-03-22")
    def test_get_age_before_birthday_current_year(self):
        """Тест получения возраста, если день рождения ещё не наступил в этом году"""
        # Проверка через freeze_time с разными датами
        person = Person("Тест", 2000)

        # 2024-03-22, день рождения 2000-12-31 ещё не наступил
        with freeze_time("2024-03-22"):
            # 2024 - 2000 = 24
            self.assertEqual(person.get_age(), 24)

        # 2024-12-31, день рождения уже наступил
        with freeze_time("2024-12-31"):
            self.assertEqual(person.get_age(), 24)

        # 2025-01-01, день рождения 2000-12-31 уже был
        with freeze_time("2025-01-01"):
            self.assertEqual(person.get_age(), 25)

    @freeze_time("2024-03-22")
    def test_get_age_newborn(self):
        """Тест получения возраста для новорождённого"""
        person = Person("Младенец", 2024)
        self.assertEqual(person.get_age(), 0)

    @freeze_time("2024-03-22")
    def test_get_age_future_year(self):
        """Тест получения возраста для человека с годом рождения в будущем"""
        person = Person("Из будущего", 2030)
        self.assertEqual(person.get_age(), -6)  # Отрицательный возраст

    @freeze_time("2024-03-22")
    def test_get_age_edge_cases(self):
        """Тест граничных случаев возраста"""
        test_cases = [
            (2024, 0),  # родился в этом году
            (2023, 1),  # родился в прошлом году
            (2000, 24),  # родился 24 года назад
            (1900, 124),  # очень старый человек
        ]

        for year, expected_age in test_cases:
            with self.subTest(year=year, expected=expected_age):
                person = Person("Тест", year)
                self.assertEqual(person.get_age(), expected_age)

    # ==================== Тесты для get_name ====================

    def test_get_name(self):
        """Тест получения имени"""
        self.assertEqual(self.person1.get_name(), "Иван Петров")
        self.assertEqual(self.person2.get_name(), "Анна Сидорова")
        self.assertEqual(self.person3.get_name(), "Сергей Иванов")

    def test_get_name_after_change(self):
        """Тест получения имени после изменения"""
        self.person1.set_name("Петр Иванов")
        self.assertEqual(self.person1.get_name(), "Петр Иванов")

    def test_get_name_empty(self):
        """Тест получения пустого имени"""
        person = Person("", 2000)
        self.assertEqual(person.get_name(), "")

    def test_get_name_with_special_characters(self):
        """Тест получения имени со специальными символами"""
        person = Person("Иван-Петр II", 2000)
        self.assertEqual(person.get_name(), "Иван-Петр II")

    # ==================== Тесты для set_name ====================

    def test_set_name(self):
        """Тест установки имени"""
        person = Person("Старое имя", 2000)
        person.set_name("Новое имя")
        self.assertEqual(person.name, "Новое имя")
        self.assertEqual(person.get_name(), "Новое имя")

    def test_set_name_multiple_times(self):
        """Тест многократной установки имени"""
        person = Person("Имя1", 2000)
        person.set_name("Имя2")
        self.assertEqual(person.get_name(), "Имя2")

        person.set_name("Имя3")
        self.assertEqual(person.get_name(), "Имя3")

    def test_set_name_empty(self):
        """Тест установки пустого имени"""
        person = Person("Имя", 2000)
        person.set_name("")
        self.assertEqual(person.get_name(), "")

    def test_set_name_none(self):
        """Тест установки None в качестве имени"""
        person = Person("Имя", 2000)
        person.set_name(None)
        self.assertEqual(person.get_name(), None)

    def test_set_name_with_special_characters(self):
        """Тест установки имени со специальными символами"""
        person = Person("Старое", 2000)
        person.set_name("Иван-Петр III")
        self.assertEqual(person.get_name(), "Иван-Петр III")

    # ==================== Тесты для get_address ====================

    def test_get_address_with_address(self):
        """Тест получения адреса, если он установлен"""
        self.assertEqual(self.person1.get_address(), "Москва, ул. Ленина, д. 1")

    def test_get_address_without_address(self):
        """Тест получения адреса, если он не установлен"""
        self.assertEqual(self.person2.get_address(), "")

    def test_get_address_with_empty_string(self):
        """Тест получения адреса, если он пустая строка"""
        self.assertEqual(self.person3.get_address(), "")

    def test_get_address_after_change(self):
        """Тест получения адреса после изменения"""
        self.person1.set_address("Санкт-Петербург")
        self.assertEqual(self.person1.get_address(), "Санкт-Петербург")

    def test_get_address_after_set_to_empty(self):
        """Тест получения адреса после установки пустой строки"""
        self.person1.set_address("")
        self.assertEqual(self.person1.get_address(), "")

    def test_get_address_after_set_to_none(self):
        """Тест получения адреса после установки None"""
        self.person1.set_address(None)
        self.assertEqual(self.person1.get_address(), None)

    # ==================== Тесты для set_address ====================

    def test_set_address(self):
        """Тест установки адреса"""
        person = Person("Тест", 2000)
        person.set_address("Новый адрес")
        self.assertEqual(person.address, "Новый адрес")
        self.assertEqual(person.get_address(), "Новый адрес")

    def test_set_address_multiple_times(self):
        """Тест многократной установки адреса"""
        person = Person("Тест", 2000)
        person.set_address("Адрес 1")
        self.assertEqual(person.get_address(), "Адрес 1")

        person.set_address("Адрес 2")
        self.assertEqual(person.get_address(), "Адрес 2")

        person.set_address("Адрес 3")
        self.assertEqual(person.get_address(), "Адрес 3")

    def test_set_address_empty(self):
        """Тест установки пустого адреса"""
        person = Person("Тест", 2000, "Старый адрес")
        person.set_address("")
        self.assertEqual(person.get_address(), "")

    def test_set_address_none(self):
        """Тест установки None в качестве адреса"""
        person = Person("Тест", 2000, "Старый адрес")
        person.set_address(None)
        self.assertEqual(person.get_address(), None)

    def test_set_address_long_string(self):
        """Тест установки длинного адреса"""
        long_address = "г. Москва, ул. Тверская, д. 1, кв. 2, подъезд 3, этаж 4"
        person = Person("Тест", 2000)
        person.set_address(long_address)
        self.assertEqual(person.get_address(), long_address)

    # ==================== Тесты для is_homeless ====================

    def test_is_homeless_with_address(self):
        """Тест is_homeless, когда адрес установлен"""
        # Адрес установлен (не пустой)
        self.assertFalse(self.person1.is_homeless())

    def test_is_homeless_without_address(self):
        """Тест is_homeless, когда адрес не установлен"""
        # Адрес не был передан при создании
        self.assertTrue(self.person2.is_homeless())

    def test_is_homeless_with_empty_string(self):
        """Тест is_homeless, когда адрес - пустая строка"""
        # Адрес явно передан как пустая строка
        self.assertTrue(self.person3.is_homeless())

    def test_is_homeless_after_setting_address(self):
        """Тест is_homeless после установки адреса"""
        # Изначально без адреса
        person = Person("Тест", 2000)
        self.assertTrue(person.is_homeless())

        # Устанавливаем адрес
        person.set_address("Новый адрес")
        self.assertFalse(person.is_homeless())

    def test_is_homeless_after_clearing_address(self):
        """Тест is_homeless после очистки адреса"""
        # Изначально с адресом
        person = Person("Тест", 2000, "Старый адрес")
        self.assertFalse(person.is_homeless())

        # Очищаем адрес
        person.set_address("")
        self.assertTrue(person.is_homeless())

        # Устанавливаем None
        person.set_address(None)
        self.assertTrue(person.is_homeless())

    def test_is_homeless_with_whitespace_only(self):
        """Тест is_homeless, когда адрес содержит только пробелы"""
        # Примечание: в текущей реализации адрес из пробелов считается непустым
        person = Person("Тест", 2000, "   ")
        # Это может быть багом или фичей - в зависимости от требований
        # Сейчас это не считается бездомным
        self.assertFalse(person.is_homeless())

    # ==================== Интеграционные тесты ====================

    def test_full_lifecycle(self):
        """Тест полного жизненного цикла объекта Person"""
        # Создание
        person = Person("Тест Тестов", 2000)
        self.assertEqual(person.get_name(), "Тест Тестов")
        self.assertEqual(person.get_age(), datetime.datetime.now().year - 2000)
        self.assertTrue(person.is_homeless())

        # Установка адреса
        person.set_address("г. Москва")
        self.assertEqual(person.get_address(), "г. Москва")
        self.assertFalse(person.is_homeless())

        # Смена имени
        person.set_name("Новое Имя")
        self.assertEqual(person.get_name(), "Новое Имя")

        # Очистка адреса
        person.set_address("")
        self.assertTrue(person.is_homeless())

    def test_multiple_instances(self):
        """Тест независимости разных экземпляров"""
        person1 = Person("Иван", 1990, "Москва")
        person2 = Person("Петр", 1995)

        # Проверяем независимость
        self.assertEqual(person1.get_name(), "Иван")
        self.assertEqual(person2.get_name(), "Петр")

        self.assertEqual(person1.get_address(), "Москва")
        self.assertEqual(person2.get_address(), "")

        self.assertFalse(person1.is_homeless())
        self.assertTrue(person2.is_homeless())

        # Изменяем person2
        person2.set_address("СПб")
        person2.set_name("Петр Иванов")

        # person1 не изменился
        self.assertEqual(person1.get_name(), "Иван")
        self.assertEqual(person1.get_address(), "Москва")

        # person2 изменился
        self.assertEqual(person2.get_name(), "Петр Иванов")
        self.assertEqual(person2.get_address(), "СПб")
        self.assertFalse(person2.is_homeless())


if __name__ == '__main__':
    unittest.main(verbosity=2)