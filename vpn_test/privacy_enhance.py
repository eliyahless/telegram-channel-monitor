#!/usr/bin/env python3
import os
import sys
import platform
import random
import webbrowser
import subprocess
import time

def clear_browser_data():
    """Инструкции по очистке данных браузера"""
    print("\n=== Очистка данных браузера ===")
    print("Для обеспечения приватности рекомендуется очистить следующие данные:")
    print("1. История браузера")
    print("2. Cookies и данные сайтов")
    print("3. Кэш браузера")
    print("4. Данные автозаполнения форм")
    
    print("\nИнструкции для разных браузеров:")
    
    print("\nYandex Browser:")
    print("- Нажмите Ctrl+Shift+Del (или Cmd+Shift+Del на macOS)")
    print("- Выберите 'За все время' в выпадающем меню")
    print("- Отметьте все пункты")
    print("- Нажмите 'Очистить данные'")
    
    print("\nGoogle Chrome:")
    print("- Нажмите Ctrl+Shift+Del (или Cmd+Shift+Del на macOS)")
    print("- Выберите 'За все время' в выпадающем меню")
    print("- Отметьте все пункты")
    print("- Нажмите 'Очистить данные'")
    
    print("\nFirefox:")
    print("- Нажмите Ctrl+Shift+Del (или Cmd+Shift+Del на macOS)")
    print("- Выберите 'Все' в разделе временного диапазона")
    print("- Отметьте все пункты")
    print("- Нажмите 'Удалить сейчас'")
    
    choice = input("\nОткрыть страницу настроек вашего браузера? (да/нет): ")
    if choice.lower() in ['да', 'д', 'yes', 'y']:
        if platform.system() == 'Darwin':  # macOS
            if os.path.exists('/Applications/Yandex.app'):
                webbrowser.get('Yandex').open('chrome://settings/clearBrowserData')
            else:
                # Просто откроем настройки в браузере по умолчанию
                webbrowser.open('about:preferences#privacy')
    
    input("\nНажмите Enter, когда закончите очистку данных...")

def randomize_user_agent():
    """Информация о том, как рандомизировать User-Agent"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0"
    ]
    
    print("\n=== Рандомизация User-Agent ===")
    print("User-Agent - это идентификатор браузера, который отправляется каждому посещаемому сайту.")
    print("Замена его на случайное значение повышает анонимность.")
    
    print("\nРекомендуемые расширения для смены User-Agent:")
    print("- Firefox: User-Agent Switcher")
    print("- Chrome/Yandex: User-Agent Switcher for Chrome")
    print("- Brave: встроенная функция в настройках приватности")
    
    print("\nРекомендуемый случайный User-Agent:")
    random_ua = random.choice(user_agents)
    print(f"\n{random_ua}")
    print("\nВы можете скопировать этот User-Agent и использовать его в расширении.")
    
    choice = input("\nОткрыть страницу расширения для вашего браузера? (да/нет): ")
    if choice.lower() in ['да', 'д', 'yes', 'y']:
        # Открываем страницу расширения в зависимости от ОС
        if platform.system() == 'Darwin':  # macOS
            webbrowser.open("https://chrome.google.com/webstore/detail/user-agent-switcher-for-c/djflhoibgkdhkhhcedjiklpkjnoahfmg")
        else:
            webbrowser.open("https://addons.mozilla.org/ru/firefox/addon/user-agent-string-switcher/")
    
    input("\nНажмите Enter для возврата в главное меню...")

def enable_incognito_mode():
    """Инструкции по использованию режима инкогнито"""
    print("\n=== Режим инкогнито ===")
    print("Режим инкогнито помогает скрыть вашу активность в интернете от других пользователей устройства.")
    print("Однако он НЕ скрывает вашу активность от интернет-провайдера или сайтов, которые вы посещаете.")
    
    print("\nКак открыть режим инкогнито:")
    print("- Яндекс.Браузер: Ctrl+Shift+N (или Cmd+Shift+N на macOS)")
    print("- Google Chrome: Ctrl+Shift+N (или Cmd+Shift+N на macOS)")
    print("- Firefox: Ctrl+Shift+P (или Cmd+Shift+P на macOS)")
    print("- Brave: Ctrl+Shift+N (или Cmd+Shift+N на macOS)")
    
    print("\nДля максимальной анонимности используйте режим инкогнито ВМЕСТЕ с VPN.")
    
    choice = input("\nОткрыть окно в режиме инкогнито для вашего браузера по умолчанию? (да/нет): ")
    if choice.lower() in ['да', 'д', 'yes', 'y']:
        # Определяем ОС и открываем инкогнито
        if platform.system() == 'Darwin':  # macOS
            try:
                subprocess.run(['open', '-a', 'Google Chrome', '--args', '--incognito'], check=False)
            except:
                # Если Chrome не найден, пробуем Firefox
                try:
                    subprocess.run(['open', '-a', 'Firefox', '--args', '-private'], check=False)
                except:
                    print("Не удалось открыть режим инкогнито. Пожалуйста, откройте его вручную.")
        else:
            print("Пожалуйста, откройте режим инкогнито вручную, используя сочетания клавиш.")
    
    input("\nНажмите Enter для возврата в главное меню...")

def dns_leak_protection():
    """Информация о защите от DNS-утечек"""
    print("\n=== Защита от DNS-утечек ===")
    print("DNS-утечки могут раскрыть ваши настоящие местоположение даже при использовании VPN.")
    
    print("\nРекомендации по защите:")
    print("1. Используйте DNS-серверы вашего VPN-провайдера (обычно включено по умолчанию)")
    print("2. Настройте DNS вручную на серверы, которые не хранят логи:")
    print("   - Cloudflare: 1.1.1.1 и 1.0.0.1")
    print("   - Google: 8.8.8.8 и 8.8.4.4")
    print("   - Quad9: 9.9.9.9")
    
    print("\nПроверка DNS-утечек:")
    print("Чтобы проверить наличие DNS-утечек, посетите следующие сайты:")
    print("- https://www.dnsleaktest.com")
    print("- https://dnsleak.com")
    print("- https://ipleak.net")
    
    choice = input("\nОткрыть сайт для проверки DNS-утечек? (да/нет): ")
    if choice.lower() in ['да', 'д', 'yes', 'y']:
        print("\nПРЕДУПРЕЖДЕНИЕ: Перед открытием сайта убедитесь, что VPN активен!")
        confirm = input("Подтвердите, что VPN включен (да/нет): ")
        if confirm.lower() in ['да', 'д', 'yes', 'y']:
            webbrowser.open("https://www.dnsleaktest.com")
        else:
            print("Сначала включите VPN, затем повторите эту проверку.")
    
    input("\nНажмите Enter для возврата в главное меню...")

def fingerprint_protection():
    """Информация о защите от цифрового отпечатка браузера"""
    print("\n=== Защита от цифрового отпечатка браузера ===")
    print("Цифровой отпечаток браузера - это уникальный набор характеристик вашего устройства и браузера,")
    print("который может использоваться для вашей идентификации даже без cookies.")
    
    print("\nРекомендации по защите:")
    print("1. Используйте Brave Browser или Firefox с настройками приватности")
    print("2. Установите расширения:")
    print("   - Privacy Badger")
    print("   - uBlock Origin")
    print("   - Canvas Blocker")
    print("3. В Firefox включите настройку privacy.resistFingerprinting")
    
    print("\nПроверка цифрового отпечатка:")
    print("Чтобы проверить уникальность вашего отпечатка, посетите:")
    print("- https://amiunique.org")
    print("- https://coveryourtracks.eff.org")
    
    choice = input("\nОткрыть сайт для проверки цифрового отпечатка? (да/нет): ")
    if choice.lower() in ['да', 'д', 'yes', 'y']:
        webbrowser.open("https://coveryourtracks.eff.org")
    
    input("\nНажмите Enter для возврата в главное меню...")

def privacy_menu():
    """Главное меню инструментов приватности"""
    while True:
        print("\n" + "="*50)
        print("  ИНСТРУМЕНТЫ ПОВЫШЕНИЯ ПРИВАТНОСТИ")
        print("="*50)
        print("1. Очистка данных браузера")
        print("2. Рандомизация User-Agent")
        print("3. Использование режима инкогнито")
        print("4. Защита от DNS-утечек")
        print("5. Защита от цифрового отпечатка браузера")
        print("0. Вернуться в главное меню")
        
        choice = input("\nВыберите опцию (0-5): ")
        
        if choice == "1":
            clear_browser_data()
        elif choice == "2":
            randomize_user_agent()
        elif choice == "3":
            enable_incognito_mode()
        elif choice == "4":
            dns_leak_protection()
        elif choice == "5":
            fingerprint_protection()
        elif choice == "0":
            break
        else:
            print("\nНеверный выбор. Пожалуйста, выберите снова.")
            time.sleep(1)

if __name__ == "__main__":
    print("==== Инструменты повышения приватности ====")
    print("ВАЖНО: Эти инструменты предназначены для личного использования")
    print("и повышения безопасности при работе в интернете.")
    
    privacy_menu() 