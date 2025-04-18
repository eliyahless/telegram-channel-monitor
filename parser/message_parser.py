import logging
from datetime import datetime
from telethon.tl.types import Message, MessageMediaPhoto, MessageMediaDocument
from dataclasses import dataclass
from typing import Optional, List

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ParsedMessage:
    """Структура для хранения распарсенного сообщения"""
    message_id: int
    channel_id: int
    date: datetime
    text: str
    media_type: Optional[str] = None
    forward_from: Optional[str] = None
    reply_to_msg_id: Optional[int] = None
    has_media: bool = False
    views: Optional[int] = None
    forwards: Optional[int] = None

class MessageParser:
    def __init__(self):
        self.media_types = {
            MessageMediaPhoto: 'photo',
            MessageMediaDocument: 'document'
        }
    
    async def parse_message(self, message: Message) -> ParsedMessage:
        """Парсит сообщение из Telegram"""
        try:
            # Определяем тип медиа
            media_type = None
            has_media = False
            if message.media:
                has_media = True
                for media_class, media_name in self.media_types.items():
                    if isinstance(message.media, media_class):
                        media_type = media_name
                        break
            
            # Получаем информацию о пересланном сообщении
            forward_from = None
            if message.forward:
                if message.forward.from_name:
                    forward_from = message.forward.from_name
                elif message.forward.from_id:
                    forward_from = str(message.forward.from_id)
            
            # Создаем структуру с данными сообщения
            parsed_message = ParsedMessage(
                message_id=message.id,
                channel_id=message.peer_id.channel_id if hasattr(message.peer_id, 'channel_id') else None,
                date=message.date,
                text=message.text or message.message or '',
                media_type=media_type,
                forward_from=forward_from,
                reply_to_msg_id=message.reply_to.reply_to_msg_id if message.reply_to else None,
                has_media=has_media,
                views=message.views if hasattr(message, 'views') else None,
                forwards=message.forwards if hasattr(message, 'forwards') else None
            )
            
            return parsed_message
            
        except Exception as e:
            logger.error(f"Ошибка при парсинге сообщения {message.id}: {e}")
            return None
    
    async def parse_messages(self, messages: List[Message]) -> List[ParsedMessage]:
        """Парсит список сообщений"""
        parsed_messages = []
        for message in messages:
            parsed_message = await self.parse_message(message)
            if parsed_message:
                parsed_messages.append(parsed_message)
        return parsed_messages 