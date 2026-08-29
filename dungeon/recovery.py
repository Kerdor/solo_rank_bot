"""Обработка предупреждений о недостатке энергии и HP."""

import asyncio

from telethon.tl.custom import Message

from config import log
from parsers.messages import classify_warning
from parsers.profile import parse_energy


ENERGY_EMPTY_MARKER = "Этот предмет нельзя использовать для восстановления энергии."


async def wait_for_energy(conv) -> None:
    """Ждёт естественного восстановления энергии до максимума."""
    await conv.send_message("/profile")
    profile = await conv.get_response()
    energy = parse_energy(profile.raw_text)

    if energy is None:
        log.warning("Не удалось определить время восстановления энергии из /profile.")
        return

    current, maximum, minutes_to_full = energy
    if current >= maximum:
        return

    log.info(
        f"Кристаллы энергии закончились: {current}/{maximum}. "
        f"Ожидаю естественное восстановление до полного ({minutes_to_full} мин)."
    )
    await asyncio.sleep(minutes_to_full * 60 + 5)


async def resolve_warning(conv, resp: Message) -> bool:
    """Обрабатывает предупреждение через /energy и/или /heal."""
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

        if ENERGY_EMPTY_MARKER in energy_resp.raw_text:
            await wait_for_energy(conv)

    if need_hp:
        await conv.send_message("/heal")
        heal_resp = await conv.get_response()
        log.info(f"/heal -> {heal_resp.raw_text}")
    return True
