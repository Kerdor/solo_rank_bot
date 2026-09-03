# PROJECT STATE

## 2026-09-03 — HP/energy dungeon-entry checkpoint

Implemented resource preparation before dungeon entry.

### Current behavior
- If HP is low, the bot uses `/heal` before entering a dungeon.
- If energy is insufficient, the bot uses `/energy`.
- If both HP and energy are insufficient, both recovery commands are attempted.
- After `/energy`, the bot checks actual energy from `/profile`.
- If energy is still below the selected dungeon requirement, the bot waits for natural regeneration instead of entering in exhaustion.
- If HP is sufficient but energy is not, the bot waits for energy and does not enter the dungeon exhausted.
- Warning handling no longer confirms `Войти в истощении`.

### Changed files
- `dungeon/recovery.py`
- `dungeon/cycle.py`

Latest commits:
- Resource recovery logic: `a3b525e753bdd0335c73ab50e80a8e4d76b27a0c`
- Dungeon entry preparation: `cb1310335ac591af562f7fd551e6d66c918aa07a`
