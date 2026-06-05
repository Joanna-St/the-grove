## What This Is
A personal idle creature sanctuary game in Pygame (Python). You play as a druid 
tending a magical grove on the edge of the Feywild (Faerûn / BG3 world). Creatures 
arrive, bond milestones unlock, resources accumulate passively.

Tone reference: Undertale — creatures have individual personalities and small stories.
Full design bible: `docs/grove_game_design.docx`

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
│   └── grove_game_design.docx
├── config.json
├── save.json          ← gitignored
├── main.py
├── game/
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
- [ ] Phase 1 — Foundation
- [ ] Phase 1.5 — Minimal Visual Layer
- [ ] Phase 2 — Heartstone (playable demo)
- [ ] Phase 3 — Full Progression
- [ ] Phase 4 — Events & Visitors
- [ ] Phase 5 — Art & Polish

Full phase descriptions in design doc.

## Current Phase
**Phase 1 — Foundation**
- [ ] Project structure + Pygame window
- [ ] Config file
- [ ] Save/load system
- [ ] Hybrid time system (real elapsed + in-game day/night cycle + dev speed mode)
- [ ] Resource tracking (rectangles and text only — no art yet)

Deliverable: game launches, time passes, resources tick, save and reload works.

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
- `main.py` — Pygame 1024×768 window; day-tinted background; resource HUD; time arc bar; keybind hints; save flash
- `assets/sprites/` and `assets/sounds/` directories created
- Deliverable confirmed: game launches, time passes, resources tick, save/reload works
- **Next:** Phase 1.5 — Minimal Visual Layer (placeholder sprites, Heartstone background, basic UI)