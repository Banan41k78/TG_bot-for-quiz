import asyncio
import logging
from aiogram import Bot, Dispatcher, F

import database as db
import handlers
from config import API_TOKEN

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Объект бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Регистрация хэндлеров
dp.message.register(handlers.cmd_start, F.text == "start")
dp.message.register(handlers.cmd_quiz, F.text == "quiz")
dp.message.register(handlers.cmd_quiz, F.text == "Начать игру")
dp.message.register(handlers.cmd_results, F.text == "results")
dp.message.register(handlers.cmd_history, F.text == "history")

dp.callback_query.register(handlers.right_answer, F.data == "right_answer")
dp.callback_query.register(handlers.wrong_answer, F.data == "wrong_answer")
dp.callback_query.register(handlers.save_result, F.data == "save_result")
dp.callback_query.register(handlers.restart_quiz, F.data == "restart_quiz")

# Запуск бота
async def main():
    await db.create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())