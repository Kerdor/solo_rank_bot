"""Selfbot для авто-прохождения данжей в Solo Rank."""

import asyncio

from telethon import TelegramClient

from config import API_ID, API_HASH, SESSION_NAME, log
from dungeon.cycle import run_cycle


async def main():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.start()
    log.info("Клиент запущен, начинаю бесконечный цикл данжей.")

    while True:
        try:
            await run_cycle(client)
        except asyncio.TimeoutError as e:
            log.error(f"Таймаут ожидания ответа бота: {e}. Пауза 30с и повтор.")
            await asyncio.sleep(30)
        except Exception as e:
            log.exception(f"Неожиданная ошибка: {e}. Пауза 30с и повтор.")
            await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(main())
