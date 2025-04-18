#!/usr/bin/env python3
import requests
import json
import sys
import ssl

def check_ip():
    """Проверяет текущий IP адрес и информацию о геолокации"""
    try:
        # Используем разные сервисы для проверки IP, с явной проверкой SSL
        ipinfo = requests.get("https://ipinfo.io/json", timeout=5, verify=True).json()
        ip_api = requests.get("https://ip-api.com/json/", timeout=5, verify=True).json()
        
        print("\n=== Информация о вашем IP ===")
        print(f"IP адрес: {ipinfo.get('ip', 'Не определен')}")
        print(f"Страна: {ipinfo.get('country', 'Не определена')}")
        print(f"Город: {ipinfo.get('city', 'Не определен')}")
        print(f"Провайдер: {ipinfo.get('org', 'Не определен')}")
        
        print("\n=== Информация от ip-api.com ===")
        print(f"IP адрес: {ip_api.get('query', 'Не определен')}")
        print(f"Страна: {ip_api.get('country', 'Не определена')}")
        print(f"Код страны: {ip_api.get('countryCode', 'Не определен')}")
        print(f"Провайдер: {ip_api.get('isp', 'Не определен')}")
        
    except requests.exceptions.SSLError:
        print("Ошибка SSL: Невозможно установить защищенное соединение")
        return False
    except Exception as e:
        print(f"Ошибка при получении информации об IP: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Проверка вашего текущего IP адреса...")
    check_ip() 