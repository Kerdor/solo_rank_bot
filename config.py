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

SESSION_NAME = "auth/dungeon_selfbot"

BOT_USERNAME = "solo_rank_bot"

# Таймауты ожидания ответа бота (сек)
RESPONSE_TIMEOUT = 30
REPORT_EXTRA_WAIT = 90
HOT_SPRINGS_MSG_TIMEOUT = 20 * 60
LOW_HP_THRESHOLD_PERCENT = 20

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("dungeon_bot")