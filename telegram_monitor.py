import os
import logging
import asyncio
import re
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from dotenv import load_dotenv
from db_manager import DatabaseManager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

class TelegramMonitor:
    def __init__(self):
        # Получение учетных данных
        self.api_id = int(os.getenv('API_ID'))
        self.api_hash = os.getenv('API_HASH')
        self.bot_token = os.getenv('BOT_TOKEN')
        self.output_channel = os.getenv('OUTPUT_CHANNEL')
        
        # Инициализация базы данных
        self.db = DatabaseManager()
        
        # Создание временной директории для медиа
        if not os.path.exists('temp'):
            os.makedirs('temp')
        
        # Клиенты для чтения и отправки
        self.user_client = None
        self.bot_client = None
        
        # Кэш ключевых слов
        self.keywords = []
        self.refresh_keywords()
        
    def refresh_keywords(self):
        """Обновляет кэш ключевых слов из базы данных"""
        self.keywords = [k['word'].lower() for k in self.db.get_all_keywords()]
        logger.info(f"Загружены ключевые слова: {self.keywords}")
        
    async def start_clients(self):
        """Запускает клиентов для мониторинга и отправки сообщений"""
        # Клиент для чтения (от имени пользователя)
        self.user_client = TelegramClient('user_session', self.api_id, self.api_hash)
        await self.user_client.start()
        logger.info("Клиент пользователя запущен")
        
        # Клиент для отправки (от имени бота)
        self.bot_client = TelegramClient('bot_session', self.api_id, self.api_hash)
        await self.bot_client.start(bot_token=self.bot_token)
        logger.info("Клиент бота запущен")
        
    async def stop_clients(self):
        """Останавливает клиентов"""
        if self.user_client:
            await self.user_client.disconnect()
        if self.bot_client:
            await self.bot_client.disconnect()
        logger.info("Клиенты остановлены")
    
    def contains_keywords(self, text):
        """Проверяет, содержит ли текст ключевые слова"""
        if not text:
            return False
            
        text = text.lower()
        return any(keyword in text for keyword in self.keywords)
    
    def format_message(self, message_text, channel_username, message_id):
        """Форматирует текст сообщения"""
        if not message_text:
            return ""
            
        # Удаляем лишние пробелы и переносы строк
        text = re.sub(r'\s+', ' ', message_text).strip()
        
        # Добавляем хештег #скидка если есть ключевые слова
        keywords = ['скидк', 'акци', 'распродаж', 'дешев', 'sale', 'промокод', '%']
        if any(keyword in text.lower() for keyword in keywords):
            text += "\n#скидка"
        
        # Добавляем ссылку на оригинальный пост
        post_url = f"https://t.me/{channel_username}/{message_id}"
        text += f'\n\n<a href="{post_url}">@{channel_username}</a>'
        
        return text
    
    async def process_message(self, event):
        """Обрабатывает новое сообщение и пересылает его если нужно"""
        # Пропускаем сообщения от ботов или системные сообщения
        if event.message.from_id and getattr(event.message.from_id, 'user_id', None) and event.message.from_id.user_id == 777000:
            return
            
        # Получаем идентификаторы сообщения и канала
        message_id = event.message.id
        channel_id = str(event.chat_id)
        
        # Пропускаем, если уже обрабатывали
        if self.db.message_exists(message_id, channel_id):
            logger.info(f"Сообщение {message_id} уже обработано, пропускаем")
            return
            
        # Получаем информацию о канале
        try:
            channel = await event.client.get_entity(event.chat_id)
            channel_username = channel.username
            channel_name = channel.title
            logger.info(f"Новое сообщение из канала {channel_name} (@{channel_username})")
        except Exception as e:
            logger.error(f"Ошибка при получении информации о канале: {e}")
            return
            
        # Проверяем текст на наличие ключевых слов
        if not self.contains_keywords(event.message.text):
            logger.info(f"Сообщение не содержит ключевых слов, пропускаем")
            self.db.add_processed_message(message_id, channel_id)
            return
            
        try:
            # Если есть медиа, скачиваем его
            if event.message.media:
                # Скачиваем медиа во временную директорию
                path = await event.message.download_media('temp/')
                logger.info(f"Медиа сохранено в {path}")
                
                # Форматируем текст сообщения
                formatted_text = self.format_message(
                    event.message.text,
                    channel_username,
                    message_id
                )
                
                # Отправляем сообщение с медиа
                await self.bot_client.send_file(
                    self.output_channel,
                    path,
                    caption=formatted_text,
                    parse_mode='html'
                )
                logger.info("Сообщение с медиа успешно отправлено")
                
                # Удаляем временный файл
                os.remove(path)
            else:
                # Форматируем текст сообщения
                formatted_text = self.format_message(
                    event.message.text,
                    channel_username,
                    message_id
                )
                
                # Отправляем только текст
                await self.bot_client.send_message(
                    self.output_channel,
                    formatted_text,
                    parse_mode='html'
                )
                logger.info("Текстовое сообщение успешно отправлено")
                
            # Добавляем сообщение в историю обработанных
            self.db.add_processed_message(message_id, channel_id)
            
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")
    
    async def setup_handlers(self):
        """Настраивает обработчики событий для мониторинга каналов"""
        # Получаем все активные каналы из базы данных
        channels = self.db.get_channels_by_city()
        
        if not channels:
            logger.warning("В базе данных нет каналов для мониторинга")
            return
            
        # Регистрируем обработчик для всех каналов
        @self.user_client.on(events.NewMessage(chats=[int(c['channel_id']) for c in channels]))
        async def new_message_handler(event):
            await self.process_message(event)
            
        logger.info(f"Настроен мониторинг для {len(channels)} каналов")
        
    async def run(self):
        """Запускает мониторинг каналов"""
        await self.start_clients()
        await self.setup_handlers()
        
        logger.info("Бот запущен и готов к мониторингу каналов")
        
        # Запускаем бесконечный цикл для работы клиентов
        try:
            await self.user_client.run_until_disconnected()
        finally:
            await self.stop_clients()
            
# Точка входа в программу
if __name__ == "__main__":
    monitor = TelegramMonitor()
    asyncio.run(monitor.run()) 