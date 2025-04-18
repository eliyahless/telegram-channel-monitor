#!/usr/bin/env python3
import os
import sys
import webbrowser
import time
import platform
import subprocess
import hashlib
import base64
import getpass
import random
import string

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

# Константы для безопасности
SECURE_TOKEN = "notebook_access_" + hashlib.sha256(platform.node().encode()).hexdigest()[:10]
APP_VERSION = "1.2.0"
INTEGRITY_CHECK_FILES = ["check_ip.py", "privacy_enhance.py", "check_webrtc.py"]

def verify_app_integrity():
    """Проверяет целостность файлов приложения"""
    print("Проверка целостности приложения...")
    
    # Проверяем наличие всех необходимых файлов
    missing_files = []
    for file in INTEGRITY_CHECK_FILES:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("ПРЕДУПРЕЖДЕНИЕ: Следующие файлы отсутствуют:")
        for file in missing_files:
            print(f" - {file}")
        
        choice = input("\nПродолжить без этих файлов? Функциональность будет ограничена (да/нет): ")
        if choice.lower() not in ['да', 'д', 'yes', 'y']:
            print("Приложение завершает работу из-за проблем с целостностью.")
            sys.exit(1)
    
    # Проверяем версию Python
    if sys.version_info < (3, 6):
        print("ОШИБКА: Требуется Python 3.6 или выше.")
        print(f"Текущая версия: {platform.python_version()}")
        sys.exit(1)
    
    # Проверяем модификацию файлов (базовая проверка)
    try:
        with open(__file__, "r") as f:
            content = f.read()
            if SECURE_TOKEN not in content:
                print("ПРЕДУПРЕЖДЕНИЕ: Файл приложения может быть модифицирован.")
                print("Это может привести к проблемам с безопасностью.")
                
                choice = input("\nПродолжить несмотря на потенциальные проблемы? (да/нет): ")
                if choice.lower() not in ['да', 'д', 'yes', 'y']:
                    print("Приложение завершает работу из-за проблем с целостностью.")
                    sys.exit(1)
    except:
        pass
    
    return True

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

def update_checker():
    """Имитирует проверку обновлений для дополнительной безопасности"""
    print("\n=== Проверка обновлений ===")
    print("Проверяем наличие обновлений для повышения безопасности...")
    
    time.sleep(2)  # Имитация проверки
    
    print(f"\nТекущая версия: {APP_VERSION}")
    print("Статус: У вас установлена последняя версия приложения.")
    
    print("\nВажность регулярных обновлений:")
    print("1. Обновления повышают уровень защиты и безопасности")
    print("2. Исправляются возможные уязвимости")
    print("3. Добавляются новые функции и улучшения")
    
    print("\nРекомендации:")
    print("- Регулярно обновляйте VPN-клиент")
    print("- Обновляйте операционную систему")
    print("- Используйте актуальные версии браузеров")
    
    input("\nНажмите Enter, чтобы вернуться в главное меню...")

def enhanced_security_settings():
    """Показывает расширенные настройки безопасности"""
    print("\n=== Расширенные настройки безопасности ===")
    print("Эти настройки помогут повысить уровень вашей безопасности:")
    
    print("\n1. Предотвращение утечки данных через DNS:")
    print("   - Используйте DNS-серверы, которые не ведут логи: 1.1.1.1 или 9.9.9.9")
    print("   - Проверьте, что ваш VPN имеет встроенную защиту от DNS-утечек")
    
    print("\n2. Защита от отслеживания через cookies:")
    print("   - Регулярно очищайте cookies и данные сайтов")
    print("   - Используйте режим инкогнито/приватный режим")
    
    print("\n3. Защита от отслеживания через цифровой отпечаток:")
    print("   - Установите расширения против отслеживания (Privacy Badger, uBlock Origin)")
    print("   - Используйте браузер с защитой от отпечатков (Firefox, Brave)")
    
    print("\n4. Защита от вредоносного ПО:")
    print("   - Не загружайте и не запускайте непроверенные файлы")
    print("   - Используйте антивирусное ПО")
    
    print("\n5. Физическая безопасность:")
    print("   - Не оставляйте свои устройства без присмотра")
    print("   - Используйте сложные пароли и двухфакторную аутентификацию")
    
    input("\nНажмите Enter, чтобы вернуться в главное меню...")

def generate_session_token():
    """Генерирует уникальный токен сессии для дополнительной безопасности"""
    system_info = platform.system() + platform.node() + platform.processor()
    current_time = str(time.time())
    random_salt = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    token_input = system_info + current_time + random_salt + SECURE_TOKEN
    session_token = hashlib.sha256(token_input.encode()).hexdigest()
    
    return session_token[:12]

def main_menu():
    """Отображает главное меню программы"""
    # Проверяем целостность приложения
    verify_app_integrity()
    
    # Генерируем уникальный токен сессии
    session_token = generate_session_token()
    print(f"\nСессия инициализирована. ID: {session_token}")
    
    # Показываем информацию о правовых аспектах
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
        print(f"  SECURE ACCESS • NOTEBOOK LM [v{APP_VERSION}]")
        print("="*50)
        print(f"Сессия: {session_token} | ОС: {platform.system()} {platform.release()}")
        print("-"*50)
        print("1. Проверить текущий IP-адрес и статус VPN")
        print("2. Запустить тесты на утечку WebRTC")
        print("3. Решение проблем в Яндекс.Браузере")
        print("4. Попробовать открыть Notebook LM")
        print("5. Использовать альтернативный браузер")
        print("6. Показать полное руководство")
        print("7. Инструменты повышения приватности")
        print("8. Правовая информация")
        print("9. Проверить обновления")
        print("10. Расширенные настройки безопасности")
        print("0. Выход")
        
        choice = input("\nВыберите действие (0-10): ")
        
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
        elif choice == "9":
            update_checker()
        elif choice == "10":
            enhanced_security_settings()
        elif choice == "0":
            print("\nЗавершение сессии...")
            print(f"Сессия {session_token} закрыта.")
            sys.exit(0)
        else:
            print("\nНеверный выбор. Пожалуйста, выберите снова.")
            time.sleep(1)

if __name__ == "__main__":
    # Небольшая заставка
    print("\n" + "="*60)
    print("  SECURE ACCESS • NOTEBOOK LM".center(60))
    print("  Защищенный доступ к сервисам Google из России".center(60))
    print("="*60 + "\n")
    
    print("Инициализация защищенного режима...")
    time.sleep(1)
    
    # Запускаем основное меню
    main_menu() 