"""Работа с inline/reply-кнопками Telegram."""

from telethon.tl.custom import Message

from config import log


def _normalize(text: str) -> str:
    return " ".join(text.split()).strip()


async def click_button(message: Message, text: str) -> bool:
    """Кликает кнопку по точному совпадению или вхождению текста."""
    if not message.buttons:
        log.warning(f"Попытка нажать {text!r}, но в сообщении нет кнопок.")
        return False

    target = _normalize(text)
    buttons = [button for row in message.buttons for button in row]
    log.info(
        f"Ищу кнопку {target!r}. Кнопки в сообщении: "
        f"{[_normalize(button.text) for button in buttons]}"
    )

    for button in buttons:
        button_text = _normalize(button.text)
        if button_text == target or target in button_text:
            log.info(f"Нашёл кнопку {button_text!r}, нажимаю...")
            try:
                await button.click()
            except Exception as e:
                log.exception(f"Ошибка клика по кнопке {button_text!r}: {e}")
                return False
            log.info(f"Кнопка {button_text!r} нажата успешно.")
            return True

    log.warning(f"Кнопка {target!r} не найдена.")
    return False
