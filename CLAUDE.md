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
│   ├── dialogue.py
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
- [x] Phase 2 — Heartstone (playable demo)
- [x] Phase 3 — Full Progression
- [x] Phase 4 — Events & Visitors
- [ ] Phase 5 — Art & Polish
- [ ] Phase 6 — Post-Launch Additions

Full phase descriptions in design doc.

## Current Phase
**Phase 5 — Art & Polish**

Scope TBD at start of phase — see design doc for original spec (pixel sprites for druid/creatures, replacing coded placeholders) plus accumulated revisit items in IDEAS.md (Shield rename, resource storage caps, multi-box visual indicator, etc).

## Phase 6 — Post-Launch Additions (not yet scoped)
- Creature max-bond perks (design.md specs one per creature: Pseudodragon/Stirge early-warning, Flumph/Displacer Beast event dampening, Pixie wildcard intervention, Blink Dog yield boost, Moss Wisp grove-health-gated boost). Deliberately deferred post-launch — half of these assume a negative/threat tagging axis for grove + visitor events that doesn't exist yet (4c/4d shipped as pure flavour, no good/bad categorisation). Revisit scoping then.

## Session Log
*Update before closing each session: what was completed, what's next, any decisions 
made that future sessions need to know about.*

### Session 1 — [03.06.2026]
- Project initialised
- CLAUDE.md created

### Session 2 — [03.06.2026]
**Phase 1 complete.**
- `config.json` — all tunable values (resource rates, area costs, day length, dev speed multiplier, event intervals, autosave interval)
- `game/time_system.py` — in-game time advances only while game is open (offline progress removed in Session 5); dev speed toggle (D key); dawn/day/dusk/night periods
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

### Session 4 — [06.06.2026]
**Phase 2 complete.**
- `game/dialogue.py` — dialogue pools for stirge and blink dog (5 lines per bond level 0–3), milestone texts, forage and tend-statue flavour lines
- `game/creatures.py` — full Creature class: arrival timing, passive resource contribution by bond level, click interaction, bond XP + level-up, dialogue TTL, interact cooldown, bond flash TTL
- `game/save_load.py` — player name added to save format
- `game/renderer.py` — stirge placeholder (dark oval, wings, proboscis, eye), blink dog placeholder (canine silhouette with shimmer flicker and glow aura), dialogue bubble renderer, action panel renderer; clickable rect helpers for all three interactables
- `main.py` — name entry screen on first launch; click detection (stirge, blink dog, statue); F/T active actions with cooldown bars; bond XP flash (gold highlight on interact); player name top-right; bond status display `[*--]` style
- `config.json` — arrival timings, bond XP config, action cooldown/yield values
- `IDEAS.md` — added interaction-triggered resource drops and blink dog random object drops as future considerations
- **Known gap:** glamour base drain agreed (0.002/s) but not implemented — carry into Phase 3 start
- **Decisions:** creature contributions are passive/continuous (not interaction-triggered); bond XP visual = brief gold flash on bond line; no floating resource numbers for now (parked in Ideas); resource panel width fixed to contain numbers
- Deliverable confirmed: name entry works, stirge and blink dog arrive on schedule, interactions build bond, stat tending works, save/load preserves all state
- **Next:** Phase 3 — Full Progression (area unlock mechanic first, then remaining six creatures)

### Session 5 — [06.06.2026]
**Phase 3 pre-work: Protection redesign (unplanned but necessary).**
- Design doc updated (via Claude AI consultation) — glamour drain scrapped in favour of a new separate **Protection** stat
- `game/resources.py` — Protection added as fourth resource (0–100%); passive generation now scales with protection level × grove size; floor at 10% so generation never fully stops; protection decays in real time (not game time), scaling with number of unlocked areas + Feywild Boundary bonus; `add()` caps protection at max
- `config.json` — `glamour_decay` removed; `protection` block added (starting 80, max 100, decay 0.02/s, feywild extra 0.03/s, min generation multiplier 0.1); `tend_statue` reworked: now costs 5 glamour and restores 30 protection (previously yielded glamour)
- `game/areas.py` — `glamour_threshold()` removed; `has_feywild_boundary()` added
- `game/time_system.py` — offline progress removed; grove waits when closed (resources and time do not advance while game is shut)
- `main.py` — tend-statue action updated (costs glamour, restores protection; shows warning if glamour insufficient); HUD y-positions shifted down to accommodate fourth resource bar; `tick()` call updated to pass `dt_real`
- `IDEAS.md` — added: shield decay tuning, "Shield" display name revisit, resource storage caps
- **Decisions:** protection decays in real time (not game time) so dev speed mode doesn't drain it faster; glamour is now purely a resource that accumulates and is spent; "Shield" is the current HUD label for protection, flagged for renaming in Phase 5
- **Next:** area unlock mechanic (UI + spending resources to restore areas)

### Session 6 — [06.06.2026]
**Phase 3 step 1: Feeding mechanic + creature action menu.**
- `game/renderer.py` — `draw_action_menu()` and `action_menu_item_rects()`: reusable popup menu anchored above a creature with hover highlight, greyed-out unavailable options, cost detail right-aligned, tail pointing toward creature; foundation for Phase 4 event dialogue choices
- `main.py` — `_creature_menu_options()` helper; `action_menu` state dict; clicking a creature opens menu (Interact / Feed) instead of acting directly; MOUSEMOTION updates hover; ESC closes menu before quitting; menu fire-or-dismiss on click
- `game/dialogue.py` — `STIRGE_FEED` and `BLINK_DOG_FEED` pools (5 personality-specific feeding lines each, flat pools not bond-gated)
- `game/creatures.py` — `can_feed` property, `feed()` method, `feed_indicator` property (`[f:**]` style); daily reset keyed to `day_number`; per-feed cooldown (`_feed_cd_remaining`, real seconds, bleeds into next day); `_resolve_bond()` extracted as shared helper for interact and feed; persistence updated; `Creatures.update()` signature adds `day_number`
- `config.json` — `feeding` block per creature: `feeds_per_day`, `forage_cost`, `bond_xp_per_feed`, `cooldown_real_seconds`
- **Decisions:** feeding is a separate mechanic from interact (daily cap + per-feed cooldown, not interact cooldown); interact cooldown is purely real-time and does not reset at day boundaries; level-up milestone text takes priority over feed/interact line when both fire simultaneously; feed option shows cost in menu detail; feed greyed when on cooldown OR daily limit reached OR insufficient forage
- **Next:** area unlock UI (panel showing locked areas, costs, spend resources to restore)

### Session 7 — [06.06.2026]
**Phase 3 complete.**
- `game/dialogue.py` — dialogue pools for all 6 new creatures (OWLBEAR, PSEUDODRAGON, FLUMPH, MOSS_WISP, PIXIE, DISPLACER_BEAST): 5 lines per bond level 0–3, 5 feed lines each, MILESTONES entries for all 8 creatures; Joanna edited several lines for tone
- `game/renderer.py` — coded placeholder visuals for all 6 new creatures (owlbear, pseudodragon, flumph, moss_wisp, pixie, displacer_beast): each has `*_pos()`, `*_rect()`, `draw_*()` functions; flumph/moss_wisp/pixie/displacer_beast are time-of-day animated; draw_scene updated to draw all 8 creatures via loop
- `main.py` — data-driven `_CREATURE_REGISTRY` list replaces explicit per-creature click handling; all 8 creatures wired for click detection, action menu, and dialogue bubble rendering; all 8 creature pos/rect functions imported
- `config.json` — creature configs for all 6 new creatures already in place (from Session 6 planning)
- **Decisions:** creature perks deferred — most are event-system dependent (Phase 4); blink dog scouting was inferred from flavour text, not specced; moss wisp gen boost also deferred to Phase 4; floating dialogue bubbles remain for now, to be replaced by bottom text box as first step of Phase 4
- **Next:** Phase 4 — bottom text box UI first (replaces bubbles + sidebar flash), then event system

### Session 8 — [06.06.2026]
**Phase 3 cleanup: bottom text box UI.**
- `game/renderer.py` — `draw_text_box()`: fixed bottom panel (100px, full-width), two modes — options (creature name + Interact/Feed list with hover highlight) and text (speaker label + wrapped dialogue, auto-expires or dismiss); `text_box_item_rects()`: pure rect helper for hover/click detection; `draw_center_flash()`: small centred semi-transparent panel for transient messages; `draw_action_panel()` gains `bottom` parameter to anchor above text box
- `main.py` — `text_box` state dict replaces `action_menu` + `flash_text`/`flash_ttl`; `_grove_text()` and `_creature_text()` helpers reduce boilerplate; creature clicks open options mode in text box; interact/feed switch box to text mode; grove messages (forage, tend, area restored) go to text box with "The Grove" label; errors and "Saved." go to `draw_center_flash`; `render_keybinds()` gains `right_align` flag; keybinds moved to top-right below player name; `draw_action_menu` / `action_menu_item_rects` / `draw_dialogue` removed from call sites (kept in renderer.py for Phase 4 reuse)
- **Decisions:** text box dismisses on ESC, click outside (options), any click (text), or TTL expiry; floating dialogue bubbles fully removed; `draw_action_menu` retained in renderer.py as Phase 4 foundation for event dialogue choices; creature perks and event system deferred to Phase 4
- **Next:** Phase 4 — creature event system, grove events, visitor cameo arcs

### Session 9 — [17.06.2026]
**Phase 4 complete (4a–4d signed off; max-bond perks deferred, see Phase 6).**

**4a — Event infrastructure.**
- `game/events.py` — new `Events` class: creature-event stagger (`can_fire_creature_event()` / `mark_creature_event_fired()`, global cooldown so two creatures never pop a `!` at the same moment), `grove_pending_event` / `visitor_pending_event` scaffolding, persistence (`to_dict`/`from_dict`)
- `game/renderer.py` — `draw_notification()`: small gold exclamation-mark glyph drawn above a creature/statue/druid when it has something pending; unified marker reused by creature events, grove events, and visitor arcs
- Signed off before moving to content (4b)

**4b — Creature events.**
- `game/dialogue.py` — `FIXED_EVENTS` (one-time per bond level, 8 creatures × levels 1–3) and `REPEATABLE_EVENTS` (flat pool per creature) pools added
- `game/creatures.py` — `Creature._update_events()`: three-step scheduler — (1) scan bond levels for an un-fired fixed event and schedule it with a random delay (`fixed_event_delay_range_seconds`), (2) deliver it once the delay elapses and the global stagger is clear, (3) otherwise fall back to delivering a repeatable event on its own cooldown (`creature_event_interval_seconds`); reward is bond XP only for fixed events, all 3 resources + bond XP for repeatable; `has_event` / `pending_event` exposed for the action-menu "Event" option
- `config.json` — `events` block added: `creature_event_interval_seconds`, `creature_event_stagger_seconds`, `fixed_event_delay_range_seconds`, `fixed_event_bond_xp`, `repeatable_event_bond_xp`, `repeatable_event_resource_yield`
- **Known gap flagged, not fixed:** `dlg.pick(dlg.FORAGE)` can surface a blink-dog-themed line before the blink dog has arrived — parked in IDEAS.md
- Verified via dev-speed playtest: fixed events deliver once per bond level, repeatable events keep cycling, stagger prevents simultaneous `!`s

**4c — Grove events.**
- `game/dialogue.py` — `GROVE_EVENTS` dict: 3 flavour lines per area, gated by area unlock
- `game/events.py` — `_pick_grove_event()`: fully random selection (`random.choice`) across all unlocked areas' lines, no no-repeat tracking — deliberate choice after discussion (no other event pool in the game uses no-repeat tracking, so this stays consistent); own cooldown (`grove_event_interval_seconds`)
- **Process note:** mid-QA, an unconfirmed code change was made (excluding-already-shown lines) without asking first — caught by the user, reverted in favour of the fully-random approach, and the "no changes without explicit confirmation" rule was formalised in memory (`feedback_no_unconfirmed_changes.md`)

**4d — Visitor cameo arcs.**
- `game/dialogue.py` — `VISITOR_ARCS`: 6 visitors (Kid, Girl, Druid, Healer, Soldier, Smith), each with a trigger condition, an ordered list of beats (`unlock_periods`, `min_gap_game_seconds`, one or more dialogue `boxes`), and a resource reward on the final beat
- `game/events.py` — visitor state machine: `_check_trigger()` per visitor key (bond-level gates, area-unlock gates, day-number gate for the Druid), `_try_activate_visitor()`, `_check_beat_timing()`, `advance_visitor()`; beat timing tracked via `beat_idx` + `beat_consumed_game_seconds` (reworked from an earlier box-level design — see below); `visitor_display_name()` added for the text-box speaker label
- `main.py` — druid-figure click opens/advances the active visitor's beat; multi-box beats render as a sequence
- **UX fixes made after initial QA (same session):** TTL removed from all text boxes everywhere (was auto-closing before longer visitor text could be read); multi-box click-to-advance (click anywhere advances a non-last box, dismisses on the last; ESC suppressed on non-last boxes as a "there's more" hint — flagged in IDEAS.md as needing a clearer visual cue eventually); visitor text boxes now show the visitor's name as speaker
- **Bug found & fixed:** beats originally gated on `min_day_offset` relative to a fixed `arrival_day`. Delaying a click let later beats' day conditions already be satisfied, so they chained instantly on dismiss (seen with the Druid and Healer arcs, both `unlock_periods: None`). Fixed by dropping day-offset entirely in favour of `min_gap_game_seconds` measured from each beat's own consumption time; Druid/Healer beats 2–3 given explicit 600-second (1 game day) gaps; trimmed the dialogue text that named specific day counts (Druid "two days"/"third morning", Healer "a few days"/"fourth morning")
- **Known remaining gap (accepted, not fixing):** period-gated beats (Girl, Soldier — dusk→night→dawn) can still chain instantly if the player delays a click until the next beat's period has already arrived (e.g. delaying the "night" beat until dawn lets the "dawn" beat fire immediately). A `require_period_change` edge-detection fix was proposed and explicitly declined — left as-is.

**Phase wrap-up.**
- **Decision:** creature max-bond perks (design.md spec) deferred to a new Phase 6 (post-launch). Half the perks assume a negative/threatening-event axis that doesn't exist in the current event content — re-scope when revisited.
- `config.json` QA test values reverted: `grove_event_interval_seconds` 20 → 600, `visitor_druid_min_day` 2 → 10
- **Next:** Phase 5 — Art & Polish (scope not yet defined this session)