"""Парсеры данных профиля."""

import re


POWER_RE = re.compile(r"Мощь:\s*(\d+)")
HP_PERCENT_RE = re.compile(r"HP:\s*\d+/\d+\s*\((\d+)%\)")


def parse_power(text: str) -> int:
    m = POWER_RE.search(text)
    if not m:
        raise ValueError(f"Не смог найти 'Мощь' в ответе /profile:\n{text}")
    return int(m.group(1))


def parse_hp_percent(text: str):
    """Возвращает текущий % HP из профиля, либо None если не нашли."""
    m = HP_PERCENT_RE.search(text)
    return int(m.group(1)) if m else None
