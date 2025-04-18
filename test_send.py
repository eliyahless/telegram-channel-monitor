import os
import logging
from telethon import TelegramClient
from dotenv import load_dotenv
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# Получение учетных данных
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
OUTPUT_CHANNEL = os.getenv('OUTPUT_CHANNEL')

async def test_send():
    """Тестирование отправки в канал"""
    async with TelegramClient('bot_session', API_ID, API_HASH) as bot:
        # Авторизация бота
        await bot.start(bot_token=BOT_TOKEN)
        logger.info("Бот запущен")
        
        try:
            # Получаем информацию о канале
            channel = await bot.get_entity(OUTPUT_CHANNEL)
            logger.info(f"Канал найден: {channel.title}")
            
            # Формируем тестовое сообщение
            current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
            test_message = f"""🔥 Тестовое сообщение!

Проверка работы бота для пересылки сообщений.
#тест

Опубликовано: {current_time}"""
            
            # Отправляем сообщение
            message = await bot.send_message(OUTPUT_CHANNEL, test_message)
            logger.info("Тестовое сообщение отправлено успешно!")
            
        except Exception as e:
            logger.error(f"Ошибка при отправке: {str(e)}")

if __name__ == '__main__':
    import asyncio
    asyncio.run(test_send()) 