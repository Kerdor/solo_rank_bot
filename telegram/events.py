"""Ожидание новых и отредактированных сообщений Telegram."""

import asyncio

from telethon import events
from telethon.tl.custom import Message

from config import BOT_USERNAME, log
from telegram.buttons import click_button


async def wait_update(client, timeout: int, message_id: int | None = None) -> Message:
    """Ждёт новое или изменённое сообщение от целевого бота."""
    future = asyncio.get_running_loop().create_future()

    async def handler(event):
        event_message = event.message
        if event_message.chat_id != await client.get_peer_id(BOT_USERNAME):
            return
        if message_id is not None and event_message.id != message_id:
            return
        if not future.done():
            future.set_result(event_message)

    client.add_event_handler(handler, events.NewMessage(chats=BOT_USERNAME))
    client.add_event_handler(handler, events.MessageEdited(chats=BOT_USERNAME))
    try:
        return await asyncio.wait_for(future, timeout=timeout)
    finally:
        client.remove_event_handler(handler, events.NewMessage(chats=BOT_USERNAME))
        client.remove_event_handler(handler, events.MessageEdited(chats=BOT_USERNAME))


async def click_and_wait_update(client, message: Message, button_text: str, timeout: int) -> Message | None:
    """Ставит обработчик заранее, нажимает кнопку и ждёт редактирование этого сообщения."""
    future = asyncio.get_running_loop().create_future()

    async def handler(event):
        event_message = event.message
        if event_message.id != message.id:
            return
        if event_message.chat_id != message.chat_id:
            return
        if not future.done():
            future.set_result(event_message)

    client.add_event_handler(handler, events.MessageEdited(chats=BOT_USERNAME))
    try:
        if not await click_button(message, button_text):
            return None
        updated_message = await asyncio.wait_for(future, timeout=timeout)
        log.info(
            f"Сообщение #{updated_message.id} изменилось после нажатия '{button_text}'. "
            f"Новые кнопки: {[button.text for row in updated_message.buttons or [] for button in row]}"
        )
        return updated_message
    finally:
        client.remove_event_handler(handler, events.MessageEdited(chats=BOT_USERNAME))
