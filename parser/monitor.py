import json
import logging
import logging.config
import time
from typing import List, Set
import asyncio
import random
import re

from telethon import TelegramClient
from telethon.tl.types import Message, Channel
from telethon.errors import FloodWaitError, ChatAdminRequiredError

from config.settings import PARSER, LOGGING
from .models import ParsedMessage
from .classifiers import find_tags, is_hot_content
from .summarizer import create_short_title

# Настройка логирования
logging.config.dictConfig(LOGGING)
logger = logging.getLogger('parser')

def extract_city(text: str) -> str:
    """Извлекает город из текста или возвращает Москву по умолчанию"""
    # Список городов для поиска
    cities = ["Москва", "Санкт-Петербург", "Спб", "СПб", "Питер"]
    
    # Нормализуем текст
    text = text.lower()
    
    for city in cities:
        if city.lower() in text:
            if city.lower() in ["спб", "питер"]:
                return "Санкт-Петербург"
            return city
    
    return "Москва"  # По умолчанию

def load_processed_ids() -> Set[int]:
    """Загружает ID обработанных сообщений из файла"""
    try:
        if PARSER['processed_file'].exists():
            with open(PARSER['processed_file'], 'r') as f:
                return set(json.load(f))
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Ошибка загрузки {PARSER['processed_file']}: {e}")
    return set()

def save_processed_ids(processed_ids: Set[int]) -> None:
    """Сохраняет ID обработанных сообщений в файл"""
    PARSER['processed_file'].parent.mkdir(exist_ok=True)
    try:
        with open(PARSER['processed_file'], 'w') as f:
            json.dump(list(processed_ids), f, indent=4)
    except IOError as e:
        logger.error(f"Ошибка сохранения {PARSER['processed_file']}: {e}")

async def process_message(message: Message, source: str) -> ParsedMessage:
    """
    Обрабатывает отдельное сообщение из канала.
    
    Args:
        message: Объект сообщения Telegram
        source: Имя канала-источника
        
    Returns:
        ParsedMessage: Обработанное сообщение
    """
    # Получаем текст сообщения
    message_text = message.text if hasattr(message, 'text') else ""
    message_caption = message.caption if hasattr(message, 'caption') else ""
    full_text = message_text or message_caption or ""
    
    # Определяем город
    city = extract_city(full_text)
    
    # Находим теги
    tags = list(find_tags(full_text))
    
    # Определяем, горячее ли предложение
    is_hot = is_hot_content(tags)
    
    # Создаем короткое описание
    short = create_short_title(full_text, tags, city)
    
    # Формируем ссылку на сообщение
    link = f"https://t.me/{source.strip('@')}/{message.id}"
    
    return ParsedMessage(
        id=str(message.id),
        text=full_text,
        city=city,
        tags=tags,
        is_hot=is_hot,
        short=short,
        link=link,
        source=source
    )

async def parse_channel(client: TelegramClient) -> List[ParsedMessage]:
    """
    Парсит последние сообщения из целевых каналов.
    
    Args:
        client: Клиент Telegram
        
    Returns:
        List[ParsedMessage]: Список обработанных сообщений
    """
    start_time = time.time()
    processed_ids = load_processed_ids()
    new_messages: List[ParsedMessage] = []
    
    for channel in PARSER['target_channels']:
        try:
            # Добавляем небольшую задержку между каналами
            await asyncio.sleep(random.uniform(PARSER['min_delay'], PARSER['max_delay']))
            
            try:
                entity = await client.get_entity(channel)
                if not isinstance(entity, Channel):
                    logger.warning(f"{channel} не является каналом, пропускаем")
                    continue
                    
                logger.info(f"Получена сущность канала {channel}")
                
                count = 0
                found = 0
                
                async for message in client.iter_messages(entity, limit=PARSER['message_limit']):
                    try:
                        # Небольшая задержка между сообщениями
                        await asyncio.sleep(random.uniform(0.5, 1))
                        
                        count += 1
                        if count % 5 == 0:
                            logger.info(f"Проверено {count}/{PARSER['message_limit']} сообщений...")
                        
                        if isinstance(message, Message) and message.id not in processed_ids:
                            parsed_message = await process_message(message, channel)
                            new_messages.append(parsed_message)
                            processed_ids.add(message.id)
                            found += 1
                            logger.info(f"Найдено новое сообщение: ID {message.id} ({found} всего)")
                            
                    except FloodWaitError as e:
                        logger.warning(f"Превышен лимит запросов, ожидаем {e.seconds} секунд")
                        await asyncio.sleep(e.seconds)
                    except Exception as e:
                        logger.error(f"Ошибка обработки сообщения: {e}")
                        continue
                        
            except ChatAdminRequiredError:
                logger.error(f"Бот должен быть администратором канала {channel}")
                continue
            except FloodWaitError as e:
                logger.warning(f"Превышен лимит запросов для канала {channel}, ожидаем {e.seconds} секунд")
                await asyncio.sleep(e.seconds)
                continue
            except Exception as e:
                logger.error(f"Ошибка при получении доступа к каналу {channel}: {e}")
                continue
                
            logger.info(f"Проверка канала {channel} завершена. Найдено: {found} сообщений")
            
        except Exception as e:
            logger.error(f"Ошибка парсинга канала {channel}: {e}")
            continue
    
    if new_messages:
        save_processed_ids(processed_ids)
        logger.info(f"Сохранено {len(processed_ids)} ID обработанных сообщений")
    
    total_time = time.time() - start_time
    logger.info(f"Парсинг завершен за {total_time:.2f} сек")
    
    # Возвращаем сообщения в обратном порядке (новые первыми)
    return new_messages[::-1] 