## What This Is
A personal idle creature sanctuary game in Pygame (Python). You play as a druid 
tending a magical grove on the edge of the Feywild (Faerûn / BG3 world). Creatures 
arrive, bond milestones unlock, resources accumulate passively.

Tone reference: Undertale — creatures have individual personalities and small stories.
Full design bible: `docs/design.md` (also `docs/grove_game_design.docx`)

Repo: https://github.com/Joanna-St/the-grove (public, MIT license)

## Tech Stack
- Python + Pygame
- Save system: JSON on disk
- Config: external JSON/YAML (all tunable values here — never hardcoded)
- No other dependencies planned for core game

## Project Structure

the-grove/
├── CLAUDE.md
├── IDEAS.md
├── docs/
│   ├── design.md         ← design bible (canonical reference)
│   └── grove_game_design.docx
├── config.json
├── save.json             ← gitignored
├── main.py
├── game/
│   ├── renderer.py
│   ├── time_system.py
│   ├── resources.py
│   ├── creatures.py
│   ├── areas.py
│   ├── events.py
│   └── save_load.py
└── assets/
    ├── sprites/
    └── sounds/

## Development Rules
- Complete each phase fully before starting the next
- New ideas during build → IDEAS.md, not current phase
- All tunable values in config.json, never hardcoded
- Dev speed mode must always be functional
- Update the Session Log before closing each session

## Phases
- [x] Phase 0 — Design (complete)
- [x] Phase 1 — Foundation
- [x] Phase 1.5 — Minimal Visual Layer
- [ ] Phase 2 — Heartstone (playable demo)
- [ ] Phase 3 — Full Progression
- [ ] Phase 4 — Events & Visitors
- [ ] Phase 5 — Art & Polish

Full phase descriptions in design doc.

## Current Phase
**Phase 2 — The Heartstone (playable demo)**
- [ ] Stirge and blink dog arrive with full interaction and bond tracking
- [ ] Resource generation from creatures (rates from config)
- [ ] Silvanus statue tending (glamour system live)
- [ ] Player name entry at first launch

Deliverable: playable demo — you can tend the grove, feed the stirge, watch the blink dog cause chaos.

## Session Log
*Update before closing each session: what was completed, what's next, any decisions 
made that future sessions need to know about.*

### Session 1 — [03.06.2026]
- Project initialised
- CLAUDE.md created

### Session 2 — [03.06.2026]
**Phase 1 complete.**
- `config.json` — all tunable values (resource rates, area costs, day length, dev speed multiplier, event intervals, autosave interval)
- `game/time_system.py` — hybrid real/in-game time; offline progress calculated on load; dev speed toggle (D key); dawn/day/dusk/night periods
- `game/resources.py` — forage, heartwood, glamour tracking; passive generation scales with glamour health × grove size; rendered as bars + text
- `game/save_load.py` — JSON save/load; auto-saves every 60s and on clean exit; saves on demand (S key)
- `game/areas.py` — area unlock tracking; heartstone always active; size_multiplier for passive scaling
- `game/creatures.py` / `game/events.py` — stubs with persistence interface (Phase 2/4)
- `main.py` — Pygame window; day-tinted background; resource HUD; time arc bar; keybind hints; save flash
- `assets/sprites/` and `assets/sounds/` directories created
- Deliverable confirmed: game launches, time passes, resources tick, save/reload works
- **Next:** Phase 1.5 — Minimal Visual Layer

### Session 3 — [05.06.2026]
**Phase 1.5 complete.**
- `game/renderer.py` — coded placeholder scene: sky gradient (period-tinted), tree silhouettes, Heartstone clearing with moss spots, Silvanus statue (stone geometry + glamour glow), druid hooded figure, ambient firefly motes at dusk/night
- No image files — all geometry, designed to be swapped for real sprites in Phase 5
- `main.py` updated to call `draw_scene()` instead of flat fill; HUD floats over scene
- All four day periods (dawn/day/dusk/night) visually distinct
- `IDEAS.md` created — parked runtime fullscreen toggle and custom icon for Phase 5
- **Deviations from Phase 1.5 spec (design.md):** design called for pixel sprites (druid, stirge, blink dog) — deferred entirely; art approach (Claude AI / GPT) TBD for Phase 5. Interaction prompts skipped — no creatures to interact with until Phase 2, no point building dead UI. Coded scene goes beyond spec (trees, clearing, motes) but adds no complexity to later phases.
- **Window decision:** settled on 900×640. Fullscreen mode available via `"fullscreen": true` in config.json (uses NOFRAME + letterboxing, no resolution change). Runtime toggle attempted and abandoned — SDL2 window repositioning unreliable on Windows; parked in IDEAS.md.
- Deliverable confirmed: it looks vaguely like a grove
- **Next:** Phase 2 — The Heartstone (stirge and blink dog arrive, interaction, bond tracking, glamour system, player name entry)