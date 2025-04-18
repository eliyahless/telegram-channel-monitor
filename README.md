# Telegram Channel Monitor

Бот для мониторинга Telegram-каналов и пересылки сообщений по ключевым словам.

## Функциональность

- Мониторинг нескольких каналов одновременно
- Фильтрация сообщений по ключевым словам
- Пересылка сообщений в целевой канал
- Поддержка медиафайлов (фото, видео)
- Фильтрация по дате (только свежие сообщения)

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/telegram-channel-monitor.git
cd telegram-channel-monitor
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` и заполните его:
```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
TARGET_CHANNELS=@channel1,@channel2
OUTPUT_CHANNEL=@your_channel
```

## Использование

Запустите скрипт:
```bash
python channel_monitor.py
```

## Конфигурация

- `TARGET_CHANNELS` - список каналов для мониторинга (через запятую)
- `OUTPUT_CHANNEL` - канал для пересылки сообщений
- Ключевые слова для поиска можно изменить в коде

## Требования

- Python 3.7+
- telethon
- python-dotenv

## Лицензия

MIT 