"""Маркеры и классификация сообщений бота."""

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
ENTER_SUCCESS_MARKER = "Инстанс-данж запущен"
REPORT_MARKER = "Отчёт инстанс-данжа"

ENERGY_WARNING_MARKER = "⚠️ Недостаточно энергии."
EXHAUSTION_BUTTON = "Войти в истощении"


def classify_warning(text: str):
    """Возвращает (need_energy, need_hp) или (False, False)."""
    if WARN_NO_ENERGY_AND_HP in text:
        return True, True
    need_energy = WARN_NO_ENERGY in text
    need_hp = WARN_LOW_HP in text
    return need_energy, need_hp
