"""
Довольно неудобно использовать встроенный валидатор NumberRange для ограничения числа по его длине.
Создадим свой для поля phone. Создайте валидатор обоими способами.
Валидатор должен принимать на вход параметры min и max — минимальная и максимальная длина,
а также опциональный параметр message (см. рекомендации к предыдущему заданию).
"""
"""
Валидаторы для поля phone.
Созданы двумя способами: функция и класс.
"""
from typing import Optional
from wtforms.validators import ValidationError
from flask_wtf import FlaskForm
from wtforms import Field


# ==================== Функциональный валидатор ====================
def number_length(min: int, max: int, message: Optional[str] = None):
    """
    Фабрика валидаторов для проверки длины числа.

    Args:
        min: минимальная длина числа
        max: максимальная длина числа
        message: сообщение об ошибке

    Returns:
        функция-валидатор
    """

    def _number_length(form: FlaskForm, field: Field):
        if field.data is None:
            return

        # Преобразуем число в строку и проверяем длину
        number_str = str(field.data)

        # Проверяем, что строка состоит только из цифр (для отрицательных чисел)
        if number_str.startswith('-'):
            number_str = number_str[1:]

        if not number_str.isdigit():
            raise ValidationError(message or "Значение должно содержать только цифры")

        length = len(number_str)

        if length < min or length > max:
            if message:
                raise ValidationError(message)
            else:
                raise ValidationError(f"Длина числа должна быть от {min} до {max} символов. Текущая длина: {length}")

    return _number_length


# ==================== Класс-валидатор ====================
class NumberLength:
    """
    Класс-валидатор для проверки длины числа.

    Args:
        min: минимальная длина числа
        max: максимальная длина числа
        message: сообщение об ошибке
    """

    def __init__(self, min: int, max: int, message: Optional[str] = None):
        self.min = min
        self.max = max
        self.message = message

    def __call__(self, form: FlaskForm, field: Field):
        if field.data is None:
            return

        # Преобразуем число в строку и проверяем длину
        number_str = str(field.data)

        # Проверяем, что строка состоит только из цифр (для отрицательных чисел)
        if number_str.startswith('-'):
            number_str = number_str[1:]

        if not number_str.isdigit():
            raise ValidationError(self.message or "Значение должно содержать только цифры")

        length = len(number_str)

        if length < self.min or length > self.max:
            if self.message:
                raise ValidationError(self.message)
            else:
                raise ValidationError(
                    f"Длина числа должна быть от {self.min} до {self.max} символов. "
                    f"Текущая длина: {length}"
                )
