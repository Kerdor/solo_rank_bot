# PROJECT STATE

## 2026-09-04 — Per-account energy waiting mode

Added an independent energy-waiting setting for each Telegram account.

### Configuration
- `WAIT_FOR_ENERGY_1=true|false`
- `WAIT_FOR_ENERGY_2=true|false`
- `WAIT_FOR_ENERGY_3=true|false`
- `true` = wait for natural energy regeneration until the selected dungeon can be entered normally.
- `false` = do not wait for natural energy regeneration; when the game offers `Войти в истощении`, the bot uses that option.
- If the variable is omitted, the default is `true`, preserving the previous behavior.
- The existing single-account fallback also supports `WAIT_FOR_ENERGY`.

### Current behavior
- Each account carries its own `wait_for_energy` mode into its independent dungeon loop.
- Energy recovery and exhaustion behavior are therefore isolated per account.
- HP recovery behavior remains unchanged: low HP can still trigger `/heal` and, when healing items are unavailable, natural HP recovery is still awaited.
- When energy is insufficient, `/energy` is still attempted first. If no energy item is available and the account has `WAIT_FOR_ENERGY=false`, the bot clicks `Войти в истощении` instead of waiting.
- With `WAIT_FOR_ENERGY=true`, the existing natural energy wait behavior is preserved.
- Existing anti-spam handling for `/energy` and `/heal` remains in place.

### Changed files
- `config.py` — parses per-account `WAIT_FOR_ENERGY_N` settings.
- `main.py` — passes each account's setting into its own async dungeon loop.
- `dungeon/cycle.py` — propagates the account-specific mode through dungeon radar, resource preparation, and warning handling.
- `dungeon/recovery.py` — conditionally waits for energy or clicks `Войти в истощении` when waiting is disabled.
- `.env.example` — documents the new settings.
