"""Ожидание новых и отредактированных сообщений Telegram."""

import asyncio

from telethon import events
from telethon.tl.custom import Message

from config import BOT_USERNAME


async def wait_update(client, timeout: int) -> Message:
    """Ждёт новое сообщение или правку старого от целевого бота."""
    future = asyncio.get_running_loop().create_future()

    async def handler(event):
        if not future.done():
            future.set_result(event.message)

    client.add_event_handler(handler, events.NewMessage(chats=BOT_USERNAME))
    client.add_event_handler(handler, events.MessageEdited(chats=BOT_USERNAME))
    try:
        return await asyncio.wait_for(future, timeout=timeout)
    finally:
        client.remove_event_handler(handler, events.NewMessage(chats=BOT_USERNAME))
        client.remove_event_handler(handler, events.MessageEdited(chats=BOT_USERNAME))
