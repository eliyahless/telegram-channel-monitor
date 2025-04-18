import pytest
from parser.classifiers import normalize_text, find_tags, is_hot_content, extract_price, TAG_RULES

@pytest.mark.parametrize(
    "input_text,expected",
    [
        ("Привет, мир!", "привет мир"),
        ("Test123!@#", "test123"),
        ("ВЕРХНИЙ регистр", "верхний регистр"),
    ],
)
def test_normalize_text(input_text: str, expected: str) -> None:
    assert normalize_text(input_text) == expected

@pytest.mark.parametrize(
    "input_text,expected_tags",
    [
        (
            "Скидка 20% на все суши и роллы!",
            {"скидка", "азия"},
        ),
        (
            "Новый шеф-повар представляет авторское меню",
            {"шеф"},
        ),
        (
            "Веганский бранч каждое воскресенье",
            {"веган", "бранч"},
        ),
        (
            "Обычный текст без тегов",
            set(),
        ),
    ],
)
def test_find_tags(input_text: str, expected_tags: set[str]) -> None:
    assert find_tags(input_text) == expected_tags

@pytest.mark.parametrize(
    "tags,expected",
    [
        (["скидка", "азия", "бар"], True),  # Скидка + 2 других тега
        (["подарок", "шеф", "веган"], True),  # Подарок + 2 других тега
        (["скидка", "азия"], False),  # Недостаточно других тегов
        (["азия", "бар", "веган"], False),  # Нет промо-тегов
        ([], False),  # Пустой список
    ],
)
def test_is_hot_content(tags: list[str], expected: bool) -> None:
    assert is_hot_content(tags) == expected

@pytest.mark.parametrize(
    "input_text,expected_prices",
    [
        (
            "Стоимость 100₽, специальная цена 80₽",
            [80, 100],
        ),
        (
            "Всего за 199 руб",
            [199],
        ),
        (
            "Цена: 500р",
            [500],
        ),
        (
            "Текст без цен",
            [],
        ),
    ],
)
def test_extract_price(input_text: str, expected_prices: list[int]) -> None:
    assert extract_price(input_text) == expected_prices

def test_tag_rules_structure() -> None:
    """Проверяет структуру правил тегов"""
    for tag, rule in TAG_RULES.items():
        assert isinstance(tag, str)
        assert isinstance(rule.keywords, list)
        assert all(isinstance(k, str) for k in rule.keywords)
        assert isinstance(rule.emoji, str)
        assert len(rule.emoji) > 0 