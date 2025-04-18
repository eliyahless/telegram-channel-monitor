#!/usr/bin/env python3
import asyncio
import logging
import os
import re
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from dotenv import load_dotenv
import json
import tempfile

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def normalize_channel_name(channel):
    """Преобразование ссылки или имени канала в формат @username"""
    # Если это ссылка вида https://t.me/username
    if 't.me/' in channel:
        channel = channel.split('t.me/')[-1]
    
    # Удаляем все, что не является буквами, цифрами или подчеркиванием
    channel = re.sub(r'[^a-zA-Z0-9_]', '', channel)
    
    # Добавляем @ если его нет
    if not channel.startswith('@'):
        channel = '@' + channel
    
    return channel

def is_fresh_message(message_date, max_age_days=7):
    """Проверка, что сообщение не старше указанного количества дней"""
    if not message_date:
        return False
    
    now = datetime.now(message_date.tzinfo)
    age = now - message_date
    return age.days <= max_age_days

async def get_channel_messages(client, channel, limit=100):
    """Получение сообщений из канала"""
    try:
        # Нормализуем имя канала
        channel = normalize_channel_name(channel)
        logger.info(f"Получение сообщений из канала: {channel}")
        
        messages = []
        async for message in client.iter_messages(channel, limit=limit):
            if message.text and is_fresh_message(message.date):  # Проверяем дату сообщения
                messages.append({
                    'id': message.id,
                    'text': message.text,
                    'date': message.date.isoformat(),
                    'channel': channel,
                    'media': bool(message.media),
                    'message': message
                })
                logger.info(f"Найдено свежее сообщение от {message.date}")
        
        logger.info(f"Найдено {len(messages)} свежих сообщений в канале {channel}")
        return messages
    except Exception as e:
        logger.error(f"Ошибка при получении сообщений из канала {channel}: {e}")
        return []

def contains_keywords(text, keywords):
    """Проверка наличия ключевых слов в тексте"""
    text = text.lower()
    return any(keyword.lower() in text for keyword in keywords)

async def forward_message(user_client, bot_client, message, output_channel):
    """Пересылка сообщения в целевой канал"""
    try:
        # Нормализуем имя выходного канала
        output_channel = normalize_channel_name(output_channel)
        logger.info(f"Начинаем пересылку сообщения в канал {output_channel}")
        
        # Получаем информацию о канале
        chat = await bot_client.get_entity(output_channel)
        logger.info(f"Получена информация о целевом канале: {chat}")
        
        # Создаем временную директорию для медиафайлов
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Если есть медиа, скачиваем его
                if message.media:
                    logger.info("Сообщение содержит медиафайл")
                    media_path = await user_client.download_media(
                        message.media,
                        file=temp_dir
                    )
                    logger.info(f"Медиафайл успешно скачан: {media_path}")
                    
                    # Отправляем медиафайл с текстом
                    await bot_client.send_file(
                        chat.id,
                        media_path,
                        caption=message.text[:1000] if message.text else None  # Ограничиваем длину текста
                    )
                    logger.info("Медиафайл успешно отправлен")
                else:
                    # Отправляем только текст
                    logger.info("Отправка текстового сообщения...")
                    await bot_client.send_message(
                        chat.id,
                        message.text[:4000] if message.text else ""  # Ограничиваем длину текста
                    )
                    logger.info("Текстовое сообщение успешно отправлено")
                
                logger.info(f"Сообщение успешно переслано в канал {output_channel}")
                return True
                
            except Exception as e:
                logger.error(f"Ошибка при отправке сообщения: {str(e)}")
                return False
                
    except Exception as e:
        logger.error(f"Критическая ошибка при пересылке сообщения: {e}")
        logger.error(f"Тип ошибки: {type(e)}")
        logger.error(f"Детали ошибки: {str(e)}")
        return False

async def check_bot_permissions(bot_client):
    """Проверка прав бота в целевом канале"""
    try:
        output_channel = normalize_channel_name(os.getenv("OUTPUT_CHANNEL"))
        logger.info(f"Проверка прав бота в канале {output_channel}")
        
        # Получаем информацию о канале
        chat = await bot_client.get_entity(output_channel)
        logger.info(f"Информация о канале: {chat}")
        
        # Пробуем отправить тестовое сообщение
        try:
            await bot_client.send_message(chat.id, "Тестовое сообщение для проверки прав")
            logger.info("Права бота проверены успешно")
            return True
        except Exception as e:
            logger.error(f"Ошибка при отправке тестового сообщения: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Ошибка при проверке канала: {e}")
        return False

async def process_channels(user_client, bot_client):
    """Обработка всех каналов"""
    channels = [normalize_channel_name(channel.strip()) for channel in os.getenv("TARGET_CHANNELS", "").split(",")]
    keywords = os.getenv("KEYWORDS", "").split(",")
    output_channel = normalize_channel_name(os.getenv("OUTPUT_CHANNEL"))
    
    logger.info(f"Список каналов для мониторинга: {channels}")
    logger.info(f"Ключевые слова для поиска: {keywords}")
    logger.info(f"Целевой канал для пересылки: {output_channel}")
    
    if not channels or not keywords:
        logger.error("Не указаны каналы или ключевые слова")
        return
    
    matched_messages = []
    
    for channel in channels:
        logger.info(f"Начинаем обработку канала: {channel}")
        try:
            messages = await get_channel_messages(user_client, channel)
            logger.info(f"Получено {len(messages)} сообщений из канала {channel}")
            
            for message_data in messages:
                logger.info(f"Проверяем сообщение: {message_data['text'][:100]}...")
                if contains_keywords(message_data['text'], keywords):
                    logger.info(f"Найдено совпадение! Текст: {message_data['text'][:100]}...")
                    matched_messages.append(message_data)
                    
                    # Пересылаем сообщение
                    logger.info("Начинаем пересылку сообщения...")
                    await forward_message(user_client, bot_client, message_data['message'], output_channel)
                    logger.info("Сообщение успешно переслано!")
                    break  # Пересылаем только первое найденное сообщение для теста
        except Exception as e:
            logger.error(f"Ошибка при обработке канала {channel}: {e}")
    
    if not matched_messages:
        logger.info("Сообщений с ключевыми словами не найдено")
    else:
        logger.info(f"Всего найдено {len(matched_messages)} сообщений с ключевыми словами")

async def main():
    """Основная функция"""
    user_client = None
    bot_client = None
    
    try:
        # Инициализация клиентов
        user_client = TelegramClient('user_session', int(os.getenv("API_ID")), os.getenv("API_HASH"))
        bot_client = TelegramClient('bot_session', int(os.getenv("API_ID")), os.getenv("API_HASH"))
        
        # Запуск клиентов
        await user_client.start()
        await bot_client.start(bot_token=os.getenv("BOT_TOKEN"))
        
        logger.info("Клиенты успешно запущены")
        
        # Проверяем права бота
        if not await check_bot_permissions(bot_client):
            logger.error("Бот не имеет необходимых прав для работы. Проверьте настройки канала.")
            return
        
        await process_channels(user_client, bot_client)
        
    except Exception as e:
        logger.error(f"Ошибка в основной функции: {e}")
    finally:
        if user_client:
            await user_client.disconnect()
        if bot_client:
            await bot_client.disconnect()
        logger.info("Клиенты отключены")

if __name__ == "__main__":
    asyncio.run(main()) 