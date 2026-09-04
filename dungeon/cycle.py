"""Основной цикл прохождения данжей."""

import asyncio

from config import (
    log,
    BOT_USERNAME,
    RESPONSE_TIMEOUT,
    REPORT_EXTRA_WAIT,
    STALE_DUNGEON_EXTRA_WAIT,
    DEFAULT_DUNGEON_ETA_MINUTES,
    HOT_SPRINGS_MSG_TIMEOUT,
    LOW_HP_THRESHOLD_PERCENT,
)
from parsers.profile import parse_power, parse_hp_percent
from parsers.dungeon import parse_dungeons, parse_resets_left, DUNGEON_ETA_RE
from parsers.messages import (
    ENTER_SUCCESS_MARKER,
    REPORT_MARKER,
    ALREADY_IN_DUNGEON_MARKER,
    INJURY_MARKER,
    INJURY_STATUS_MARKER,
    ALREADY_IN_SPRINGS_MARKER,
    HOT_SPRINGS_BUTTON,
    START_RECOVERY_BUTTON,
    RECOVERY_DONE_MARKER,
)
from dungeon.selector import choose_dungeon
from dungeon.recovery import resolve_warning, prepare_dungeon_resources
from telegram.buttons import click_button
from telegram.events import wait_update, click_and_wait_update


async def wait_for_report(conv, client, wait_seconds):
    """Ждёт отчёт (всегда новое сообщение, не edit) и возвращает его."""
    report_msg = await conv.get_response(timeout=wait_seconds)
    if REPORT_MARKER in report_msg.raw_text:
        result = "ПОБЕДА" if "ПОБЕДА" in report_msg.raw_text else "ПОРАЖЕНИЕ"
        log.info(f"Отчёт получен: {result}")
    else:
        log.warning(f"Получено сообщение вместо отчёта:\n{report_msg.raw_text}")
    return report_msg


async def visit_hot_springs(conv, client, profile_msg=None):
    """Идёт в горячие источники через /profile и ждёт полного восстановления (оба сеанса)."""
    if profile_msg is None:
        await conv.send_message("/profile")
        profile_msg = await conv.get_response()

    if ALREADY_IN_SPRINGS_MARKER in profile_msg.raw_text:
        log.info("Уже в источниках — просто дожидаюсь окончания сеансов, повторно не захожу.")
        springs_msg = profile_msg
    else:
        log.info("Обнаружена травма — иду в горячие источники.")
        clicked = await click_button(profile_msg, HOT_SPRINGS_BUTTON)
        if not clicked:
            log.error("Кнопка 'Горячие источники' не найдена в /profile, пропускаю лечение.")
            return

        springs_menu_msg = await wait_update(client, RESPONSE_TIMEOUT)
        clicked = await click_button(springs_menu_msg, START_RECOVERY_BUTTON)
        if not clicked:
            log.error("Кнопка 'Начать восстановление' не найдена, пропускаю лечение.")
            return

        springs_msg = await wait_update(client, RESPONSE_TIMEOUT)

    first_line = springs_msg.raw_text.splitlines()[0] if springs_msg.raw_text else ""
    log.info(f"В источниках: {first_line}")

    while RECOVERY_DONE_MARKER not in springs_msg.raw_text:
        springs_msg = await wait_update(client, HOT_SPRINGS_MSG_TIMEOUT)
        first_line = springs_msg.raw_text.splitlines()[0] if springs_msg.raw_text else ""
        log.info(f"Источники: {first_line}")

    log.info("Восстановление завершено, возвращаюсь к данжам.")


async def get_dungeon_radar(conv, wait_for_energy=True):
    """Получает свежий список данжей и обрабатывает предупреждения."""
    while True:
        await conv.send_message("/dungeon")
        radar_msg = await conv.get_response(timeout=RESPONSE_TIMEOUT)
        warning_result = await resolve_warning(
            conv,
            radar_msg,
            should_wait_for_energy=wait_for_energy,
        )
        if warning_result == "wait_energy":
            log.info("Энергии недостаточно и кристаллов нет — жду естественного восстановления 5 минут перед следующей проверкой.")
            await asyncio.sleep(5 * 60)
            continue
        if warning_result:
            log.info("Вместо списка данжей пришло предупреждение — пробуем /dungeon снова.")
            continue
        return radar_msg


async def get_favorite_defs(client):
    """Читает DEF данжей из последнего сообщения в 'Избранном' Telegram."""
    messages = await client.get_messages("me", limit=1)
    if not messages:
        return []

    text = (messages[0].raw_text or "").strip()
    if not text:
        return []

    parts = text.split()
    if not all(part.isdigit() for part in parts):
        log.warning("Последнее сообщение в 'Избранном' не содержит только DEF через пробел — избранные пропущены.")
        return []

    favorite_defs = [int(part) for part in parts]
    log.info(f"Избранные DEF: {favorite_defs}")
    return favorite_defs


async def run_cycle(client, wait_for_energy=True):
    async with client.conversation(BOT_USERNAME, timeout=RESPONSE_TIMEOUT) as conv:
        while True:
            await conv.send_message("/profile")
            profile_msg = await conv.get_response()
            power = parse_power(profile_msg.raw_text)
            log.info(f"Мощь охотника: {power}")

            if INJURY_STATUS_MARKER in profile_msg.raw_text:
                log.info("В профиле обнаружена травма — иду в источники.")
                await visit_hot_springs(conv, client, profile_msg)
                continue

            hp_percent = parse_hp_percent(profile_msg.raw_text)

            radar_msg = await get_dungeon_radar(conv, wait_for_energy)

            if ALREADY_IN_DUNGEON_MARKER in radar_msg.raw_text:
                log.info("Уже в данже (незавершённый прошлый забег) — жду отчёт вместо списка.")
                stale_report = await wait_for_report(conv, client, REPORT_EXTRA_WAIT + STALE_DUNGEON_EXTRA_WAIT)
                if INJURY_MARKER in stale_report.raw_text:
                    await visit_hot_springs(conv, client)
                continue

            entries = parse_dungeons(radar_msg.raw_text)
            resets_left = parse_resets_left(radar_msg.raw_text)
            favorite_defs = await get_favorite_defs(client)
            log.info(f"Данжи: {[(e['idx'], e['name'], e['def'], e['energy']) for e in entries]} | сбросов: {resets_left}")

            chosen = None
            while chosen is None:
                chosen, need_reset = choose_dungeon(entries, power, resets_left, favorite_defs)
                if chosen is not None:
                    break
                if not need_reset:
                    break
                log.info("Все данжи сильнее мощи, сбрасываем список...")
                clicked = await click_button(radar_msg, "Сбросить список")
                if not clicked:
                    log.error("Кнопка 'Сбросить список' не найдена, беру самого слабого.")
                    chosen = min(entries, key=lambda e: e["def"])
                    break
                radar_msg = await wait_update(client, RESPONSE_TIMEOUT)
                entries = parse_dungeons(radar_msg.raw_text)
                resets_left = max(0, resets_left - 1)

            log.info(f"Выбран данж #{chosen['idx']} {chosen['name']} (DEF {chosen['def']}, EN {chosen['energy']})")

            await prepare_dungeon_resources(conv, chosen["energy"], hp_percent, wait_for_energy)

            updated_radar = await click_and_wait_update(
                client,
                radar_msg,
                f"Войти #{chosen['idx']}",
                RESPONSE_TIMEOUT,
            )
            if updated_radar is None:
                log.error(f"Не удалось получить обновлённое сообщение после 'Войти #{chosen['idx']}'.")
                continue

            text = updated_radar.raw_text
            buttons = [button.text for row in updated_radar.buttons or [] for button in row]
            log.info(f"Обновлённое сообщение #{updated_radar.id}: {text.splitlines()[0] if text else '(пусто)'}")
            log.info(f"Кнопки после входа в данж: {buttons}")

            warning_result = await resolve_warning(conv, updated_radar, chosen["energy"], wait_for_energy)
            if warning_result == "started":
                enter_resp = await wait_update(client, RESPONSE_TIMEOUT, updated_radar.id)
                text = enter_resp.raw_text
            elif warning_result == "retry":
                radar_msg = await get_dungeon_radar(conv, wait_for_energy)
                clicked = await click_button(radar_msg, f"Войти #{chosen['idx']}")
                if not clicked:
                    log.error(f"Не нашёл свежую кнопку 'Войти #{chosen['idx']}' после обработки предупреждения.")
                    continue
                enter_resp = await wait_update(client, RESPONSE_TIMEOUT)
                text = enter_resp.raw_text

                warning_result = await resolve_warning(conv, enter_resp, chosen["energy"], wait_for_energy)
                if warning_result == "started":
                    enter_resp = await wait_update(client, RESPONSE_TIMEOUT)
                    text = enter_resp.raw_text
                elif warning_result == "retry":
                    continue

            if ENTER_SUCCESS_MARKER not in text:
                log.warning(f"Неожиданный ответ на вход, жду отчёт на всякий случай:\n{text}")

            eta_match = DUNGEON_ETA_RE.search(text)
            eta_minutes = int(eta_match.group(1)) if eta_match else DEFAULT_DUNGEON_ETA_MINUTES
            wait_seconds = eta_minutes * 60 + REPORT_EXTRA_WAIT
            log.info(f"Данж запущен, жду отчёт (~{eta_minutes} мин, таймаут {wait_seconds}с)...")

            report_msg = await wait_for_report(conv, client, wait_seconds)
            if INJURY_MARKER in report_msg.raw_text:
                await visit_hot_springs(conv, client)
