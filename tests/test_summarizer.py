import pytest
from parser.summarizer import create_short_title, extract_date_info

@pytest.mark.parametrize(
    "text,tags,city,expected",
    [
        (
            "Скидка 20% на все суши и роллы! Приходите к нам.",
            ["скидка", "азия"],
            "Москва",
            "💰🍜 Скидка 20% на все суши и роллы!",
        ),
        (
            "Новый шеф-повар представляет авторское меню за 1500₽",
            ["шеф"],
            "Москва",
            "👨‍🍳 Новый шеф-повар представляет авторское меню • от 1500₽",
        ),
        (
            "Очень длинное предложение, которое нужно обрезать, потому что оно превышает лимит в сто символов и может занять слишком много места",
            [],
            "Москва",
            "Очень длинное предложение, которое нужно обрезать, потому что оно превышает лимит в сто символов и может...",
        ),
    ],
)
def test_create_short_title(text: str, tags: list[str], city: str, expected: str) -> None:
    assert create_short_title(text, tags, city) == expected

@pytest.mark.parametrize(
    "text,expected",
    [
        (
            "Акция действует до 15 января",
            "15 января",
        ),
        (
            "Начиная с 1 марта новое меню",
            "1 марта",
        ),
        (
            "Мероприятие пройдет 25 декабря",
            "25 декабря",
        ),
        (
            "Текст без даты",
            None,
        ),
    ],
)
def test_extract_date_info(text: str, expected: str | None) -> None:
    assert extract_date_info(text) == expected 