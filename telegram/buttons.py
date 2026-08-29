"""Работа с inline/reply-кнопками Telegram."""

from telethon.tl.custom import Message


async def click_button(message: Message, text: str) -> bool:
    """Кликает кнопку, текст которой содержит text."""
    if not message.buttons:
        return False
    for row in message.buttons:
        for button in row:
            if text.strip() in button.text.strip():
                await button.click()
                return True
    return False
