import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import Message
from dotenv import load_dotenv
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

async def test_connection():
    """Тестирует подключение к Telegram API используя строку сессии"""
    try:
        # Получаем строку сессии из .env
        session_string = os.getenv('SESSION_STRING')
        if not session_string:
            logger.error("SESSION_STRING не найдена в .env файле!")
            logger.info("Пожалуйста, сначала запустите python tests/get_session.py")
            return
            
        # Инициализация клиента с существующей сессией
        client = TelegramClient(
            StringSession(session_string),
            int(os.getenv('API_ID')),
            os.getenv('API_HASH')
        )
        
        logger.info("Подключаемся к Telegram...")
        await client.connect()
        
        if not await client.is_user_authorized():
            logger.error("Сессия недействительна! Получите новую сессию через get_session.py")
            return
        
        # Получение информации о себе
        me = await client.get_me()
        logger.info(f"Успешное подключение! Вы вошли как: {me.first_name}")
        
        # Тестирование получения сообщений
        target_channel = os.getenv('TARGET_CHANNEL')
        if target_channel:
            logger.info(f"Пробуем получить сообщения из канала {target_channel}...")
            try:
                messages = await client.get_messages(target_channel, limit=3)
                for msg in messages:
                    if isinstance(msg, Message) and msg.text:
                        logger.info(f"\nСообщение: {msg.text[:100]}...")  # Показываем только первые 100 символов
            except Exception as e:
                logger.error(f"Ошибка при получении сообщений: {e}")
        
        await client.disconnect()
        logger.info("Тест завершен успешно!")
        
    except Exception as e:
        logger.error(f"Ошибка при тестировании: {e}")
    finally:
        try:
            await client.disconnect()
        except:
            pass

if __name__ == '__main__':
    asyncio.run(test_connection()) 