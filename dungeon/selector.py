"""Выбор данжа по мощи охотника."""

from config import log


def choose_dungeon(entries, power: int, resets_left: int, favorite_defs=None):
    """
    Возвращает (dungeon, need_reset: bool).
    need_reset=True значит: сначала жать 'Сбросить список'.

    favorite_defs — DEF данжей из 'Избранного' в порядке приоритета.
    Избранный данж выбирается только если мощь строго больше его DEF.
    """
    favorite_defs = favorite_defs or []

    for favorite_def in favorite_defs:
        if power <= favorite_def:
            continue

        favorite = next(
            (e for e in entries if e["def"] == favorite_def),
            None,
        )
        if favorite is not None:
            log.info(
                f"Выбираю избранный данж {favorite['name']} "
                f"(DEF {favorite['def']}, мощь {power})."
            )
            return favorite, False

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
