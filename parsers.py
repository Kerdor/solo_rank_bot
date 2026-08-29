"""
Парсеры ответов бота и логика выбора данжа.
"""

import re

from config import log

# ============================== ПАРСЕРЫ ==============================

POWER_RE = re.compile(r"Мощь:\s*(\d+)")
RESETS_RE = re.compile(r"Доступно сбросов:\s*(\d+)\s*/\s*(\d+)")
ENTRY_RE = re.compile(
    r"(\d+)\.\s*(.+?)\s*\n\[Ранг:\s*([A-ZА-Я]+)\]\s*\|\s*🛡\s*DEF:\s*(\d+)"
)
DUNGEON_ETA_RE = re.compile(r"Отчёт будет готов через\s*(\d+)\s*минут")

WARN_NO_ENERGY_AND_HP = "Недостаточно энергии и низкое HP"
WARN_NO_ENERGY = "Недостаточно энергии"
WARN_LOW_HP = "Низкое HP"

ALREADY_IN_DUNGEON_MARKER = "уже находишься в данже"

INJURY_MARKER = "Раны заживут через"
HOT_SPRINGS_BUTTON = "Горячие источники"
ALREADY_IN_SPRINGS_MARKER = "Горячие источники: сеанс"
RECOVERY_DONE_MARKER = "Восстановление завершено"
INJURY_STATUS_MARKER = "Травма:"
START_RECOVERY_BUTTON = "Начать восстановление"


HP_PERCENT_RE = re.compile(r"HP:\s*\d+/\d+\s*\((\d+)%\)")

ENTER_SUCCESS_MARKER = "Инстанс-данж запущен"
REPORT_MARKER = "Отчёт инстанс-данжа"


def parse_power(text: str) -> int:
    m = POWER_RE.search(text)
    if not m:
        raise ValueError(f"Не смог найти 'Мощь' в ответе /profile:\n{text}")
    return int(m.group(1))


def parse_resets_left(text: str) -> int:
    m = RESETS_RE.search(text)
    if not m:
        raise ValueError(f"Не смог найти 'Доступно сбросов' в списке данжей:\n{text}")
    return int(m.group(1))


def parse_hp_percent(text: str):
    """Возвращает текущий % HP из профиля, либо None если не нашли."""
    m = HP_PERCENT_RE.search(text)
    return int(m.group(1)) if m else None


def parse_dungeons(text: str):
    """Возвращает список dict: {idx, name, rank, def}."""
    entries = []
    for m in ENTRY_RE.finditer(text):
        idx, name, rank, defense = m.groups()
        entries.append(
            {
                "idx": int(idx),
                "name": name.strip(),
                "rank": rank,
                "def": int(defense),
            }
        )
    if not entries:
        raise ValueError(f"Не смог распарсить список данжей:\n{text}")
    return entries


def choose_dungeon(entries, power: int, resets_left: int):
    """
    Возвращает (dungeon, need_reset: bool).
    need_reset=True значит: сначала жать 'Сбросить список', этот dungeon не финальный.
    """
    candidates = [e for e in entries if e["def"] <= power]
    if candidates:
        return max(candidates, key=lambda e: e["def"]), False

    if resets_left > 0:
        return None, True

    # все данжи сильнее и сбросов нет -> берём самый слабый несмотря на риск
    weakest = min(entries, key=lambda e: e["def"])
    log.warning(
        "Все данжи сильнее мощи и сбросов 0/5 — рискуем, берём самый слабый: "
        f"{weakest['name']} (DEF {weakest['def']})"
    )
    return weakest, False


def classify_warning(text: str):
    """Возвращает (need_energy, need_hp) или (False, False) если предупреждения нет."""
    if WARN_NO_ENERGY_AND_HP in text:
        return True, True
    need_energy = WARN_NO_ENERGY in text
    need_hp = WARN_LOW_HP in text
    return need_energy, need_hp