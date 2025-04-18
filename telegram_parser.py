#!/usr/bin/env python3
import asyncio
import logging
import os
import getpass
import time

from aiogram import Bot
from telethon import TelegramClient
from telethon.sessions import StringSession

from config import settings
from parser.monitor import parse_channel
from bot.sender import send_messages_to_user

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Сохраненная строка сессии 
SESSION_STRING = "1ApWapzMBu6Zq7nPE5zXTdcTQon7fEu56EKrrStsgg3qabnrmpBAPmHTXBK9SeKhPiNNZDKQ-Awtby52bdNtG-0-pEOPqW4en1Vm3FMDc-K7iyTLHFSPydmh9AxUF5PXbopH4EdpWJiXr9lWjTPdbboZHEkAGKBOnmxeVnsqrCtxLHL9vRfAMktTci-LLoaWNeq9YRWcWk0t1mGsYKZua5uBWO4EQ7gFJJ_H_N34da5Yyp0XN7uu6FwOhZpVSUCBl9jySBoxSwfEo3kVkLs75wlJ5ofLtKNvKQitmU4IIzTZOeq-5U3fWRRLUneqcqqMcGusSvkDbosdHcMbyjUcTeKYepVFnwp4="

async def main():
    """Основная функция запуска парсера и отправки сообщений."""
    logging.info("Запуск бота...")

    # --- Инициализация клиентов --- #
    # Используем сохраненную строку сессии для авторизации
    telethon_client = TelegramClient(StringSession(SESSION_STRING), settings.API_ID, settings.API_HASH)
    bot = Bot(token=settings.BOT_TOKEN)

    try:
        # --- Подключение Telethon --- #
        logging.info("Подключение к Telegram (Telethon) с сохраненной сессией...")
        
        # Определяем обработчик для ввода пароля 2FA (на случай, если сессия истечет)
        async def password_callback():
            # Используем getpass для скрытого ввода пароля
            return getpass.getpass("Введите ваш облачный пароль 2FA: ")
        
        # Сначала пробуем подключиться напрямую, без ввода данных
        await telethon_client.connect()
        
        # Если не авторизованы, то запускаем полный процесс авторизации
        if not await telethon_client.is_user_authorized():
            logging.info("Сессия истекла, запрашиваем повторную авторизацию...")
            await telethon_client.start(
                phone=lambda: input('Введите номер телефона (например, +79991234567): '),
                password=password_callback
            )
            
            # После успешной авторизации сохраняем новую строку сессии
            if await telethon_client.is_user_authorized():
                new_session_string = telethon_client.session.save()
                logging.info(f"Новая строка сессии: {new_session_string}")
                logging.info("Сохраните эту строку для будущего использования.")
            else:
                logging.error("Не удалось авторизоваться даже с вводом данных. Завершение работы.")
                return
        
        # Проверка авторизации
        me = await telethon_client.get_me()
        logging.info(f"Telethon успешно авторизован как пользователь: {me.first_name} (ID: {me.id}).")

        # Сначала отправим последнее сообщение из канала без фильтрации (тестовый режим)
        await send_last_message(telethon_client, bot)

        # --- Основной цикл (в данном случае один запуск) --- #
        logging.info("Начинаем парсинг канала...")
        new_filtered_messages = await parse_channel(telethon_client)

        if new_filtered_messages:
            logging.info(f"Найдено {len(new_filtered_messages)} новых сообщений. Отправка...")
            await send_messages_to_user(bot, new_filtered_messages)
            logging.info("Отправка завершена.")
        else:
            logging.info("Новых подходящих сообщений не найдено.")

    except Exception as e:
        logging.exception(f"Произошла ошибка во время выполнения: {e}")
    finally:
        # --- Закрытие соединений --- #
        if telethon_client.is_connected():
            await telethon_client.disconnect()
            logging.info("Telethon клиент отключен.")
        # Закрываем сессию бота Aiogram
        if hasattr(bot, 'session') and bot.session:
            await bot.session.close()
            logging.info("Сессия Aiogram бота закрыта.")

async def send_last_message(client: TelegramClient, bot: Bot):
    """Отправляет последнее сообщение из канала без фильтрации для проверки работы бота."""
    try:
        start_time = time.time()
        logging.info("Получаем последнее сообщение из канала для теста...")
        await bot.send_message(settings.USER_ID, "🔄 Начинаю работу... Получаю последнее сообщение из канала.")
        
        entity = await client.get_entity('@afisharestaurants')
        messages = await client.get_messages(entity, limit=1)
        
        if messages and len(messages) > 0:
            message = messages[0]
            logging.info(f"Найдено последнее сообщение ID: {message.id} (заняло {time.time() - start_time:.2f} сек)")
            await bot.send_message(settings.USER_ID, "✅ Сообщение найдено, подготавливаю к отправке...")
            
            # Создаем текст сообщения
            message_link = f"https://t.me/afisharestaurants/{message.id}"
            message_text = message.text if hasattr(message, 'text') and message.text else ''
            message_caption = message.caption if hasattr(message, 'caption') and message.caption else ''
            full_text = message_text or message_caption or 'Пустой текст'
            
            text_to_send = f"ТЕСТОВОЕ СООБЩЕНИЕ\n\n{full_text}\n\nИсточник: {message_link}"
            
            # Отправляем сообщение
            media_start = time.time()
            await bot.send_message(settings.USER_ID, text_to_send)
            logging.info(f"Текст сообщения отправлен (заняло {time.time() - media_start:.2f} сек)")
            
            # Если есть медиа, отправляем его отдельно
            if message.media:
                await bot.send_message(settings.USER_ID, "⏳ Обнаружены медиафайлы. Загружаю... (это может занять время)")
                logging.info("Обнаружены медиаданные, пересылаем...")
                try:
                    media_start = time.time()
                    # Скачиваем медиафайл временно
                    await bot.send_message(settings.USER_ID, "⏳ Скачиваю медиафайл...")
                    media_file = await message.download_media(file=bytes)
                    logging.info(f"Медиафайл скачан (заняло {time.time() - media_start:.2f} сек)")
                    
                    await bot.send_message(settings.USER_ID, "⏳ Отправляю медиафайл...")
                    send_start = time.time()
                    if message.photo:
                        await bot.send_photo(
                            chat_id=settings.USER_ID,
                            photo=media_file,
                            caption="Фото из последнего поста @afisharestaurants"
                        )
                    elif message.video:
                        await bot.send_video(
                            chat_id=settings.USER_ID,
                            video=media_file,
                            caption="Видео из последнего поста @afisharestaurants"
                        )
                    logging.info(f"Медиафайл отправлен (заняло {time.time() - send_start:.2f} сек)")
                    await bot.send_message(settings.USER_ID, "✅ Медиафайл успешно отправлен!")
                except Exception as e:
                    logging.error(f"Ошибка при отправке медиа: {e}")
                    await bot.send_message(settings.USER_ID, f"❌ Ошибка при отправке медиа: {str(e)[:100]}...")
            
            total_time = time.time() - start_time
            logging.info(f"Тестовое сообщение отправлено (общее время: {total_time:.2f} сек)")
            await bot.send_message(settings.USER_ID, f"✅ Тестовое сообщение отправлено за {total_time:.2f} сек")
        else:
            logging.warning("Не удалось получить сообщения из канала")
            await bot.send_message(settings.USER_ID, "❌ Не удалось получить сообщения из канала @afisharestaurants")
            
    except Exception as e:
        logging.exception(f"Ошибка при отправке тестового сообщения: {e}")
        try:
            await bot.send_message(settings.USER_ID, f"❌ Ошибка при получении сообщений: {str(e)[:100]}...")
        except:
            pass

if __name__ == "__main__":
    # Используем loop.run_until_complete для корректного завершения в некоторых средах
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logging.info("Получен сигнал KeyboardInterrupt, завершение работы...")
    finally:
        # Дополнительная очистка, если необходима
        tasks = asyncio.all_tasks(loop)
        for task in tasks:
            task.cancel()
        group = asyncio.gather(*tasks, return_exceptions=True)
        loop.run_until_complete(group)
        loop.close()
        logging.info("Цикл событий asyncio закрыт.") 