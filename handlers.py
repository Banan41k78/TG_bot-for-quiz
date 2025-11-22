import datetime
from aiogram import types, F
from aiogram.filters.command import Command

import database as db
import keyboards as kb
from quiz_data import quiz_data

async def show_quiz_results(message: types.Message, user_id: int):
    """Показывает результаты квиза"""
    user_answers = await db.get_user_answers(user_id)
    correct_answers = await db.count_correct_answers(user_id)
    total_questions = len(quiz_data)
    
    result_text = f"🎉 Квиз завершен! 🎉\n\n"
    result_text += f"Ваш результат: {correct_answers}/{total_questions}\n\n"
    
    # Добавляем детали по каждому вопросу
    result_text += "Детали ответов:\n"
    for i, answer in enumerate(user_answers):
        question = quiz_data[i]
        user_correct = answer[0] if answer else False
        status = "✅" if user_correct else "❌"
        result_text += f"{i+1}. {status} {question['question']}\n"
    
    # Добавляем оценку
    percentage = (correct_answers / total_questions) * 100
    result_text += f"\nПроцент правильных ответов: {percentage:.1f}%\n"
    
    if percentage >= 90:
        result_text += "🎉 Отлично! Вы настоящий Python-эксперт!"
    elif percentage >= 70:
        result_text += "👍 Хороший результат!"
    elif percentage >= 50:
        result_text += "😊 Неплохо, но есть куда расти!"
    else:
        result_text += "📚 Рекомендуется повторить основы Python!"
    
    # Отправляем результаты с кнопками для сохранения или повторения
    await message.answer(result_text, reply_markup=kb.generate_results_keyboard())

async def get_question(message: types.Message, user_id: int):
    """Отправляет вопрос пользователю"""
    current_question_index = await db.get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    keyboard = kb.generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=keyboard)

async def new_quiz(message: types.Message):
    """Начинает новый квиз"""
    user_id = message.from_user.id
    current_question_index = 0
    await db.update_quiz_index(user_id, current_question_index)
    await db.clear_user_answers(user_id)
    await get_question(message, user_id)

# Хэндлер на команду /start
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать в квиз!", reply_markup=kb.get_start_keyboard())

# Хэндлер на команду /quiz
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)

# Хэндлер на команду /results
async def cmd_results(message: types.Message):
    """Показывает результаты последнего квиза"""
    user_answers = await db.get_user_answers(message.from_user.id)
    if not user_answers:
        await message.answer("Вы еще не проходили квиз. Начните игру с помощью /quiz")
        return
    
    await show_quiz_results(message, message.from_user.id)

# Хэндлер на команду /history
async def cmd_history(message: types.Message):
    """Показывает историю результатов пользователя"""
    user_id = message.from_user.id
    history = await db.get_quiz_history(user_id)
    
    if not history:
        await message.answer("У вас пока нет сохраненных результатов. Пройдите квиз с помощью /quiz и сохраните результат!")
        return
    
    history_text = "📊 История ваших результатов:\n\n"
    
    for i, result in enumerate(history):
        correct_answers, total_questions, date = result
        percentage = (correct_answers / total_questions) * 100
        date_str = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f').strftime('%d.%m.%Y %H:%M')
        
        history_text += f"{i+1}. {date_str}\n"
        history_text += f"   Результат: {correct_answers}/{total_questions} ({percentage:.1f}%)\n\n"
    
    # Добавляем статистику
    total_attempts = len(history)
    best_result = max(history, key=lambda x: x[0])
    best_percentage = (best_result[0] / best_result[1]) * 100
    
    history_text += f"📈 Статистика:\n"
    history_text += f"Всего попыток: {total_attempts}\n"
    history_text += f"Лучший результат: {best_result[0]}/{best_result[1]} ({best_percentage:.1f}%)\n"
    
    await message.answer(history_text)

# Обработчик нажатия на кнопку с правильным ответом
async def right_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    await callback.message.answer("Верно!")
    current_question_index = await db.get_quiz_index(callback.from_user.id)
    
    # Сохраняем правильный ответ
    await db.save_user_answer(callback.from_user.id, current_question_index, True)
    
    # Обновление номера текущего вопроса
    current_question_index += 1
    await db.update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await show_quiz_results(callback.message, callback.from_user.id)

# Обработчик нажатия на кнопку с неправильным ответом
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    current_question_index = await db.get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']

    await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")

    # Сохраняем неправильный ответ
    await db.save_user_answer(callback.from_user.id, current_question_index, False)
    
    # Обновление номера текущего вопроса
    current_question_index += 1
    await db.update_quiz_index(callback.from_user.id, current_question_index)

    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await show_quiz_results(callback.message, callback.from_user.id)

# Обработчик сохранения результата
async def save_result(callback: types.CallbackQuery):
    """Сохраняет результат пользователя"""
    user_id = callback.from_user.id
    correct_answers = await db.count_correct_answers(user_id)
    total_questions = len(quiz_data)
    
    # Сохраняем результат в базу данных
    await db.save_quiz_result(user_id, correct_answers, total_questions)
    
    await callback.message.edit_text(
        f"✅ Ваш результат сохранен!\n\n"
        f"Правильных ответов: {correct_answers}/{total_questions}\n"
        f"Вы можете посмотреть историю результатов с помощью команды /history",
        reply_markup=None
    )
    
    # Добавляем кнопку для начала новой игры
    await callback.message.answer("Хотите попробовать еще раз?", reply_markup=kb.get_start_keyboard())

# Обработчик начала нового квиза
async def restart_quiz(callback: types.CallbackQuery):
    """Начинает квиз заново"""
    await callback.message.edit_reply_markup(reply_markup=None)
    await new_quiz(callback.message)