import datetime
import random
import os
import re
from flask import Flask

app = Flask(__name__)

# Список машин в глобальной области видимости (не пересоздаётся при каждом запросе)
cars_list = ['Chevrolet', 'Renault', 'Ford', 'Lada']

# Список пород кошек в глобальной области видимости
cat_breeds = ['корниш-рекс', 'русская голубая', 'шотландская вислоухая', 'мейн-кун', 'манчкин']

# Получаем абсолютный путь к директории с текущим файлом
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOOK_FILE = os.path.join(BASE_DIR, 'war_and_peace.txt')

# Способ 1: Использование обычной глобальной переменной (РЕКОМЕНДУЕТСЯ)
visit_count = 0

# Функция для получения списка слов из книги
def get_words_from_book():
    """Читает файл книги и возвращает список всех слов без знаков препинания"""
    try:
        with open(BOOK_FILE, 'r', encoding='utf-8') as book:
            text = book.read()
            # Используем регулярное выражение для поиска всех слов (только буквы, включая русские)
            # r"[а-яА-Яa-zA-Z]+" находит последовательности русских и английских букв
            words = re.findall(r"[а-яА-Яa-zA-Z]+", text)
            return words
    except FileNotFoundError:
        print(f"Ошибка: файл {BOOK_FILE} не найден")
        return ["ошибка", "файл", "не", "найден"]

# Загружаем список слов при запуске приложения (глобально, не при каждом запросе)
words_list = get_words_from_book()

@app.route('/test')
def test_function():
    now = datetime.datetime.now(datetime.timezone.utc)
    return f'Это тестовая страничка, ответ сгенерирован в {now}'


@app.route('/hello_world')
def hello_world():
    return 'Привет, мир!'

@app.route('/cars')
def get_cars():
    # Возвращаем список машин через запятую
    return ', '.join(cars_list)

@app.route('/cats')
def get_random_cat():
    # Выбираем случайную породу из списка
    random_breed = random.choice(cat_breeds)
    return random_breed

@app.route('/get_time/now')
def get_current_time():
    # Получаем текущее время
    current_time = datetime.datetime.now()
    # Форматируем строку с использованием переменной
    return f'Точное время: {current_time}'

@app.route('/get_time/future')
def get_future_time():
    # Получаем текущее время
    current_time = datetime.datetime.now()
    # Добавляем один час с помощью timedelta
    time_delta = datetime.timedelta(hours=1)
    current_time_after_hour = current_time + time_delta
    # Форматируем строку с использованием переменной
    return f'Точное время через час будет {current_time_after_hour}'

@app.route('/get_random_word')
def get_random_word():
    # Выбираем случайное слово из предварительно загруженного списка
    if words_list:
        random_word = random.choice(words_list)
        return random_word
    else:
        return "Не удалось загрузить слова из книги", 500

@app.route('/counter')
def counter():
    global visit_count
    visit_count += 1
    return f'Эту страницу открыли {visit_count} раз(а)'

if __name__ == '__main__':
    app.run(debug=True)