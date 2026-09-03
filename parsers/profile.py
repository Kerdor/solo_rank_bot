"""Парсеры данных профиля."""

import re


POWER_RE = re.compile(r"Мощь:\s*(\d+)")
HP_PERCENT_RE = re.compile(r"HP:\s*\d+/\d+\s*\((\d+)%\)")
ENERGY_RE = re.compile(r"⚡️\s*(\d+)\s*/\s*(\d+)\s*→\s*(?:max|Макс\.)\s*(?:(\d+)ч\s*)?(?:(\d+)м)?")


def parse_power(text: str) -> int:
    m = POWER_RE.search(text)
    if not m:
        raise ValueError(f"Не смог найти 'Мощь' в ответе /profile:\n{text}")
    return int(m.group(1))


def parse_hp_percent(text: str):
    """Возвращает текущий % HP из профиля, либо None если не нашли."""
    m = HP_PERCENT_RE.search(text)
    return int(m.group(1)) if m else None


def parse_energy(text: str):
    """Возвращает (текущая энергия, максимум, минут до полного восстановления) или None."""
    m = ENERGY_RE.search(text)
    if not m:
        return None

    current = int(m.group(1))
    maximum = int(m.group(2))
    hours = int(m.group(3) or 0)
    minutes = int(m.group(4) or 0)
    return current, maximum, hours * 60 + minutes
