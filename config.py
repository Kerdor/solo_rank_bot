"""
Настройки selfbot'а для авто-прохождения данжей в Solo Rank.
"""

import logging
import os

from dotenv import load_dotenv


load_dotenv()

# ============================== НАСТРОЙКИ ==============================

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_USERNAME = os.getenv("BOT_USERNAME", "solo_rank_bot")
SESSION_NAME = os.getenv("SESSION_NAME", "auth/dungeon_selfbot")

if not API_ID or not API_HASH:
    raise RuntimeError("Не заданы API_ID и API_HASH в .env")

# Таймауты ожидания ответа бота (сек)
RESPONSE_TIMEOUT = 30
REPORT_EXTRA_WAIT = 90
STALE_DUNGEON_EXTRA_WAIT = 10 * 60
DEFAULT_DUNGEON_ETA_MINUTES = 3
HOT_SPRINGS_MSG_TIMEOUT = 20 * 60
LOW_HP_THRESHOLD_PERCENT = 20

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("dungeon_bot")
