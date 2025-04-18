#!/usr/bin/env python3
import webbrowser
import platform
import os
import sys
import time

def open_webrtc_test_sites():
    """Открывает веб-сайты для проверки WebRTC утечек"""
    test_sites = [
        "https://browserleaks.com/webrtc",
        "https://ipleak.net/",
        "https://www.expressvpn.com/webrtc-leak-test"
    ]
    
    print("\n=== Проверка WebRTC утечек ===")
    print("Открываем сайты для проверки возможных утечек через WebRTC...")
    print("Эти сайты помогут выявить, показывает ли ваш браузер реальный IP-адрес даже при включенном VPN.")
    
    print("\nВАЖНО: После проверки каждого сайта закрывайте вкладки для безопасности!")
    print("ПРЕДУПРЕЖДЕНИЕ: Не вводите личные данные на тестовых сайтах!")
    
    proceed = input("\nПодтвердите, что понимаете риски и хотите продолжить (да/нет): ")
    if proceed.lower() not in ['да', 'д', 'yes', 'y']:
        print("Операция отменена пользователем")
        return
    
    for site in test_sites:
        try:
            print(f"\nОткрываем: {site}")
            print("Проверяется: безопасное соединение (HTTPS)...")
            if not site.startswith("https://"):
                print("ПРЕДУПРЕЖДЕНИЕ: Сайт использует небезопасное соединение!")
                continue_anyway = input("Продолжить несмотря на риск? (да/нет): ")
                if continue_anyway.lower() not in ['да', 'д', 'yes', 'y']:
                    print("Пропуск этого сайта...")
                    continue
            
            webbrowser.open(site)
            if site != test_sites[-1]:  # Не ждем после последнего сайта
                input("Нажмите Enter, чтобы открыть следующий сайт для проверки...")
                print("Не забудьте закрыть предыдущую вкладку!")
                time.sleep(1)
        except Exception as e:
            print(f"Ошибка при открытии {site}: {e}")
    
    print("\n=== Инструкции по результатам тестов ===")
    print("1. Если вы видите свой реальный IP-адрес на любом из этих сайтов, у вас есть утечка WebRTC")
    print("2. Для Яндекс.Браузера: откройте настройки и отключите WebRTC или установите расширение")
    print("3. Рекомендуется использовать браузер Firefox или Brave, которые имеют лучшую защиту от утечек")
    
    # Напоминание о безопасности
    print("\nНе забудьте закрыть все тестовые вкладки!")
    time.sleep(2)

def check_browser_settings():
    """Проверяет и предлагает настройки для разных браузеров"""
    system = platform.system()
    print("\n=== Рекомендации по настройке браузера ===")
    
    print("\nДля Яндекс.Браузера:")
    print("1. Откройте about:config в адресной строке")
    print("2. Найдите параметр media.peerconnection.enabled")
    print("3. Установите значение false")
    print("4. Также рекомендуется установить расширение WebRTC Control")
    
    print("\nАльтернативные браузеры:")
    print("- Firefox: самый надежный для использования с VPN")
    print("- Brave: имеет встроенную защиту от WebRTC утечек")
    print("- Chrome: требует установки расширений для защиты")
    
    print("\nДополнительные настройки безопасности:")
    print("- Используйте режим инкогнито/приватный при посещении Notebook LM")
    print("- Отключите геолокацию в настройках браузера")
    print("- Регулярно очищайте кэш и cookie браузера")
    
    input("\nНажмите Enter для возврата в главное меню...")

if __name__ == "__main__":
    print("==== Утилита проверки WebRTC утечек ====")
    print("ПРЕДУПРЕЖДЕНИЕ: Эта утилита откроет внешние сайты в вашем браузере.")
    print("Используйте на свой страх и риск и закрывайте сайты после проверки!")
    
    print("\n1. Открыть сайты для проверки WebRTC утечек")
    print("2. Показать инструкции по настройке браузера")
    print("3. Выход")
    
    choice = input("\nВыберите действие (1-3): ")
    
    if choice == "1":
        open_webrtc_test_sites()
    elif choice == "2":
        check_browser_settings()
    else:
        print("Выход из программы")
        sys.exit(0) 