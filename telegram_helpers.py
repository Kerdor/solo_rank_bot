"""
Вспомогательные функции для взаимодействия с ботом через Telethon conversation.
"""

import asyncio

from telethon import events
from telethon.tl.custom import Message

from config import log, BOT_USERNAME
from parsers import classify_warning


async def click_button(message: Message, text: str) -> bool:
    """
    Кликает кнопку, текст которой СОДЕРЖИТ text (а не точное совпадение) —
    у кнопок бывает эмодзи-префикс ("🔥 Горячие источники" и т.п.),
    из-за которого точное сравнение не срабатывало.
    """
    if not message.buttons:
        return False
    for row in message.buttons:
        for button in row:
            if text.strip() in button.text.strip():
                await button.click()
                return True
    return False

async def wait_update(client, timeout: int) -> Message:
    """
    Ждём либо новое сообщение от бота, либо правку старого — что придёт раньше.

    Раньше это делалось через conv.get_response() и conv.get_edit()
    одновременно — из-за этого Telethon иногда путался и падал с ошибкой,
    причём поломка "тянулась" и на следующие обычные вызовы get_response().
    Поэтому здесь просто слушаем сообщения бота напрямую, без конфликта.
    Первый параметр — сам TelegramClient, а не Conversation.
    """
    future = asyncio.get_event_loop().create_future()

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


async def resolve_warning(conv, resp: Message) -> bool:
    """
    Если resp — предупреждение (энергия/HP), чинит через /energy и/или /heal.
    Возвращает True, если предупреждение было и обработано (вызывающий код должен повторить попытку).
    Кнопки подтверждения ('Войти с риском'/'Войти в истощении', 'Отмена') не трогаем.
    """
    text = resp.raw_text
    need_energy, need_hp = classify_warning(text)
    if not (need_energy or need_hp):
        return False

    first_line = text.splitlines()[0] if text else ""
    log.info(f"Предупреждение: энергия={need_energy}, hp={need_hp} ({first_line})")

    if need_energy:
        await conv.send_message("/energy")
        energy_resp = await conv.get_response()
        log.info(f"/energy -> {energy_resp.raw_text}")
    if need_hp:
        await conv.send_message("/heal")
        heal_resp = await conv.get_response()
        log.info(f"/heal -> {heal_resp.raw_text}")
    return True