import os
import logging
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from dotenv import load_dotenv
import re
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
TARGET_CHANNEL = os.getenv('TARGET_CHANNEL')
OUTPUT_CHANNEL = os.getenv('OUTPUT_CHANNEL')

def format_message(message_text, channel_username, message_id):
    """Форматирование текста сообщения"""
    if not message_text:
        return ""
        
    # Удаляем лишние пробелы и переносы строк
    text = re.sub(r'\s+', ' ', message_text).strip()
    
    # Добавляем хештег #скидка если есть ключевые слова
    keywords = ['скидк', 'акци', 'распродаж', 'дешев', 'sale', 'промокод', '%']
    if any(keyword in text.lower() for keyword in keywords):
        text += "\n#скидка"
    
    # Добавляем форматированную ссылку на пост
    post_url = f"https://t.me/{channel_username}/{message_id}"
    text += f'\n\n<a href="{post_url}">@{channel_username}</a>'
    
    return text

async def forward_last_post():
    """Пересылка последнего поста"""
    # Создаем временную директорию для медиа
    if not os.path.exists('temp'):
        os.makedirs('temp')
        
    # Создаем клиент для чтения
    async with TelegramClient('user_session', API_ID, API_HASH) as client:
        logger.info("Подключаюсь к Telegram...")
        
        try:
            # Получаем последнее сообщение из канала
            source_channel = await client.get_entity(TARGET_CHANNEL)
            logger.info(f"Исходный канал найден: {source_channel.title}")
            
            messages = await client.get_messages(source_channel, limit=1)
            if not messages:
                logger.info("Сообщений не найдено")
                return
                
            message = messages[0]
            logger.info(f"Получено сообщение: {message.text[:100]}...")
            
            if message.media:
                # Скачиваем медиа
                path = await message.download_media('temp/')
                logger.info(f"Медиа сохранено в {path}")
                
                # Создаем клиент бота для отправки
                async with TelegramClient('bot_session', API_ID, API_HASH) as bot:
                    await bot.start(bot_token=BOT_TOKEN)
                    logger.info("Бот подключен")
                    
                    # Форматируем текст с ссылкой на оригинальный пост
                    formatted_text = format_message(
                        message.text,
                        source_channel.username,
                        message.id
                    )
                    
                    # Отправляем новое сообщение с медиа и HTML-форматированием
                    await bot.send_file(
                        OUTPUT_CHANNEL,
                        path,
                        caption=formatted_text,
                        parse_mode='html'
                    )
                    logger.info("Сообщение успешно отправлено!")
                    
                # Удаляем временный файл
                os.remove(path)
            else:
                logger.info("В сообщении нет медиа")
                
        except Exception as e:
            logger.error(f"Ошибка: {str(e)}")

if __name__ == '__main__':
    import asyncio
    asyncio.run(forward_last_post()) 