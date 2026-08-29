"""Выбор данжа по мощи охотника."""

from config import log


def choose_dungeon(entries, power: int, resets_left: int):
    """
    Возвращает (dungeon, need_reset: bool).
    need_reset=True значит: сначала жать 'Сбросить список'.
    """
    candidates = [e for e in entries if e["def"] <= power]
    if candidates:
        return max(candidates, key=lambda e: e["def"]), False

    if resets_left > 0:
        return None, True

    weakest = min(entries, key=lambda e: e["def"])
    log.warning(
        "Все данжи сильнее мощи и сбросов 0/5 — рискуем, берём самый слабый: "
        f"{weakest['name']} (DEF {weakest['def']})"
    )
    return weakest, False
