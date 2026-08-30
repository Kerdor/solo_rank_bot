"""Работа с inline/reply-кнопками Telegram."""

from telethon.tl.custom import Message


def _normalize(text: str) -> str:
    return " ".join(text.split()).strip()


async def click_button(message: Message, text: str) -> bool:
    """Кликает кнопку с точным совпадением или содержащую искомый текст."""
    if not message.buttons:
        return False

    target = _normalize(text)
    buttons = [button for row in message.buttons for button in row]

    for button in buttons:
        button_text = _normalize(button.text)
        if button_text == target:
            await button.click()
            return True

    for button in buttons:
        button_text = _normalize(button.text)
        if target in button_text:
            await button.click()
            return True

    return False
