import re
from typing import List, Optional
from .classifiers import extract_price, TAG_RULES

def create_short_title(text: str, tags: List[str], city: str) -> str:
    """
    Создает краткий заголовок для сообщения.
    
    Args:
        text: Исходный текст сообщения
        tags: Список тегов
        city: Город
        
    Returns:
        str: Краткий заголовок с эмодзи и ценой
    """
    # Извлекаем цены
    prices = extract_price(text)
    min_price = min(prices) if prices else None
    
    # Находим ключевые части текста
    sentences = re.split(r'[.!?\n]+', text)
    first_sentence = sentences[0].strip() if sentences else text
    
    # Ограничиваем длину первого предложения
    if len(first_sentence) > 100:
        first_sentence = first_sentence[:97] + "..."
    
    # Выбираем до 3 эмодзи для тегов
    emojis = [TAG_RULES[tag].emoji for tag in tags if tag in TAG_RULES][:3]
    emoji_prefix = "".join(emojis) + " " if emojis else ""
    
    # Формируем заголовок
    if min_price:
        return f"{emoji_prefix}{first_sentence} • от {min_price}₽"
    else:
        return f"{emoji_prefix}{first_sentence}"

def extract_date_info(text: str) -> Optional[str]:
    """
    Извлекает информацию о датах из текста.
    
    Args:
        text: Текст для анализа
        
    Returns:
        Optional[str]: Найденная дата или None
    """
    months = (
        "января|февраля|марта|апреля|мая|июня|"
        "июля|августа|сентября|октября|ноября|декабря"
    )
    
    date_patterns = [
        rf'(?:до|по)\s+(\d{{1,2}}(?:\s+)?(?:{months}))',
        rf'(?:с|начиная с)\s+(\d{{1,2}}(?:\s+)?(?:{months}))',
        rf'(\d{{1,2}}(?:\s+)?(?:{months}))',
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None 