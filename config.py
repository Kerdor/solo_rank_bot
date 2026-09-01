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

# Аккаунты Telegram. Каждый аккаунт использует отдельный session-файл.
# PHONE нужен только для первичной авторизации; после создания .session
# повторный ввод кода обычно не потребуется.
ACCOUNTS = []

for index in range(1, 4):
    phone = os.getenv(f"PHONE_{index}", "").strip()
    session_name = os.getenv(
        f"SESSION_NAME_{index}",
        f"auth/dungeon_selfbot_{index}",
    ).strip()

    if phone or session_name:
        ACCOUNTS.append({
            "phone": phone,
            "session_name": session_name,
        })

if not ACCOUNTS:
    # Обратная совместимость со старым .env с одним SESSION_NAME.
    ACCOUNTS.append({
        "phone": os.getenv("PHONE", "").strip(),
        "session_name": os.getenv("SESSION_NAME", "auth/dungeon_selfbot").strip(),
    })

if not API_ID or not API_HASH:
    raise RuntimeError("Не заданы API_ID и API_HASH в .env")

# Таймауты ожидания ответа бота (сек)
RESPONSE_TIMEOUT = 30
REPORT_EXTRA_WAIT = 90
STALE_DUNGEON_EXTRA_WAIT = 10 * 60
DEFAULT_DUNGEON_ETA_MINUTES = 3
HOT_SPRINGS_MSG_TIMEOUT = 20 * 60
LOW_HP_THRESHOLD_PERCENT = 20
RETRY_DELAY = 30

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("dungeon_bot")
