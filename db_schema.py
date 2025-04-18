import sqlite3
import os

def create_database():
    """Создает базу данных, если она не существует"""
    conn = sqlite3.connect('telegram_parser.db')
    cursor = conn.cursor()
    
    # Таблица городов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cities (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL
    )
    ''')
    
    # Таблица каналов с привязкой к городам
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS channels (
        id INTEGER PRIMARY KEY,
        channel_id TEXT NOT NULL,
        channel_name TEXT NOT NULL,
        channel_username TEXT,
        city_id INTEGER,
        is_active INTEGER DEFAULT 1,
        FOREIGN KEY (city_id) REFERENCES cities (id),
        UNIQUE(channel_id)
    )
    ''')
    
    # Таблица ключевых слов для фильтрации
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS keywords (
        id INTEGER PRIMARY KEY,
        word TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        UNIQUE(word)
    )
    ''')
    
    # Таблица обработанных сообщений
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS processed_messages (
        id INTEGER PRIMARY KEY,
        message_id INTEGER NOT NULL,
        channel_id TEXT NOT NULL,
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(message_id, channel_id)
    )
    ''')
    
    # Таблица пользователей с их городами
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER UNIQUE NOT NULL,
        city_id INTEGER,
        is_admin INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (city_id) REFERENCES cities (id)
    )
    ''')
    
    conn.commit()
    conn.close()
    
    print("База данных успешно создана!")

def add_default_data():
    """Добавляет начальные данные в базу"""
    conn = sqlite3.connect('telegram_parser.db')
    cursor = conn.cursor()
    
    # Добавляем несколько городов
    cities = [
        ('Москва',),
        ('Санкт-Петербург',),
        ('Новосибирск',),
        ('Екатеринбург',),
        ('Казань',)
    ]
    
    cursor.executemany('INSERT OR IGNORE INTO cities (name) VALUES (?)', cities)
    
    # Добавляем ключевые слова для фильтрации
    keywords = [
        ('скидка',),
        ('акция',),
        ('распродажа',),
        ('промокод',),
        ('бесплатно',),
        ('дешево',),
        ('выгодно',),
        ('sale',),
        ('promo',),
        ('discount',)
    ]
    
    cursor.executemany('INSERT OR IGNORE INTO keywords (word) VALUES (?)', keywords)
    
    conn.commit()
    conn.close()
    
    print("Начальные данные добавлены!")

if __name__ == "__main__":
    create_database()
    add_default_data() 