#!/usr/bin/env python3
import os
import sys
import webbrowser
import time
import platform
import subprocess
import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path
from parser.session_manager import SessionManager
from parser.message_parser import MessageParser
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
import threading
from db_schema import create_database, add_default_data
from telegram_monitor import TelegramMonitor
from aiogram import executor
from bot import dp

# Импортируем наши модули
try:
    from check_ip import check_ip
except ImportError:
    def check_ip():
        print("Ошибка: Модуль check_ip.py не найден")
        return False

try:
    from privacy_enhance import privacy_menu
except ImportError:
    def privacy_menu():
        print("Ошибка: Модуль privacy_enhance.py не найден")
        return False

from aiogram import Bot
from config import settings
from parser.monitor import parse_channel
from bot.sender import send_messages_to_user
from config.settings import TELEGRAM, LOGGING

# Настройка логирования
logging.config.dictConfig(LOGGING)
logger = logging.getLogger('parser')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clear_screen():
    """Очищает экран терминала"""
    if platform.system() == 'Windows':
        subprocess.run(['cls'], shell=True)
    else:
        subprocess.run(['clear'], shell=True)

def check_vpn_status():
    """Проверяет статус VPN-соединения"""
    print("\n=== Проверка статуса VPN ===")
    check_ip()
    
    choice = input("\nВаш IP показывает правильную страну? (да/нет): ")
    if choice.lower() in ['да', 'д', 'yes', 'y']:
        print("\nОтлично! Ваш VPN настроен правильно.")
        return True
    else:
        print("\nВозможно, VPN не включен или имеются утечки.")
        return False

def open_notebook_lm():
    """Открывает Notebook LM в браузере"""
    print("\nОткрываю Notebook LM в браузере...")
    print("\nПРЕДУПРЕЖДЕНИЕ БЕЗОПАСНОСТИ: Закройте все другие вкладки браузера перед проверкой!")
    
    proceed = input("Подтвердите, что готовы продолжить (да/нет): ")
    if proceed.lower() not in ['да', 'д', 'yes', 'y']:
        print("Операция отменена пользователем")
        return False
        
    webbrowser.open("https://notebooklm.google.com/")
    
    time.sleep(3)  # Даем время на загрузку страницы
    
    print("\nВы смогли получить доступ к Notebook LM? (да/нет): ")
    result = input()
    
    if result.lower() in ['да', 'д', 'yes', 'y']:
        print("\nПоздравляем! Проблема решена.")
        return True
    else:
        print("\nК сожалению, проблема не решена. Давайте продолжим диагностику.")
        return False

def yandex_browser_specific():
    """Специфические инструкции для Яндекс.Браузера"""
    print("\n=== Решение проблем в Яндекс.Браузере ===")
    print("1. Откройте about:config в адресной строке")
    print("2. Найдите и отключите следующие настройки:")
    print("   - media.peerconnection.enabled → false (отключает WebRTC)")
    print("   - privacy.resistFingerprinting → true (повышает приватность)")
    print("3. Установите расширения:")
    print("   - WebRTC Control: https://chrome.google.com/webstore/detail/webrtc-control/fjkmabmdepjfammlpliljpnbhleegehm")
    print("   - Location Guard: https://chrome.google.com/webstore/detail/location-guard/cfohepagpmnodfdmjliccbbigdkfcgia")
    
    print("\nПРЕДУПРЕЖДЕНИЕ БЕЗОПАСНОСТИ: Устанавливайте расширения только из официальных магазинов!")
    
    choice = input("\nОткрыть страницу расширений Яндекс.Браузера? (да/нет): ")
    if choice.lower() in ['да', 'д', 'yes', 'y']:
        webbrowser.open("https://browser.yandex.ru/extensions/")
    
    print("\nПосле установки расширений и изменения настроек, перезапустите браузер.")
    input("\nНажмите Enter, чтобы вернуться в главное меню...")

def run_webrtc_tests():
    """Запускает проверку WebRTC утечек"""
    try:
        if os.path.exists("check_webrtc.py"):
            print("\nПРЕДУПРЕЖДЕНИЕ БЕЗОПАСНОСТИ: Сейчас будут открыты сайты для проверки утечек.")
            print("После завершения проверки ЗАКРОЙТЕ эти сайты для вашей безопасности!")
            
            proceed = input("Подтвердите, что готовы продолжить (да/нет): ")
            if proceed.lower() not in ['да', 'д', 'yes', 'y']:
                print("Операция отменена пользователем")
                return
                
            if platform.system() == 'Windows':
                subprocess.run(['python', 'check_webrtc.py'], shell=False)
            else:
                subprocess.run(['python3', 'check_webrtc.py'], shell=False)
        else:
            print("Ошибка: Файл check_webrtc.py не найден")
    except Exception as e:
        print(f"Ошибка при запуске проверки WebRTC: {e}")
    
    input("\nНажмите Enter, чтобы вернуться в главное меню...")

def show_instructions():
    """Отображает инструкции из руководства"""
    try:
        if os.path.exists("vpn_guide.md"):
            with open("vpn_guide.md", "r", encoding="utf-8") as f:
                content = f.read()
                print("\n" + content)
        else:
            print("Ошибка: Файл vpn_guide.md не найден")
    except Exception as e:
        print(f"Ошибка при чтении руководства: {e}")
    
    input("\nНажмите Enter, чтобы вернуться в главное меню...")

def use_alternative_browser():
    """Инструкции по использованию альтернативного браузера"""
    print("\n=== Использование альтернативного браузера ===")
    print("Наиболее рекомендуемые браузеры для работы с VPN:")
    print("1. Mozilla Firefox (лучшая защита от утечек)")
    print("2. Brave Browser (встроенная защита от отслеживания)")
    print("3. Google Chrome (требует дополнительных расширений)")
    
    print("\nПРЕДУПРЕЖДЕНИЕ БЕЗОПАСНОСТИ: Загружайте браузеры только с официальных сайтов!")
    
    choice = input("\nОткрыть страницу загрузки Firefox? (да/нет): ")
    if choice.lower() in ['да', 'д', 'yes', 'y']:
        webbrowser.open("https://www.mozilla.org/ru/firefox/new/")
    
    choice = input("\nОткрыть страницу загрузки Brave? (да/нет): ")
    if choice.lower() in ['да', 'д', 'yes', 'y']:
        webbrowser.open("https://brave.com/download/")
    
    input("\nНажмите Enter, чтобы вернуться в главное меню...")

def show_legal_info():
    """Показывает информацию о правовых аспектах"""
    print("\n=== Правовая информация ===")
    print("В Российской Федерации использование VPN регулируется законодательством.")
    print("Согласно российскому законодательству:")
    print("1. Использование VPN для личных целей НЕ запрещено")
    print("2. Закон №276-ФЗ запрещает использование VPN для доступа к запрещенным ресурсам")
    print("3. Сервис Notebook LM НЕ входит в список запрещенных ресурсов Роскомнадзора")
    
    print("\nИспользование нашей утилиты для личных целей (например, для доступа к")
    print("Notebook LM с целью образования или работы) не противоречит законодательству.")
    
    print("\nОднако, обратите внимание, что:")
    print("1. Вы используете данную утилиту на свой страх и риск")
    print("2. Авторы программы не несут ответственности за неправомерное использование")
    print("3. Всегда следите за изменениями в законодательстве")
    
    choice = input("\nЯ понимаю и принимаю эту информацию (да/нет): ")
    if choice.lower() not in ['да', 'д', 'yes', 'y']:
        print("Для использования утилиты необходимо принять эту информацию.")
        sys.exit(0)
    
    input("\nНажмите Enter, чтобы вернуться в главное меню...")

def main_menu():
    """Отображает главное меню программы"""
    # Первое, что мы делаем - показываем информацию о правовых аспектах
    show_legal_info()
    
    print("\nПРЕДУПРЕЖДЕНИЕ: Эта утилита предназначена только для обхода географических ограничений.")
    print("Используйте ее ответственно и в соответствии с законодательством вашей страны.")
    print("Разработчики не несут ответственности за неправильное использование данной утилиты.")
    
    proceed = input("\nПодтвердите, что вы понимаете это предупреждение (да/нет): ")
    if proceed.lower() not in ['да', 'д', 'yes', 'y']:
        print("Программа завершена.")
        sys.exit(0)
    
    while True:
        clear_screen()
        print("="*50)
        print("  УТИЛИТА ДОСТУПА К NOTEBOOK LM ИЗ РОССИИ")
        print("="*50)
        print("1. Проверить текущий IP-адрес и статус VPN")
        print("2. Запустить тесты на утечку WebRTC")
        print("3. Решение проблем в Яндекс.Браузере")
        print("4. Попробовать открыть Notebook LM")
        print("5. Использовать альтернативный браузер")
        print("6. Показать полное руководство")
        print("7. Инструменты повышения приватности")
        print("8. Правовая информация")
        print("0. Выход")
        
        choice = input("\nВыберите действие (0-8): ")
        
        if choice == "1":
            check_vpn_status()
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "2":
            run_webrtc_tests()
        elif choice == "3":
            yandex_browser_specific()
        elif choice == "4":
            open_notebook_lm()
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "5":
            use_alternative_browser()
        elif choice == "6":
            show_instructions()
        elif choice == "7":
            privacy_menu()
        elif choice == "8":
            show_legal_info()
        elif choice == "0":
            print("\nДо свидания!")
            sys.exit(0)
        else:
            print("\nНеверный выбор. Пожалуйста, выберите снова.")
            time.sleep(1)

# Загрузка переменных окружения
load_dotenv()

# Получение учетных данных из переменных окружения
api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
phone = os.getenv('PHONE')
target_channel = os.getenv('TARGET_CHANNEL')
output_channel = os.getenv('OUTPUT_CHANNEL')
session_string = os.getenv('SESSION_STRING')

# Создание клиента Telegram
client = TelegramClient('bot_session', api_id, api_hash)

async def save_session():
    """Сохраняет строку сессии в .env файл"""
    session_string = client.session.save()
    with open('.env', 'r') as file:
        lines = file.readlines()
    
    with open('.env', 'w') as file:
        for line in lines:
            if line.startswith('SESSION_STRING='):
                file.write(f'SESSION_STRING={session_string}\n')
            else:
                file.write(line)
    logger.info("Сессия сохранена в .env файл")

async def main():
    try:
        # Подключение к Telegram
        if session_string:
            await client.start(bot_token=bot_token)
            logger.info("Бот успешно запущен с сохраненной сессией")
        else:
            await client.start(phone=phone, bot_token=bot_token)
            await save_session()
            logger.info("Бот успешно запущен и сессия сохранена")

        # Обработчик новых сообщений
        @client.on(events.NewMessage(chats=target_channel))
        async def handle_new_message(event):
            try:
                message = event.message
                
                # Проверяем, содержит ли сообщение медиа
                if isinstance(message.media, (MessageMediaPhoto, MessageMediaDocument)):
                    # Получаем информацию о медиа
                    if isinstance(message.media, MessageMediaPhoto):
                        media_type = "Фото"
                    else:
                        media_type = "Документ"
                    
                    # Отправляем сообщение в выходной канал
                    await client.send_message(
                        output_channel,
                        f"Новое {media_type} из канала {target_channel}:\n{message.text if message.text else 'Без текста'}"
                    )
                    logger.info(f"Отправлено {media_type} в выходной канал")
                
            except Exception as e:
                logger.error(f"Ошибка при обработке сообщения: {str(e)}")

        # Запуск бота
        logger.info("Бот запущен и готов к работе")
        await client.run_until_disconnected()

    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {str(e)}")
        raise

def setup_database():
    """Создает и инициализирует базу данных"""
    try:
        create_database()
        add_default_data()
        logger.info("База данных успешно настроена")
    except Exception as e:
        logger.error(f"Ошибка при настройке базы данных: {e}")
        raise

async def run_monitor():
    """Запускает мониторинг Telegram-каналов"""
    monitor = TelegramMonitor()
    await monitor.run()

def start_monitor_thread():
    """Запускает мониторинг в отдельном потоке"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_monitor())

def check_env_variables():
    """Проверяет наличие необходимых переменных окружения"""
    required_vars = ['API_ID', 'API_HASH', 'BOT_TOKEN', 'OUTPUT_CHANNEL']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Отсутствуют необходимые переменные окружения: {', '.join(missing_vars)}")
        return False
    
    return True

def main():
    """Основная функция запуска системы"""
    logger.info("Запуск системы мониторинга каналов")
    
    # Проверяем переменные окружения
    if not check_env_variables():
        return
    
    # Настраиваем базу данных
    setup_database()
    
    # Запускаем мониторинг в отдельном потоке
    monitor_thread = threading.Thread(target=start_monitor_thread)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Запускаем бота администрирования
    logger.info("Запуск бота для управления системой")
    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    main() 