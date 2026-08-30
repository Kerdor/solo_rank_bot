"""Работа с inline/reply-кнопками Telegram."""

from telethon.tl.custom import Message


def _normalize(text: str) -> str:
    return " ".join(text.split()).strip()


async def click_button(message: Message, text: str) -> bool:
    """Кликает кнопку по точному совпадению или вхождению текста."""
    if not message.buttons:
        return False

    target = _normalize(text)
    buttons = [button for row in message.buttons for button in row]

    for button in buttons:
        button_text = _normalize(button.text)
        if button_text == target or target in button_text:
            await button.click()
            return True

    return False
