"""
Реализуйте приложение для учёта финансов, умеющее запоминать, сколько денег было потрачено за день,
а также показывать затраты за отдельный месяц и за целый год.

В программе должно быть три endpoints:

/add/<date>/<int:number> — сохранение информации о совершённой в рублях трате за какой-то день;
/calculate/<int:year> — получение суммарных трат за указанный год;
/calculate/<int:year>/<int:month> — получение суммарных трат за указанные год и месяц.

Дата для /add/ передаётся в формате YYYYMMDD, где YYYY — год, MM — месяц (от 1 до 12), DD — число (от 01 до 31).
Гарантируется, что переданная дата имеет такой формат и она корректна (никаких 31 февраля).
"""

from flask import Flask, jsonify, request
from collections import defaultdict

app = Flask(__name__)

# Структура хранения данных: {год: {месяц: сумма_трат}}
# Используем defaultdict для автоматического создания вложенных словарей
storage = defaultdict(lambda: defaultdict(int))


def parse_date(date_str):
    """
    Разбирает дату в формате YYYYMMDD

    Args:
        date_str (str): Дата в формате YYYYMMDD

    Returns:
        tuple: (year, month, day) как целые числа
    """
    year = int(date_str[:4])
    month = int(date_str[4:6])
    day = int(date_str[6:8])
    return year, month, day


@app.route('/add/<date>/<int:number>')
def add_expense(date, number):
    """
    Сохраняет информацию о трате за указанный день

    Args:
        date (str): Дата в формате YYYYMMDD
        number (int): Сумма траты в рублях

    Returns:
        str: Сообщение об успешном добавлении
    """
    try:
        # Проверяем корректность формата даты
        if len(date) != 8:
            return "Ошибка: дата должна быть в формате YYYYMMDD", 400

        year, month, day = parse_date(date)

        # Проверяем корректность месяца и дня
        if month < 1 or month > 12:
            return "Ошибка: месяц должен быть от 1 до 12", 400

        if day < 1 or day > 31:
            return "Ошибка: день должен быть от 1 до 31", 400

        # Проверяем, что сумма траты положительная
        if number <= 0:
            return "Ошибка: сумма траты должна быть положительным числом", 400

        # Добавляем трату в хранилище
        storage[year][month] += number

        return f"Добавлена трата в размере {number} руб. за {year}-{month:02d}-{day:02d}"

    except ValueError:
        return "Ошибка: неверный формат даты. Используйте YYYYMMDD", 400
    except Exception as e:
        return f"Ошибка: {str(e)}", 500


@app.route('/calculate/<int:year>')
def calculate_year(year):
    """
    Возвращает суммарные траты за указанный год

    Args:
        year (int): Год

    Returns:
        str: Сумма трат за год
    """
    total = 0

    # Суммируем траты за все месяцы указанного года
    if year in storage:
        for month_expenses in storage[year].values():
            total += month_expenses

    return f"Суммарные траты за {year} год: {total} руб."


@app.route('/calculate/<int:year>/<int:month>')
def calculate_month(year, month):
    """
    Возвращает суммарные траты за указанные год и месяц

    Args:
        year (int): Год
        month (int): Месяц (1-12)

    Returns:
        str: Сумма трат за месяц
    """
    # Проверяем корректность месяца
    if month < 1 or month > 12:
        return "Ошибка: месяц должен быть от 1 до 12", 400

    # Получаем сумму трат за указанный месяц
    total = storage.get(year, {}).get(month, 0)

    return f"Суммарные траты за {year}-{month:02d}: {total} руб."


if __name__ == '__main__':
    app.run(debug=True)
