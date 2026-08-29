"""Selfbot для авто-прохождения данжей в Solo Rank."""

import asyncio

from telethon import TelegramClient

from config import API_ID, API_HASH, SESSION_NAME, RETRY_DELAY, log
from dungeon.cycle import run_cycle


async def main():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()
    log.info("Клиент запущен, начинаю бесконечный цикл данжей.")

    while True:
        try:
            await run_cycle(client)
        except asyncio.TimeoutError as e:
            log.error(f"Таймаут ожидания ответа бота: {e}. Пауза {RETRY_DELAY}с и повтор.")
            await asyncio.sleep(RETRY_DELAY)
        except Exception as e:
            log.exception(f"Неожиданная ошибка: {e}. Пауза {RETRY_DELAY}с и повтор.")
            await asyncio.sleep(RETRY_DELAY)


if __name__ == "__main__":
    asyncio.run(main())
