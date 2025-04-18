KEYWORDS = ["скидка", "бесплатно", "открытие", "завтрак", "акция"]


def filter_message(text: str) -> bool:
    """
    Проверяет, содержит ли текст сообщения ключевые слова.

    Args:
        text: Текст сообщения для проверки.

    Returns:
        True, если текст содержит хотя бы одно ключевое слово (без учета регистра),
        иначе False.
    """
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in KEYWORDS) 