import os
import asyncio
import json
from datetime import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession
from parser.monitor import parse_channel, TARGET_CHANNELS

# Данные для подключения бота
BOT_TOKEN = '7768306152:AAEYyJEZIsPVrqS3umB9VsbiE1zlcmL4Zkg'
API_ID = 12876443
API_HASH = '227da8debb0c76622abef1fa609199be'

async def main():
    # Инициализация клиента-бота
    client = TelegramClient(StringSession(), API_ID, API_HASH).start(bot_token=BOT_TOKEN)
    
    print("Бот успешно запущен!")
    
    # Запуск парсера
    messages = await parse_channel(client)
    
    # Сохранение результатов
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'parsed_messages_{timestamp}.json'
    
    # Преобразуем сообщения в словари для JSON
    messages_dict = [msg.to_dict() for msg in messages]
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(messages_dict, f, ensure_ascii=False, indent=2)
    
    print(f"\nОбработано {len(messages)} сообщений из каналов: {', '.join(TARGET_CHANNELS)}")
    print(f"Результаты сохранены в файл: {filename}")
    print("\nПримеры первых трех сообщений:")
    
    for msg in messages[:3]:
        print(f"\nЗаголовок: {msg.short}")
        print(f"Теги: {', '.join(msg.tags)}")
        print(f"Город: {msg.city}")
        print(f"Горячее: {'Да' if msg.is_hot else 'Нет'}")
        if msg.geo:
            print(f"Координаты: {msg.geo.lat}, {msg.geo.lon}")
        print(f"Ссылка: {msg.link}")

if __name__ == '__main__':
    asyncio.run(main()) 