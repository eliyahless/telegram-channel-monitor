import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_file='telegram_parser.db'):
        self.db_file = db_file
        
    def _get_connection(self):
        """Получает соединение с базой данных"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row  # Чтобы получать результаты в виде словарей
        return conn
        
    # Методы для работы с городами
    def get_all_cities(self):
        """Получает список всех городов"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cities')
        cities = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return cities
        
    def add_city(self, name):
        """Добавляет новый город"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO cities (name) VALUES (?)', (name,))
            conn.commit()
            city_id = cursor.lastrowid
            conn.close()
            return city_id
        except sqlite3.IntegrityError:
            conn.close()
            return None
            
    def delete_city(self, city_id):
        """Удаляет город"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cities WHERE id = ?', (city_id,))
        conn.commit()
        conn.close()
        
    # Методы для работы с каналами
    def get_channels_by_city(self, city_id=None):
        """Получает каналы для указанного города или все каналы"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if city_id is not None:
            cursor.execute('''
                SELECT c.*, ct.name as city_name 
                FROM channels c
                LEFT JOIN cities ct ON c.city_id = ct.id
                WHERE c.city_id = ? AND c.is_active = 1
            ''', (city_id,))
        else:
            cursor.execute('''
                SELECT c.*, ct.name as city_name 
                FROM channels c
                LEFT JOIN cities ct ON c.city_id = ct.id
                WHERE c.is_active = 1
            ''')
            
        channels = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return channels
        
    def add_channel(self, channel_id, channel_name, channel_username=None, city_id=None):
        """Добавляет новый канал в базу"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO channels (channel_id, channel_name, channel_username, city_id) 
                VALUES (?, ?, ?, ?)
            ''', (channel_id, channel_name, channel_username, city_id))
            conn.commit()
            channel_id = cursor.lastrowid
            conn.close()
            return channel_id
        except sqlite3.IntegrityError:
            conn.close()
            return None
            
    def update_channel(self, channel_id, is_active, city_id=None):
        """Обновляет данные канала"""
        conn = self._get_connection()
        cursor = conn.cursor()
        if city_id is not None:
            cursor.execute('''
                UPDATE channels SET is_active = ?, city_id = ? 
                WHERE channel_id = ?
            ''', (is_active, city_id, channel_id))
        else:
            cursor.execute('''
                UPDATE channels SET is_active = ? WHERE channel_id = ?
            ''', (is_active, channel_id))
        conn.commit()
        conn.close()
        
    def delete_channel(self, channel_id):
        """Удаляет канал из базы"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM channels WHERE channel_id = ?', (channel_id,))
        conn.commit()
        conn.close()
        
    # Методы для работы с ключевыми словами
    def get_all_keywords(self, active_only=True):
        """Получает список всех ключевых слов"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if active_only:
            cursor.execute('SELECT * FROM keywords WHERE is_active = 1')
        else:
            cursor.execute('SELECT * FROM keywords')
            
        keywords = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return keywords
        
    def add_keyword(self, word):
        """Добавляет новое ключевое слово"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO keywords (word) VALUES (?)', (word,))
            conn.commit()
            keyword_id = cursor.lastrowid
            conn.close()
            return keyword_id
        except sqlite3.IntegrityError:
            conn.close()
            return None
            
    def update_keyword(self, keyword_id, is_active):
        """Обновляет статус ключевого слова"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE keywords SET is_active = ? WHERE id = ?', 
                      (is_active, keyword_id))
        conn.commit()
        conn.close()
        
    def delete_keyword(self, keyword_id):
        """Удаляет ключевое слово"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM keywords WHERE id = ?', (keyword_id,))
        conn.commit()
        conn.close()
        
    # Методы для работы с историей сообщений
    def message_exists(self, message_id, channel_id):
        """Проверяет, существует ли сообщение в истории"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM processed_messages 
            WHERE message_id = ? AND channel_id = ?
        ''', (message_id, channel_id))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
        
    def add_processed_message(self, message_id, channel_id):
        """Добавляет сообщение в историю обработанных"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO processed_messages (message_id, channel_id) 
                VALUES (?, ?)
            ''', (message_id, channel_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False
            
    # Методы для работы с пользователями
    def get_user(self, user_id):
        """Получает информацию о пользователе"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.*, c.name as city_name 
            FROM users u
            LEFT JOIN cities c ON u.city_id = c.id
            WHERE u.user_id = ?
        ''', (user_id,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return dict(user)
        return None
        
    def add_user(self, user_id, city_id=None, is_admin=0):
        """Добавляет нового пользователя"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (user_id, city_id, is_admin) 
                VALUES (?, ?, ?)
            ''', (user_id, city_id, is_admin))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False
            
    def update_user_city(self, user_id, city_id):
        """Обновляет город пользователя"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET city_id = ? WHERE user_id = ?', 
                      (city_id, user_id))
        conn.commit()
        conn.close()
        
    def set_admin_status(self, user_id, is_admin):
        """Устанавливает статус администратора"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET is_admin = ? WHERE user_id = ?', 
                      (is_admin, user_id))
        conn.commit()
        conn.close()
        
    def get_all_users(self, city_id=None):
        """Получает список всех пользователей"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if city_id:
            cursor.execute('''
                SELECT u.*, c.name as city_name 
                FROM users u
                LEFT JOIN cities c ON u.city_id = c.id
                WHERE u.city_id = ?
            ''', (city_id,))
        else:
            cursor.execute('''
                SELECT u.*, c.name as city_name 
                FROM users u
                LEFT JOIN cities c ON u.city_id = c.id
            ''')
            
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users 