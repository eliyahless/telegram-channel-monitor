#!/usr/bin/env python3
import os
import sys
import webbrowser
import time
import platform
import subprocess

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

if __name__ == "__main__":
    main_menu() 