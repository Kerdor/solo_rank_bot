"""Обработка предупреждений о недостатке энергии и HP."""

from telethon.tl.custom import Message

from config import log
from parsers.messages import classify_warning


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
    if need_hp:
        await conv.send_message("/heal")
        heal_resp = await conv.get_response()
        log.info(f"/heal -> {heal_resp.raw_text}")
    return True
