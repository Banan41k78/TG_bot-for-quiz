from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )

    builder.adjust(1)
    return builder.as_markup()

def generate_results_keyboard():
    """Создает клавиатуру для сохранения результатов"""
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="💾 Сохранить результат", 
        callback_data="save_result")
    )
    builder.add(types.InlineKeyboardButton(
        text="🔄 Начать заново", 
        callback_data="restart_quiz")
    )
    builder.adjust(1)
    return builder.as_markup()

def get_start_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    return builder.as_markup(resize_keyboard=True)