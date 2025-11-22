import aiosqlite
import datetime
from config import DB_NAME

async def create_table():
    """Создает таблицы в базе данных"""
    async with aiosqlite.connect(DB_NAME) as db:
        # Таблица для состояния квиза
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        # Таблица для ответов пользователя
        await db.execute('''CREATE TABLE IF NOT EXISTS user_answers (
                            user_id INTEGER, 
                            question_index INTEGER, 
                            is_correct INTEGER,
                            PRIMARY KEY (user_id, question_index)
                        )''')
        # Таблица для сохраненных результатов
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_results (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            correct_answers INTEGER,
                            total_questions INTEGER,
                            date TIMESTAMP
                        )''')
        await db.commit()

async def get_quiz_index(user_id):
    """Получает текущий индекс вопроса для пользователя"""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            return results[0] if results is not None else 0

async def update_quiz_index(user_id, index):
    """Обновляет индекс текущего вопроса"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
        await db.commit()

async def save_user_answer(user_id, question_index, is_correct):
    """Сохраняет ответ пользователя"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'INSERT INTO user_answers (user_id, question_index, is_correct) VALUES (?, ?, ?)',
            (user_id, question_index, is_correct)
        )
        await db.commit()

async def save_quiz_result(user_id, correct_answers, total_questions):
    """Сохраняет итоговый результат квиза"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            'INSERT INTO quiz_results (user_id, correct_answers, total_questions, date) VALUES (?, ?, ?, ?)',
            (user_id, correct_answers, total_questions, datetime.datetime.now())
        )
        await db.commit()

async def get_user_answers(user_id):
    """Получает все ответы пользователя"""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            'SELECT is_correct FROM user_answers WHERE user_id = ? ORDER BY question_index',
            (user_id,)
        ) as cursor:
            return await cursor.fetchall()

async def count_correct_answers(user_id):
    """Считает количество правильных ответов"""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            'SELECT COUNT(*) FROM user_answers WHERE user_id = ? AND is_correct = 1',
            (user_id,)
        ) as cursor:
            result = await cursor.fetchone()
            return result[0] if result else 0

async def clear_user_answers(user_id):
    """Очищает предыдущие ответы пользователя"""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM user_answers WHERE user_id = ?', (user_id,))
        await db.commit()

async def get_quiz_history(user_id, limit=10):
    """Получает историю результатов пользователя"""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            'SELECT correct_answers, total_questions, date FROM quiz_results WHERE user_id = ? ORDER BY date DESC LIMIT ?',
            (user_id, limit)
        ) as cursor:
            return await cursor.fetchall()