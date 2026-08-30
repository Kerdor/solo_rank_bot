"""Ожидание новых и отредактированных сообщений Telegram."""

import asyncio

from telethon import events
from telethon.tl.custom import Message

from config import BOT_USERNAME
from telegram.buttons import click_button


async def wait_update(client, timeout: int) -> Message:
    """Ждёт новое или изменённое сообщение от целевого бота."""
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


async def click_and_wait_update(client, message: Message, button_text: str, timeout: int) -> Message | None:
    """Ставит обработчик заранее, нажимает кнопку и ждёт ответ/редактирование этого сообщения."""
    future = asyncio.get_running_loop().create_future()

    async def handler(event):
        event_message = event.message
        if event_message.chat_id != message.chat_id:
            return
        if event_message.id != message.id:
            return
        if not future.done():
            future.set_result(event_message)

    client.add_event_handler(handler, events.MessageEdited(chats=BOT_USERNAME))
    client.add_event_handler(handler, events.NewMessage(chats=BOT_USERNAME))
    try:
        log_text = await _click_with_logging(message, button_text)
        if not log_text:
            return None
        return await asyncio.wait_for(future, timeout=timeout)
    finally:
        client.remove_event_handler(handler, events.MessageEdited(chats=BOT_USERNAME))
        client.remove_event_handler(handler, events.NewMessage(chats=BOT_USERNAME))


async def _click_with_logging(message: Message, button_text: str) -> bool:
    """Нажимает кнопку через общий helper."""
    return await click_button(message, button_text)
