import os
from dotenv import load_dotenv
from pathlib import Path
from typing import List

# Загружаем переменные окружения из .env файла
load_dotenv()

# --- Telethon --- #
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

# --- Aiogram --- #
BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = os.getenv("USER_ID")

# --- Валидация --- #
if not all([API_ID, API_HASH, BOT_TOKEN, USER_ID]):
    raise ValueError(
        "Необходимо установить переменные окружения: "
        "API_ID, API_HASH, BOT_TOKEN, USER_ID в .env файле."
    )

try:
    API_ID = int(API_ID) # type: ignore
except ValueError:
    raise ValueError("API_ID должен быть числом.")

try:
    USER_ID = int(USER_ID) # type: ignore
except ValueError:
    raise ValueError("USER_ID должен быть числом.")

# Базовые пути
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'

# Создаем необходимые директории
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Настройки Telegram
TELEGRAM = {
    'api_id': int(os.getenv('API_ID')),
    'api_hash': os.getenv('API_HASH'),
    'bot_token': os.getenv('BOT_TOKEN'),
    'target_channel': os.getenv('TARGET_CHANNEL'),
    'output_channel': os.getenv('OUTPUT_CHANNEL'),
}

# Настройки парсера
PARSER = {
    'message_limit': 10,
    'min_delay': 1,
    'max_delay': 3,
    'target_channels': ['@afisharestaurants', '@breakfastinmsk'],
    'processed_file': DATA_DIR / 'processed.json',
}

# Настройки логирования
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'parser.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'parser': {
            'handlers': ['console', 'file'],
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
    },
} 