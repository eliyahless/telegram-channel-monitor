from typing import List, Set, Dict
import re
from dataclasses import dataclass

@dataclass
class TagRule:
    """Правило для определения тега"""
    keywords: List[str]
    emoji: str

# Правила тегов для классификации
TAG_RULES: Dict[str, TagRule] = {
    "скидка": TagRule(
        keywords=["скидк", "акция", "%", "дешевле", "распродажа", "спец", "цена"],
        emoji="💰"
    ),
    "подарок": TagRule(
        keywords=["в подарок", "подарок", "комплимент", "бесплатно"],
        emoji="🎁"
    ),
    "шеф": TagRule(
        keywords=["шеф", "авторское", "сет", "дегустация", "tasting", "chef"],
        emoji="👨‍🍳"
    ),
    "фестиваль": TagRule(
        keywords=["фестиваль", "ивент", "мероприятие", "событие", "fest"],
        emoji="🎉"
    ),
    "завтрак": TagRule(
        keywords=["завтрак", "утро", "каша", "кофе", "breakfast"],
        emoji="🍳"
    ),
    "бранч": TagRule(
        keywords=["бранч", "brunch", "поздний завтрак"],
        emoji="🥐"
    ),
    "бар": TagRule(
        keywords=["бар", "коктейль", "вино", "пиво", "алкоголь"],
        emoji="🍸"
    ),
    "азия": TagRule(
        keywords=["суши", "роллы", "вок", "рамен", "азиатский"],
        emoji="🍜"
    ),
    "пицца": TagRule(
        keywords=["пицца", "pizza", "пиццерия"],
        emoji="🍕"
    ),
    "веган": TagRule(
        keywords=["веган", "vegan", "растительное", "без мяса"],
        emoji="🥗"
    ),
}

def normalize_text(text: str) -> str:
    """
    Нормализует текст для поиска ключевых слов.
    
    Args:
        text: Исходный текст
        
    Returns:
        str: Нормализованный текст в нижнем регистре без спецсимволов
    """
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    return text

def find_tags(text: str) -> Set[str]:
    """
    Находит теги в тексте на основе правил.
    
    Args:
        text: Текст для анализа
        
    Returns:
        Set[str]: Набор найденных тегов
    """
    normalized_text = normalize_text(text)
    found_tags = set()
    
    for tag, rule in TAG_RULES.items():
        if any(keyword.lower() in normalized_text for keyword in rule.keywords):
            found_tags.add(tag)
    
    return found_tags

def is_hot_content(tags: List[str]) -> bool:
    """
    Определяет, является ли контент горячим на основе тегов.
    
    Контент считается горячим если:
    1. Есть тег "скидка" или "подарок" И
    2. Есть хотя бы 2 других тега
    
    Args:
        tags: Список тегов
        
    Returns:
        bool: True если контент горячий, False иначе
    """
    if len(tags) < 2:
        return False
        
    has_promo = "скидка" in tags or "подарок" in tags
    other_tags = [tag for tag in tags if tag not in ["скидка", "подарок"]]
    
    return has_promo and len(other_tags) >= 2

def extract_price(text: str) -> List[int]:
    """
    Извлекает цены из текста.
    
    Args:
        text: Текст для анализа
        
    Returns:
        List[int]: Отсортированный список найденных цен
    """
    price_patterns = [
        r'(\d+)\s*₽',
        r'(\d+)\s*руб',
        r'(\d+)\s*р\b',
        r'(\d+)\s*rub',
    ]
    
    prices = []
    for pattern in price_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        prices.extend(int(match.group(1)) for match in matches)
    
    return sorted(prices) if prices else [] 