import os
import asyncio
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

async def get_session_string():
    """Получает строку сессии для последующего использования"""
    try:
        # Создаем клиент с StringSession
        client = TelegramClient(
            StringSession(),
            int(os.getenv('API_ID')),
            os.getenv('API_HASH')
        )
        
        logger.info("Подключаемся к Telegram...")
        await client.connect()
        
        if not await client.is_user_authorized():
            logger.info("Требуется авторизация...")
            phone = os.getenv('PHONE')
            await client.send_code_request(phone)
            
            try:
                code = input('Введите код из Telegram (или "q" для выхода): ')
                if code.lower() == 'q':
                    logger.info("Операция отменена пользователем")
                    return
                
                await client.sign_in(phone, code)
            except Exception as e:
                if 'password' in str(e).lower():
                    # Если требуется двухфакторная аутентификация
                    password = input('Введите пароль двухфакторной аутентификации: ')
                    await client.sign_in(password=password)
                else:
                    raise e
        
        # Получаем строку сессии
        session_string = client.session.save()
        logger.info("\n=== ВАЖНО: Сохраните эту строку сессии! ===")
        logger.info(f"Строка сессии: {session_string}")
        logger.info("Добавьте эту строку в .env файл как SESSION_STRING=ваша_строка")
        
        # Проверяем работу сессии
        me = await client.get_me()
        logger.info(f"Сессия работает! Вы вошли как: {me.first_name}")
        
        return session_string
        
    except Exception as e:
        logger.error(f"Ошибка при получении сессии: {e}")
        return None
    finally:
        try:
            await client.disconnect()
        except:
            pass

if __name__ == '__main__':
    asyncio.run(get_session_string()) 