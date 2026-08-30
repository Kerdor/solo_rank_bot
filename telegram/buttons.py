"""Работа с inline/reply-кнопками Telegram."""

from telethon.tl.custom import Message

from config import log


def _normalize(text: str) -> str:
    return " ".join(text.split()).strip()


async def click_button(message: Message, text: str) -> bool:
    """Кликает кнопку по точному совпадению или вхождению текста."""
    if not message.buttons:
        log.info(f"В сообщении нет кнопок. Ищу: '{text}'")
        return False

    target = _normalize(text)
    buttons = [button for row in message.buttons for button in row]
    log.info(f"Ищу кнопку '{target}'. Кнопки в сообщении: {[button.text for button in buttons]}")

    for button in buttons:
        button_text = _normalize(button.text)
        if button_text == target or target in button_text:
            log.info(f"Нашёл кнопку '{button_text}', нажимаю...")
            try:
                await button.click()
            except Exception as e:
                log.exception(f"Ошибка при нажатии кнопки '{button_text}': {e}")
                return False
            log.info(f"Кнопка '{button_text}' нажата успешно.")
            return True

    log.warning(f"Кнопка '{target}' не найдена.")
    return False
