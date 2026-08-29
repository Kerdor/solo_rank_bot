from parsers.dungeon import parse_dungeons, parse_resets_left
from parsers.messages import classify_warning
from parsers.profile import parse_hp_percent, parse_power


def test_parse_profile():
    text = "Мощь: 12345\nHP: 800/1000 (80%)"
    assert parse_power(text) == 12345
    assert parse_hp_percent(text) == 80


def test_parse_dungeons():
    text = (
        "Доступно сбросов: 2 / 5\n\n"
        "1. Тёмная пещера\n[Ранг: A] | 🛡 DEF: 1000\n"
        "2. Заброшенный замок\n[Ранг: S] | 🛡 DEF: 2000"
    )
    assert parse_resets_left(text) == 2
    assert parse_dungeons(text) == [
        {"idx": 1, "name": "Тёмная пещера", "rank": "A", "def": 1000},
        {"idx": 2, "name": "Заброшенный замок", "rank": "S", "def": 2000},
    ]


def test_classify_warning():
    assert classify_warning("Недостаточно энергии") == (True, False)
    assert classify_warning("Низкое HP") == (False, True)
    assert classify_warning("Недостаточно энергии и низкое HP") == (True, True)
    assert classify_warning("Всё в порядке") == (False, False)
