"""
Настройки selfbot'а для авто-прохождения данжей в Solo Rank.
"""

import logging

# ============================== НАСТРОЙКИ ==============================

API_ID = 33401351          # <-- твой api_id с my.telegram.org
API_HASH = "ea57b297b80d905007d8a85f33b29ca7"   # <-- твой api_hash
SESSION_NAME = "dungeon_selfbot"  # имя файла сессии (создастся сам)

BOT_USERNAME = "solo_rank_bot"  # <-- юзернейм/id целевого бота, без @ (или числовой id)

# Таймауты ожидания ответа бота (сек)
RESPONSE_TIMEOUT = 30      # обычный ответ (profile/dungeon/energy/heal/enter)
REPORT_EXTRA_WAIT = 90     # запас сверх заявленного времени данжа на ожидание отчёта
HOT_SPRINGS_MSG_TIMEOUT = 20 * 60  # ожидание очередного сообщения от бота в источниках (сек)
LOW_HP_THRESHOLD_PERCENT = 20  # если HP меньше этого % и нет травмы -> /heal

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("dungeon_bot")