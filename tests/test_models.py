import pytest
from datetime import datetime
from parser.models import ParsedMessage

def test_parsed_message_to_dict() -> None:
    """Тестирует конвертацию ParsedMessage в словарь"""
    now = datetime.now()
    message = ParsedMessage(
        id="123",
        text="Test message",
        city="Москва",
        tags=["скидка", "азия"],
        is_hot=True,
        short="Short test",
        link="https://t.me/channel/123",
        source="@channel",
        created_at=now,
    )
    
    message_dict = message.to_dict()
    
    assert message_dict["id"] == "123"
    assert message_dict["text"] == "Test message"
    assert message_dict["city"] == "Москва"
    assert message_dict["tags"] == ["скидка", "азия"]
    assert message_dict["is_hot"] is True
    assert message_dict["short"] == "Short test"
    assert message_dict["link"] == "https://t.me/channel/123"
    assert message_dict["source"] == "@channel"
    assert message_dict["created_at"] == now.isoformat()

def test_parsed_message_from_dict() -> None:
    """Тестирует создание ParsedMessage из словаря"""
    now = datetime.now()
    data = {
        "id": "123",
        "text": "Test message",
        "city": "Москва",
        "tags": ["скидка", "азия"],
        "is_hot": True,
        "short": "Short test",
        "link": "https://t.me/channel/123",
        "source": "@channel",
        "created_at": now.isoformat(),
    }
    
    message = ParsedMessage.from_dict(data)
    
    assert message.id == "123"
    assert message.text == "Test message"
    assert message.city == "Москва"
    assert message.tags == ["скидка", "азия"]
    assert message.is_hot is True
    assert message.short == "Short test"
    assert message.link == "https://t.me/channel/123"
    assert message.source == "@channel"
    assert message.created_at.isoformat() == now.isoformat()

def test_parsed_message_from_dict_without_created_at() -> None:
    """Тестирует создание ParsedMessage из словаря без даты создания"""
    data = {
        "id": "123",
        "text": "Test message",
        "city": "Москва",
        "tags": ["скидка", "азия"],
        "is_hot": True,
        "short": "Short test",
        "link": "https://t.me/channel/123",
        "source": "@channel",
    }
    
    message = ParsedMessage.from_dict(data)
    
    assert isinstance(message.created_at, datetime)
    assert message.id == "123" 