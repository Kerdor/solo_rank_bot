"""Обработка предупреждений о недостатке энергии и HP."""

import asyncio

from telethon.tl.custom import Message

from config import log
from parsers.messages import classify_warning, ENERGY_WARNING_MARKER, EXHAUSTION_BUTTON
from parsers.profile import parse_energy
from telegram.buttons import click_button


ENERGY_EMPTY_MARKER = "Этот предмет нельзя использовать для восстановления энергии."
ENERGY_CHECK_INTERVAL = 5 * 60
COMMAND_DELAY = 1.5


async def wait_for_energy(conv, required_energy: int) -> None:
    """Периодически проверяет профиль и ждёт нужное количество энергии."""
    while True:
        await conv.send_message("/profile")
        profile = await conv.get_response()
        energy = parse_energy(profile.raw_text)

        if energy is None:
            log.warning("Не удалось определить энергию из /profile. Повторю проверку через 5 минут.")
        else:
            current, maximum, minutes_to_full = energy
            log.info(
                f"Энергия: {current}/{maximum}, требуется: {required_energy}. "
                f"До полного: {minutes_to_full} мин."
            )
            if current >= required_energy:
                log.info(f"Энергии достаточно для данжа: {current}/{required_energy}.")
                return

        await asyncio.sleep(ENERGY_CHECK_INTERVAL)


async def resolve_warning(conv, resp: Message, required_energy: int = 0) -> str | bool:
    """Обрабатывает предупреждение через /energy, истощение и/или /heal."""
    text = resp.raw_text
    need_energy, need_hp = classify_warning(text)
    if not (need_energy or need_hp):
        return False

    first_line = text.splitlines()[0] if text else ""
    log.info(f"Предупреждение: энергия={need_energy}, hp={need_hp} ({first_line})")

    if need_energy:
        await asyncio.sleep(COMMAND_DELAY)
        await conv.send_message("/energy")
        energy_resp = await conv.get_response()
        log.info(f"/energy -> {energy_resp.raw_text}")

        if ENERGY_EMPTY_MARKER in energy_resp.raw_text:
            if not need_hp and ENERGY_WARNING_MARKER in text:
                if await click_button(resp, EXHAUSTION_BUTTON):
                    log.info("Кристаллов нет, HP достаточно — вхожу в данж в режиме истощения.")
                    return "started"
            await wait_for_energy(conv, required_energy)

    if need_hp:
        await asyncio.sleep(COMMAND_DELAY)
        await conv.send_message("/heal")
        heal_resp = await conv.get_response()
        log.info(f"/heal -> {heal_resp.raw_text}")

    return "retry"
