import logging
import time
from typing import List

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from telethon.tl.types import Message

from config import settings


async def send_messages_to_user(bot: Bot, messages: List[Message]):
    """Отправляет список сообщений пользователю через бота.

    Args:
        bot: Экземпляр aiogram Bot.
        messages: Список сообщений Telethon для отправки.
    """
    if not messages:
        logging.info("Нет новых сообщений для отправки.")
        await bot.send_message(settings.USER_ID, "ℹ️ Нет новых сообщений, соответствующих фильтрам.")
        return

    start_time = time.time()
    total = len(messages)
    logging.info(f"Начинаем отправку {total} сообщений пользователю ID {settings.USER_ID}")
    await bot.send_message(settings.USER_ID, f"🔄 Начинаю отправку {total} новых сообщений...")

    for i, message in enumerate(messages, 1):
        msg_start = time.time()
        try:
            # Формируем ссылку на оригинальное сообщение
            message_link = f"https://t.me/{message.chat.username}/{message.id}"
            text_to_send = f"{message.text or message.caption or ''}\n\nИсточник: {message_link}"

            # Отправляем прогресс
            if total > 1:
                progress = f"[{i}/{total}] "
                await bot.send_message(settings.USER_ID, f"⏳ {progress}Отправляю сообщение {i} из {total}...")
            
            # Если есть медиа, отправляем его с текстом
            if message.media:
                # Сообщаем о скачивании
                await bot.send_message(settings.USER_ID, f"⏳ Скачиваю медиафайл для сообщения {i}...")
                download_start = time.time()
                
                # Скачиваем медиафайл временно
                media_file = await message.download_media(file=bytes)
                logging.info(f"Медиафайл для сообщения {i} скачан за {time.time() - download_start:.2f} сек")
                
                # Отправляем файл
                send_start = time.time()
                if message.photo:
                    await bot.send_photo(
                        chat_id=settings.USER_ID,
                        photo=media_file,
                        caption=text_to_send
                    )
                elif message.video:
                    await bot.send_video(
                        chat_id=settings.USER_ID,
                        video=media_file,
                        caption=text_to_send
                    )
                # Другие типы медиа
                else:
                    await bot.send_message(settings.USER_ID, text_to_send)
                
                logging.info(f"Сообщение {i} с медиа отправлено за {time.time() - send_start:.2f} сек")
            else:
                # Текстовое сообщение
                await bot.send_message(settings.USER_ID, text_to_send)
                logging.info(f"Текстовое сообщение {i} отправлено")

            message_time = time.time() - msg_start
            logging.info(f"Сообщение {i}/{total} обработано за {message_time:.2f} сек")

        except TelegramAPIError as e:
            logging.error(f"Ошибка отправки сообщения ID {message.id}: {e}")
            await bot.send_message(settings.USER_ID, f"❌ Ошибка отправки сообщения: {str(e)[:100]}...")
        except Exception as e:
            logging.error(f"Непредвиденная ошибка при обработке сообщения ID {message.id}: {e}")
            await bot.send_message(settings.USER_ID, f"❌ Непредвиденная ошибка: {str(e)[:100]}...")

    total_time = time.time() - start_time
    await bot.send_message(settings.USER_ID, f"✅ Отправка завершена! {total} сообщений отправлено за {total_time:.2f} сек")
    logging.info(f"Все {total} сообщений отправлены за {total_time:.2f} сек") 