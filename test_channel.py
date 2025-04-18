import os
import logging
from telethon import TelegramClient
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# Получение учетных данных
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
TARGET_CHANNEL = os.getenv('TARGET_CHANNEL')

async def test_channel():
    """Тестирование доступа к каналу"""
    async with TelegramClient('test_session', API_ID, API_HASH) as client:
        await client.start(bot_token=BOT_TOKEN)
        
        try:
            # Получаем информацию о канале
            channel = await client.get_entity(TARGET_CHANNEL)
            logger.info(f"Канал найден: {channel.title}")
            
            # Пробуем получить последние сообщения
            messages = await client.get_messages(channel, limit=1)
            if messages:
                logger.info("Последнее сообщение:")
                msg = messages[0]
                logger.info(f"Текст: {msg.text[:100]}...")
                if msg.media:
                    logger.info(f"Тип медиа: {type(msg.media).__name__}")
            else:
                logger.info("Сообщений не найдено")
                
        except Exception as e:
            logger.error(f"Ошибка при проверке канала: {str(e)}")

if __name__ == '__main__':
    import asyncio
    asyncio.run(test_channel()) 