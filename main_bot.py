#!/usr/bin/env python3
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=os.getenv("BOT_TOKEN"), parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Я бот для мониторинга каналов.\n\n"
        "Я могу:\n"
        "• Мониторить каналы\n"
        "• Пересылать сообщения\n"
        "• Анализировать контент\n\n"
        "Используйте /help для получения списка команд."
    )

# Обработчик команды /help
@dp.message(CommandStart("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📋 Список доступных команд:\n\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        "/monitor - Начать мониторинг каналов\n"
        "/stop - Остановить мониторинг\n"
        "/status - Показать статус мониторинга"
    )

async def main():
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) 