# PROJECT STATE

## 2026-09-03 — HP/energy dungeon-entry checkpoint

Implemented resource preparation before dungeon entry and protection against recovery-command spam.

### Current behavior
- If HP is low, the bot uses `/heal` before entering a dungeon.
- If energy is insufficient, the bot uses `/energy` before entering a dungeon.
- If both HP and energy are insufficient, both recovery commands are attempted.
- If `/energy` returns `Этот предмет нельзя использовать для восстановления энергии.`, the bot treats energy crystals as unavailable and stops retrying `/energy`; it waits for natural energy regeneration.
- If `/energy` returns `Энергия уже полная.`, the bot recognizes that response and does not repeatedly issue `/energy`.
- If `/heal` returns `Лечебный предмет не найден в инвентаре.`, the bot treats healing items as unavailable and stops retrying `/heal`; it waits for natural HP recovery.
- If energy is insufficient and no energy item is available, the bot does not repeatedly call `/energy` and does not enter the dungeon in exhaustion.
- If HP is sufficient but energy is not, the bot waits for energy and does not enter the dungeon exhausted.
- If both resources are insufficient and recovery items are unavailable, the bot waits for natural recovery instead of looping recovery commands.
- The old unconditional low-HP `/heal` call in the main cycle was removed so it cannot spam `/heal` before the centralized resource preparation.
- Warning handling no longer confirms `Войти в истощении`.

### Changed files
- `dungeon/recovery.py`
- `dungeon/cycle.py`

Latest commits:
- Resource recovery logic: `a3b525e753bdd0335c73ab50e80a8e4d76b27a0c`
- Dungeon entry preparation: `cb1310335ac591af562f7fd551e6d66c918aa07a`
- Recovery command anti-spam: `727c4939087484a5f576a70db03508dd0a37c206`
- Recovery wait-loop handling: `ce493658a3c39785be62dc5db1842ad7e417d6d0`
- Full-energy response handling: `47e349737e290589e4ed15649adda4c306edb2e3`
