"""
Реализуйте endpoint, начинающийся с /max_number, в который можно передать список чисел, разделённых слешем /.
Endpoint должен вернуть текст «Максимальное переданное число {number}»,
где number — выделенное курсивом наибольшее из переданных чисел.

Примеры:

/max_number/10/2/9/1
Максимальное число: 10

/max_number/1/1/1/1/1/1/1/2
Максимальное число: 2

"""

from flask import Flask

app = Flask(__name__)


@app.route('/max_number/<path:numbers>')
def max_number(numbers):
    """
    Находит максимальное число из переданных в URL чисел

    Args:
        numbers (str): Строка с числами, разделёнными слешами

    Returns:
        str: Сообщение с максимальным числом
    """
    # Разбиваем строку по слешам
    numbers_list = numbers.split('/')

    # Фильтруем и проверяем, что все элементы являются числами
    valid_numbers = []
    invalid_items = []

    for item in numbers_list:
        try:
            # Пробуем преобразовать в число (поддерживает целые и дробные числа)
            num = float(item)
            # Проверяем, что это целое число (для вывода без .0)
            if num.is_integer():
                valid_numbers.append(int(num))
            else:
                valid_numbers.append(num)
        except ValueError:
            invalid_items.append(item)

    # Если нет валидных чисел
    if not valid_numbers:
        return "Ошибка: не передано ни одного корректного числа"

    # Если есть некорректные элементы, добавляем предупреждение
    if invalid_items:
        warning = f"\n(Некорректные значения пропущены: {', '.join(invalid_items)})"
    else:
        warning = ""

    # Находим максимальное число
    max_num = max(valid_numbers)

    # Форматируем вывод (убираем .0 для целых чисел)
    if isinstance(max_num, float) and max_num.is_integer():
        max_num_display = int(max_num)
    else:
        max_num_display = max_num

    return f'Максимальное переданное число: <i>{max_num_display}</i>{warning}'


@app.route('/max_number')
def max_number_empty():
    """Обработка запроса без параметров"""
    return "Ошибка: не передано ни одного числа. Используйте формат /max_number/число1/число2/..."


if __name__ == '__main__':
    app.run(debug=True)
