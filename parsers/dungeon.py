"""Парсеры списка данжей."""

import re


RESETS_RE = re.compile(r"Доступно сбросов:\s*(\d+)\s*/\s*(\d+)")
ENTRY_RE = re.compile(
    r"(\d+)\.\s*(.+?)\s*\n\[Ранг:\s*([A-ZА-Я]+)\]\s*\|\s*🛡\s*DEF:\s*(\d+)"
)
DUNGEON_ETA_RE = re.compile(r"Отчёт будет готов через\s*(\d+)\s*минут")


def parse_resets_left(text: str) -> int:
    m = RESETS_RE.search(text)
    if not m:
        raise ValueError(f"Не смог найти 'Доступно сбросов' в списке данжей:\n{text}")
    return int(m.group(1))


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
