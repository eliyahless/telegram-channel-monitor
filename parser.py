import os
import logging
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from dotenv import load_dotenv
import re
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('parser.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# Получение учетных данных
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')
PHONE = os.getenv('PHONE')
TARGET_CHANNEL = os.getenv('TARGET_CHANNEL')
OUTPUT_CHANNEL = os.getenv('OUTPUT_CHANNEL')

def format_message(message_text):
    """Форматирование текста сообщения"""
    if not message_text:
        return ""
        
    # Удаляем лишние пробелы и переносы строк
    text = re.sub(r'\s+', ' ', message_text).strip()
    
    # Добавляем хештег #скидка если есть ключевые слова
    keywords = ['скидк', 'акци', 'распродаж', 'дешев', 'sale', 'промокод', '%']
    if any(keyword in text.lower() for keyword in keywords):
        text += "\n#скидка"
    
    # Добавляем дату публикации
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
    text += f"\n\nОпубликовано: {current_time}"
    
    return text

async def forward_messages():
    """Функция для пересылки сообщений из одного канала в другой"""
    logger.info(f"Настройка клиента с API_ID={API_ID}")
    logger.info(f"Целевой канал: {TARGET_CHANNEL}")
    logger.info(f"Канал назначения: {OUTPUT_CHANNEL}")

    # Создаем клиент для чтения публичного канала
    client = TelegramClient('user_session', API_ID, API_HASH)
    
    try:
        # Авторизация через номер телефона
        await client.start(phone=PHONE)
        logger.info("Клиент успешно запущен")
        
        me = await client.get_me()
        logger.info(f"Авторизован как: {me.first_name}")

        # Создаем отдельный клиент для бота (для отправки в канал)
        bot = TelegramClient('bot_session', API_ID, API_HASH)
        await bot.start(bot_token=BOT_TOKEN)
        bot_info = await bot.get_me()
        logger.info(f"Бот авторизован как: {bot_info.username}")

        @client.on(events.NewMessage(chats=TARGET_CHANNEL))
        async def handler(event):
            try:
                message = event.message
                logger.info(f"Получено новое сообщение из канала {TARGET_CHANNEL}")
                
                # Проверяем тип медиа
                media_type = None
                if isinstance(message.media, MessageMediaPhoto):
                    media_type = "Фото"
                elif hasattr(message.media, 'document') and message.media.document.mime_type.startswith('video'):
                    media_type = "Видео"
                elif isinstance(message.media, MessageMediaDocument):
                    media_type = "Документ"

                # Если есть медиа и текст
                if media_type and message.text:
                    logger.info(f"Обнаружено сообщение с {media_type}")
                    # Форматируем текст
                    formatted_text = format_message(message.text)
                    
                    # Отправляем через бота
                    await bot.send_message(
                        OUTPUT_CHANNEL,
                        formatted_text,
                        file=message.media
                    )
                    logger.info(f"Отправлено {media_type} в канал {OUTPUT_CHANNEL}")
                else:
                    logger.info("Сообщение пропущено - нет медиа или текста")
                
            except Exception as e:
                logger.error(f"Ошибка при обработке сообщения: {str(e)}")

        logger.info(f"Начинаю мониторинг канала {TARGET_CHANNEL}")
        await client.run_until_disconnected()
    
    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}")
        raise
    finally:
        await client.disconnect()
        await bot.disconnect()

if __name__ == '__main__':
    import asyncio
    try:
        asyncio.run(forward_messages())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {str(e)}")
        raise 