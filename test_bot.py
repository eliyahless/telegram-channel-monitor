from telethon import TelegramClient
import os
from dotenv import load_dotenv
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# Получение учетных данных
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')

async def main():
    # Создание клиента
    async with TelegramClient('test_session', api_id, api_hash) as client:
        logger.info("Attempting to start bot...")
        try:
            # Попытка подключения
            await client.start(bot_token=bot_token)
            logger.info("Bot started successfully!")
            
            # Получение информации о боте
            me = await client.get_me()
            logger.info(f"Bot info: {me.username}")
            
            # Держим бота запущенным
            await client.run_until_disconnected()
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            raise

if __name__ == '__main__':
    import asyncio
    asyncio.run(main()) 