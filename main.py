"""Selfbot для авто-прохождения данжей в Solo Rank."""

import asyncio

from telethon import TelegramClient

from config import API_ID, API_HASH, ACCOUNTS, RETRY_DELAY, log
from dungeon.cycle import run_cycle


async def run_account(index, account):
    """Запускает бесконечный цикл данжей для одного Telegram-аккаунта."""
    session_name = account["session_name"]
    phone = account["phone"]
    client = TelegramClient(session_name, API_ID, API_HASH)

    try:
        log.info(f"[АККАУНТ {index}] Запуск: {session_name}")
        if phone:
            await client.start(phone=phone)
        else:
            await client.start()
        log.info(f"[АККАУНТ {index}] Клиент запущен, начинаю бесконечный цикл данжей.")

        while True:
            try:
                await run_cycle(client, account_index=index)
            except asyncio.TimeoutError as e:
                log.error(
                    f"[АККАУНТ {index}] Таймаут ожидания ответа бота: {e}. "
                    f"Пауза {RETRY_DELAY}с и повтор."
                )
                await asyncio.sleep(RETRY_DELAY)
            except Exception as e:
                log.exception(
                    f"[АККАУНТ {index}] Неожиданная ошибка: {e}. "
                    f"Пауза {RETRY_DELAY}с и повтор."
                )
                await asyncio.sleep(RETRY_DELAY)
    finally:
        await client.disconnect()
        log.info(f"[АККАУНТ {index}] Клиент отключён.")


async def main():
    if not ACCOUNTS:
        raise RuntimeError("Не настроен ни один Telegram-аккаунт.")

    log.info(f"Настроено аккаунтов: {len(ACCOUNTS)}")

    # Авторизация/подключение выполняется последовательно, чтобы Telegram-коды
    # и возможный ввод 2FA не смешивались в консоли. После этого все аккаунты
    # работают одновременно в отдельных asyncio-задачах.
    clients = []
    for index, account in enumerate(ACCOUNTS, start=1):
        client = TelegramClient(account["session_name"], API_ID, API_HASH)
        log.info(f"[АККАУНТ {index}] Подключение: {account['session_name']}")
        if account["phone"]:
            await client.start(phone=account["phone"])
        else:
            await client.start()
        clients.append((index, account, client))
        log.info(f"[АККАУНТ {index}] Авторизация завершена.")

    async def run_connected_account(index, client):
        try:
            log.info(f"[АККАУНТ {index}] Начинаю бесконечный цикл данжей.")
            while True:
                try:
                    await run_cycle(client, account_index=index)
                except asyncio.TimeoutError as e:
                    log.error(
                        f"[АККАУНТ {index}] Таймаут ожидания ответа бота: {e}. "
                        f"Пауза {RETRY_DELAY}с и повтор."
                    )
                    await asyncio.sleep(RETRY_DELAY)
                except Exception as e:
                    log.exception(
                        f"[АККАУНТ {index}] Неожиданная ошибка: {e}. "
                        f"Пауза {RETRY_DELAY}с и повтор."
                    )
                    await asyncio.sleep(RETRY_DELAY)
        finally:
            await client.disconnect()
            log.info(f"[АККАУНТ {index}] Клиент отключён.")

    try:
        await asyncio.gather(
            *(run_connected_account(index, client) for index, _, client in clients)
        )
    finally:
        for _, _, client in clients:
            if client.is_connected():
                await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
