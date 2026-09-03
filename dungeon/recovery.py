"""Обработка предупреждений о недостатке энергии и HP."""

import asyncio

from telethon.tl.custom import Message

from config import log
from parsers.messages import classify_warning, ENERGY_WARNING_MARKER
from parsers.profile import parse_energy, parse_hp_percent
from telegram.buttons import click_button


ENERGY_EMPTY_MARKER = "Этот предмет нельзя использовать для восстановления энергии."
ENERGY_FULL_MARKER = "Энергия уже полная."
HEAL_EMPTY_MARKER = "Лечебный предмет не найден в инвентаре."
TOO_MANY_COMMANDS_MARKER = "Слишком много команд. Подожди секунду."
ENERGY_CHECK_INTERVAL = 5 * 60
HP_CHECK_INTERVAL = 60
SAFE_HP_THRESHOLD_PERCENT = 30
COMMAND_DELAY = 1.2


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


async def wait_for_natural_hp_recovery(conv) -> None:
    """Периодически проверяет профиль и ждёт безопасного уровня HP."""
    while True:
        await conv.send_message("/profile")
        profile = await conv.get_response()
        hp_percent = parse_hp_percent(profile.raw_text)

        if hp_percent is None:
            log.warning("Не удалось определить HP из /profile. Повторю проверку через 1 минуту.")
        else:
            log.info(f"Естественное восстановление HP: {hp_percent}%")
            if hp_percent >= SAFE_HP_THRESHOLD_PERCENT:
                log.info(
                    f"HP восстановилось до безопасного уровня: {hp_percent}% "
                    f"(порог {SAFE_HP_THRESHOLD_PERCENT}%)."
                )
                return

        await asyncio.sleep(HP_CHECK_INTERVAL)


async def prepare_dungeon_resources(conv, required_energy: int, hp_percent: int | None) -> None:
    """Подготавливает HP и энергию перед входом в данж без режима истощения."""
    await conv.send_message("/profile")
    profile = await conv.get_response()
    current_hp = parse_hp_percent(profile.raw_text)
    energy = parse_energy(profile.raw_text)

    if current_hp is None:
        current_hp = hp_percent

    need_hp = current_hp is not None and current_hp < SAFE_HP_THRESHOLD_PERCENT
    need_energy = energy is None or energy[0] < required_energy

    log.info(
        f"Перед входом: HP={current_hp if current_hp is not None else '?'}%, "
        f"энергия={energy[0] if energy else '?'}/{energy[1] if energy else '?'}, "
        f"требуется EN={required_energy}."
    )

    if need_energy:
        log.info("Энергии недостаточно — использую /energy.")
        await asyncio.sleep(COMMAND_DELAY)
        await conv.send_message("/energy")
        energy_resp = await conv.get_response()
        energy_text = energy_resp.raw_text
        log.info(f"/energy -> {energy_text}")

        if TOO_MANY_COMMANDS_MARKER in energy_text:
            await asyncio.sleep(COMMAND_DELAY)
            await conv.send_message("/energy")
            energy_resp = await conv.get_response()
            energy_text = energy_resp.raw_text
            log.info(f"/energy -> {energy_text}")

        if ENERGY_EMPTY_MARKER in energy_text:
            log.info("Кристаллов для восстановления энергии нет — /energy больше не использую, жду естественного восстановления.")
        elif ENERGY_FULL_MARKER in energy_text:
            log.info("Энергия уже полная — /energy больше не использую.")

    if need_hp:
        log.info("HP недостаточно — использую /heal.")
        await asyncio.sleep(COMMAND_DELAY)
        await conv.send_message("/heal")
        heal_resp = await conv.get_response()
        heal_text = heal_resp.raw_text
        log.info(f"/heal -> {heal_text}")

        if HEAL_EMPTY_MARKER in heal_text:
            log.info("Лечебных предметов нет — /heal больше не использую, жду естественного восстановления HP.")
            await wait_for_natural_hp_recovery(conv)

    await wait_for_energy(conv, required_energy)


async def resolve_warning(conv, resp: Message, required_energy: int = 0) -> str | bool:
    """Обрабатывает предупреждение через /energy и /heal, не разрешая вход в истощении."""
    text = resp.raw_text
    need_energy, need_hp = classify_warning(text)
    if not (need_energy or need_hp):
        return False

    first_line = text.splitlines()[0] if text else ""
    log.info(f"Предупреждение: энергия={need_energy}, hp={need_hp} ({first_line})")

    energy_item_missing = False
    energy_already_full = False

    if need_energy:
        await asyncio.sleep(COMMAND_DELAY)
        await conv.send_message("/energy")
        energy_resp = await conv.get_response()
        energy_text = energy_resp.raw_text
        log.info(f"/energy -> {energy_text}")

        if TOO_MANY_COMMANDS_MARKER in energy_text:
            await asyncio.sleep(COMMAND_DELAY)
            await conv.send_message("/energy")
            energy_resp = await conv.get_response()
            energy_text = energy_resp.raw_text
            log.info(f"/energy -> {energy_text}")

        if ENERGY_EMPTY_MARKER in energy_text:
            energy_item_missing = True
            log.info("Кристаллов для восстановления энергии нет — больше не использую /energy.")
        elif ENERGY_FULL_MARKER in energy_text:
            energy_already_full = True
            log.info("Энергия уже полная — больше не использую /energy и не зацикливаю команду.")

    if need_hp:
        await asyncio.sleep(COMMAND_DELAY)
        await conv.send_message("/heal")
        heal_resp = await conv.get_response()
        heal_text = heal_resp.raw_text
        log.info(f"/heal -> {heal_text}")

        if HEAL_EMPTY_MARKER in heal_text:
            log.info("Лечебных предметов нет — /heal больше не использую, жду естественного восстановления HP.")
            await wait_for_natural_hp_recovery(conv)

    if need_energy:
        if required_energy > 0:
            if not energy_item_missing and not energy_already_full:
                await wait_for_energy(conv, required_energy)
            else:
                await asyncio.sleep(ENERGY_CHECK_INTERVAL)
        elif energy_item_missing or energy_already_full:
            await asyncio.sleep(ENERGY_CHECK_INTERVAL)

    return "retry"
