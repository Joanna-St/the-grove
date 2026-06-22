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

Sprites and background wired into renderer.py, locked-area desaturation
implemented (Session 12). Next step: UI polish items from IDEAS.md (Shield
rename, resource storage caps, multi-box visual indicator, fullscreen toggle,
custom icon, text cross-reference pass, blink dog forage pool bug).

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

### Session 10 — [21.06.2026]
**Phase 5 — Art production complete.**

All final art assets generated via AI (DALL-E via Bing Image Creator / ChatGPT).
Iterative prompt refinement approach — multiple passes per subject with reference
images used for owlbear and displacer beast to anchor body shape.

**Assets finalised:**
- `background.png` — full grove scene, pixel art / Stardew Valley style, five zones
  readable (heartstone clearing with Silvanus statue baked in, thicket lower-left,
  oldwood upper-left, canopy upper-centre, Feywild boundary right with organic
  shimmer veil). Statue integrated into background — not a separate sprite.
- `stirge.png` — mosquito-bat hybrid, pathetic-endearing, hunched pose. Needs bg removal.
- `blink_dog.png` — scrappy canine, mid-movement chaos energy, transparent bg.
- `owlbear.png` — large and heavy, owl face, sheepish wide eyes, transparent bg.
  Required reference image (D&D official art) to anchor body shape.
- `pseudodragon.png` — slender eastern-dragon style (Mushu reference), upright perch,
  quietly disdainful. Needs bg removal.
- `flumph.png` — jellyfish interpretation (departed from D&D anatomy deliberately —
  D&D flumph unreadable at sprite scale); pale translucent dome, drowsy courteous
  expression, transparent bg.
- `moss_wisp.png` — glowing green-white orb, mossy trailing edges, minimal face
  (prompt said no face; AI disagreed). Transparent bg.
- `pixie.png` — small fae figure, mid-movement impish energy, hollow dark eyes,
  transparent bg.
- `displacer_beast.png` — blue panther with shoulder tentacles, proud upright posture,
  reads slightly domestic-cat but personality correct. Required reference image.
  Needs bg removal.
- `druid.png` — hooded figure, face partially shadowed, natural leaf/moss robe detailing,
  belted, calm and still. Needs bg removal.

**Decisions:**
- Statue baked into background rather than separate sprite — eliminates style mismatch risk
- Flumph jellyfish interpretation accepted over D&D anatomy — better readable at sprite scale
- All sprites consistent pixel art style; background Stardew Valley / RPG Maker flat style

### Session 11 — [22.06.2026]
**Phase 5 — Sprite processing complete.**

All sprites processed from JFIF source files into final game-ready PNGs using
Python (Pillow + scipy + sklearn). Background also replaced with a higher-quality
version (more detailed, better zone separation).

**Background:**
- New background chosen over Session 10 version — richer detail, cleaner zone
  separation (gnarled oldwood tree clearly on left, veil on right, stone circle
  centre with cobblestone path).

**Processing pipeline applied to all 9 creature sprites:**
1. **Background removal** — two-colour flood fill from image edges, detecting the
   checkerboard transparency pattern baked into JFIF exports; flood fill seeded
   from border pixels, expanding through bg-coloured pixels only.
2. **Colour harmonisation** — zone-aware correction per sprite:
   - Brightness normalised toward background range (target ~85, bg mean ~60)
   - Green ambient tint applied to simulate forest canopy lighting
   - Saturation boosted to match background's vivid pixel-art palette (~38–45)
   - Contrast lifted (×1.18) to read against detailed background
   - Glow sprites (moss_wisp, flumph, pixie) kept brighter (target ~120) with
     channel-specific glow: green for wisp, pink-blue for flumph, golden for pixie
   - Zone tints: veil sprites get blue-purple cast; oldwood sprites get cool teal
3. **Pixelation pass** — rendered sprites (blink_dog, owlbear, flumph) had smooth
   AI gradients; 5px-block nearest-neighbour downscale/upscale reduces apparent
   resolution to match background's pixel art density

**Per-sprite notes:**
- `pseudodragon.png` — had enclosed interior background pocket between neck and wing
  (not reachable by edge flood fill); required secondary pass expanding transparent
  region through bg-coloured pixels adjacent to existing transparent area
- `flumph.png` — width squished to 70% (height preserved) to give a slimmer,
  more drifting silhouette; hue required more aggressive green reduction than
  other sprites (final: G ×0.68, R ×1.05, B ×1.04)
- `blink_dog.png` — similarly required heavy green reduction (G ×0.72, R ×1.06)
  to restore warm amber; brightness lifted ×1.25 late in process
- `owlbear.png` — brightness dialled back ×0.82 at end; was competing with brighter
  clearing creatures
- `displacer_beast.png` — white fringe at base required targeted pass removing
  high-brightness low-saturation pixels after main flood fill

**Composite mockup decisions (mockup only — not game layout):**
- Owlbear: largest (230px), bottom-left path
- Displacer beast: near-equal (285px), by gnarled left tree, mid-height
- Druid: 160px, centre foreground
- Flumph: 130px (squished), in the veil (right)
- Blink dog: 120px, left of statue
- Moss wisp: 90px, above left tree
- Pseudodragon: 110px, in right treeline canopy
- Pixie: 70px, deep in veil, upper right
- Stirge: 108px, right of statue at ground level

**Next:** Wire sprites into `renderer.py` replacing coded placeholders. Then UI
polish from IDEAS.md: Shield rename, resource storage caps, multi-box visual
indicator, fullscreen toggle, custom icon, text cross-reference pass, blink dog
forage pool bug.

### Session 12 — [22.06.2026]
**Phase 5 — Sprites wired into renderer.py; locked-area desaturation implemented.**

- `game/renderer.py` — rewritten: `draw_background`/`draw_trees`/`draw_clearing`/
  `draw_statue`/`draw_druid` and all 8 creature `draw_*` functions no longer draw
  procedural geometry; they blit real sprites instead. Generic sprite pipeline:
  `_load_sprite_raw()` loads + crops each PNG to its non-transparent bounding box
  (so transparent canvas padding, e.g. stirge's 1792×1024 file, doesn't skew
  sizing/centring); `_get_sprite_scaled()` scales to a target width preserving
  aspect, cached by `(name, target_w)`; `_blit_sprite()` centres at a layout
  position with optional offset/alpha for animation. `_SPRITE_LAYOUT` holds
  per-creature `(centre_x_frac, centre_y_frac, width_frac)` — values derived by
  diffing the Session 11 `mockup_composite.png` against `background.png` (connected-
  component analysis to recover each creature's placed centre + the session log's
  recorded composite sizes), not eyeballed
- Per-creature animation preserved from the placeholder era: blink dog shimmer-jitter,
  flumph bob, moss wisp drift, pixie flutter; displacer beast gained a new
  translucent ghost-offset double-blit (displacement illusion) since the placeholder's
  version was geometry-only
- `draw_statue`/`statue_rect` — statue art is baked into the background image now
  (not drawn), so `draw_statue` only draws the ambient glow; `statue_rect` repositioned/
  resized (measured directly off the background pixels) to match the new taller
  antlered statue for click detection
- Background scaling: background.png (1536×1024) doesn't match the 900×640 window
  aspect ratio (1.5 vs 1.40625) — scaled uniformly to cover (factor 0.625) and
  centre-cropped 30px off each side, rather than stretched, to avoid distorting the
  art
- Added `draw_period_tint()` — translucent dawn/dusk/night colour overlay over the
  whole scene, replacing the old approach of drawing a period-coloured sky directly
  (no longer possible now the sky is baked into the background art)
- **Locked-area desaturation (scoped mid-session, not originally planned for this
  session):** `docs/phase5_art_spec.csv` recorded the original art intent — 4 sub-
  zones baked into the background meant to desaturate until their area unlocks —
  but this was never implemented in any prior session, and no zone masks exist in
  the art. Asked the user whether to scope it now or defer; user chose now.
  `_ZONE_RECTS` defines rough rectangles (fractions of the background image) for
  oldwood/thicket/canopy/feywild_boundary, positioned to match where each area's
  creatures already sit (e.g. oldwood = upper-left, around displacer beast + moss
  wisp); heartstone has no rect and is never desaturated. `_background_with_locked_zones()`
  greyscales the background and composites it back over the colour version only
  within each locked zone's mask, feathered via a cheap downscale/upscale blur
  (pure pygame, no numpy) so the zone edges aren't hard rectangles; cached per
  `(screen size, frozenset of locked zone names)` since it only needs to change
  when an area unlocks. `draw_background()` / `draw_scene()` gained an `areas=None`
  param to drive this; `main.py` passes `areas` through at both `draw_scene()` call
  sites (main loop + name-entry screen, the latter via a new `areas` param on
  `run_name_entry()`)
- Verified via direct pixel sampling (not just visual inspection): rendered scenes
  with various lock states and read back pixel colour at zone centres to confirm
  greyscale vs colour matched lock state exactly, including independent partial-
  unlock combinations
- **Decision:** zone boundaries are rough rectangles, not hand-painted masks —
  acceptable per user given no per-zone art masks exist; revisit with real masks
  only if the rectangle edges read as visually wrong in actual play
- `docs/phase5_art_spec.csv` — all rows updated from "Not started" to reflect
  wired-in status
- **Next:** UI polish from IDEAS.md — Shield rename, resource storage caps,
  multi-box visual indicator, fullscreen toggle, custom icon, text cross-reference
  pass, blink dog forage pool bug.

### Session 13 — [22.06.2026]
**Phase 5 — HUD layout pass, working issue-by-issue against the real art (in progress).**

Now that the real background/sprites are in, the old HUD layout (designed
around tiny placeholder shapes) collides with the much bigger real sprites.
User listed 6 concrete issues to work through one at a time: discuss → agree →
implement → test → confirm → log → next. First two done this session:

**Issue 1 — resource panel covered moss wisp.**
- `game/resources.py` — `ResourceTracker.render()` rebuilt slimmer: bars
  80×15px (was 220×22), smaller font (caller now passes `font_sm`), panel
  208×100px (was 375×138). Geometry exposed as class constants
  (`PANEL_W`/`PANEL_H`/etc.) so `main.py` can position it without duplicating
  the math.
- `main.py` — resource panel moved from top-left to the bottom-right corner,
  sharing a row with the message box; bottom edge aligned with the message
  box's bottom edge, height now matches it exactly (100px) at the user's
  request (`PANEL_BAR_H`=15, `PANEL_PAD`=8 tune to exactly 100).
- `game/renderer.py` — `draw_text_box`/`text_box_item_rects` gained a
  `right_inset` param so the message box narrows to leave room for the
  resource panel without moving its left edge; `draw_action_panel`'s margin
  changed 12→20 to align with the rest of the bottom-right column. Action
  panel re-anchored above the resource panel (16px gap, nudged up from an
  initial 8px at the user's request, since it's getting redesigned anyway).
- Time HUD and bond list left untouched at top-left per user request — to be
  addressed in a later iteration, not this pass.

**Issue 2 — bond list covered displacer beast and owlbear.**
- Replaced the 8-line sidebar bond-status list entirely with a small 3-segment
  bar drawn directly under each *present* creature's sprite (`draw_bond_bar()`
  in `game/renderer.py`) — scales with however many creatures have arrived
  instead of reserving a fixed block, and reuses the existing
  `bond_flash_ttl` for a brighten-on-levelup flash instead of the old text
  colour-flash.
- Feed-count tracking (`[f:**]`) dropped from the HUD entirely rather than
  carried into the new bar — `Creature.feed_indicator` (game/creatures.py)
  is now unused in-game; parked in IDEAS.md as a future info/help overlay
  item instead (controls + per-creature feed limits), since checking it live
  was never actually necessary (the action menu already greys out Feed when
  unavailable).
- `_SPRITE_LAYOUT` position nudges to make room for bars without collisions:
  owlbear `y_frac` 0.702→0.670 (was 3px from the message box, needed ~12px
  clearance for the bar), displacer_beast 0.382→0.350 (consistency nudge,
  same delta as owlbear). Verified by pixel-sampling the rendered output
  (not just eyeballing) that every creature's bar clears the message box and
  doesn't overlap a neighbouring sprite.
- Follow-up tuning after user checked live: bar segments changed from 9×7 to
  13×5 (wider, slimmer); per-creature vertical-offset override added
  (`_BOND_BAR_GAP_OVERRIDE`) since blink_dog and flumph's bounding boxes have
  a lot of transparent "air" below their visual mass (flumph's tentacle tips
  taper almost to nothing, dragging its bbox bottom well below its body) —
  pulled flumph's bar in by 16px, blink_dog's by 4px, rather than a flat gap
  for every creature. Also nudged flumph's own position left (`x_frac`
  0.897→0.870) — it was overlapping the pixie by 7px; now 17px clear.
- `IDEAS.md` — added "Info / help overlay" entry under a new UI/Info section.

**Decision:** working strictly one issue at a time through this list, each
with discuss→agree→implement→test→confirm→log before moving on (explicit
user instruction — see memory `feedback_workflow_discuss_first`).

**Issue 3 — player name + keybinds cheat sheet felt out of place.**
- `main.py` — both removed from the live HUD entirely rather than restyled.
  Keybinds cheat sheet isn't coming back as a permanent HUD element — it
  folds into the future info/help overlay (already parked in IDEAS.md).
  Player name returns later, repositioned near the bottom action area once
  that's redesigned (issue 4). `render_player_name()`/`render_keybinds()`
  left defined in main.py (unused for now) rather than deleted, since both
  are slated for near-term reuse.
- Title ("The Grove") untouched — wasn't part of this issue.

**Issue 4 — Forage/Tend Statue buttons felt out of place; folded in the
orphaned time HUD too.**
- Turned out not to need a menu system at all — the statue's existing click
  pattern (event-if-pending, else action-if-ready, no menu) was simply
  extended to the druid rather than building out a generalised options-menu
  for non-creature entities (the originally-discussed "menu with
  forage/tend/event" approach was reconsidered as overkill once we talked
  through it).
  - `main.py` — druid click handler now mirrors the statue's: visitor event
    if pending, else triggers Forage if `forage_cd <= 0` (same resource
    yield logic as the old `[F]` keypress). Statue click handler unchanged.
  - F/T keybinds kept functional in code (not removed) but no longer
    advertised anywhere live — they're "bonus" shortcuts now, to be
    mentioned in the future help overlay instead.
  - Floating action panel removed entirely: `draw_action_panel()` deleted
    from `game/renderer.py` (no planned reuse, unlike `render_player_name`/
    `render_keybinds` which stay defined-but-unused) and its call site/state
    removed from `main.py`.
- Time HUD rebuilt and relocated: same width as the resource panel (208px),
  stacked directly above it in the bottom-right column (where the action
  panel used to sit). Initially given a backing panel matching the resource
  panel's style, then user asked to drop the box entirely ("didn't have one
  originally, will look fine") — bar widened to fill the full width now that
  there's no box padding to inset within.
- Dev-speed badge moved top-right (was top-left at a fixed offset that
  ended up sitting on top of the displacer beast after the issue-2 sprite
  nudges). Acknowledged as a stopgap — `IDEAS.md` notes the help-menu
  indicator should take over that spot once dev mode is retired pre-release.
- User flagged that some kind of "ready" indicator for Forage/Tend is needed
  soon (no visual cue currently exists now that the cooldown bars on the old
  floating buttons are gone) — explicitly deferred to issue 6 (notification
  marker redesign) rather than scoped here.
- Player name placement still unresolved — no "bottom action area" concept
  exists anymore now that Forage/Tend are click-only, so issue 3's original
  plan ("readd near the bottom action area") no longer cleanly applies.
  Open thread, not yet picked back up.

**Issue 5 — druid sat awkwardly in front of the statue.**
- Swapped druid and blink_dog's positions in `_SPRITE_LAYOUT`
  (game/renderer.py) — druid moved to blink_dog's old spot (left-centre),
  blink_dog took druid's old spot, then nudged left to clear the statue
  (minor ~8px edge overlap accepted rather than chased further). Druid also
  shrunk by 1/3 width (`0.111`→`0.074`) — user hadn't realised it was as
  large as the displacer beast/owlbear.
- Iterated position from there via a sequence of relative nudges given as
  plain English ("20% of its height up", "2x its height down", "half its
  width left", etc.) rather than fractions — each translated to a pixel
  delta from the creature's actual rendered size (via `_load_sprite_raw()`
  + aspect ratio) and applied as an edit to `_SPRITE_LAYOUT`, then rendered
  and checked before the next round. One miscommunication mid-way: an
  instruction to nudge from "the original positions" was first read as
  pre-swap originals, actually meant the post-swap positions — caught and
  corrected once flagged.
  - Final: `"druid": (0.313, 0.547, 0.074)`,
    `"blink_dog": (0.369, 0.727, 0.083)`.
- Also caught mid-pass: an early round of this iteration was tested only via
  a throwaway script (editing `r._SPRITE_LAYOUT` at runtime in a one-off
  Python invocation) without writing the change to `game/renderer.py` —
  user saw no change live and caught it. Lesson: when iterating on tunable
  values like this, write to the source file immediately, don't render-test
  in memory first and forget the actual edit.
- **Bonus fix while in the area:** the moss_wisp/displacer_beast overlap
  flagged during issue 2 (got worse from that issue's displacer_beast nudge,
  pre-existing before that to a smaller degree) — nudged moss_wisp
  `(0.198,0.210)`→`(0.209,0.182)` (10px right, 1/3 its height up per user's
  instruction). Reduced the overlap from 35×36px to 25×18px, not fully
  clear, but user confirmed it reads fine visually as-is (wisp floats
  above/behind the beast's head, no jarring clash) — not chasing it further.

Remaining: (6) "!" notification markers were placeholders and need a real
treatment (now also expected to cover Forage/Tend readiness — flagged by
user during issue 4 as needed "soon").

**Issue 6 — "!" notification markers replaced with a pulsing silhouette halo.**
- User wanted a halo that traces each sprite's actual outline (not a generic
  blob), one flat colour for simplicity, pulsing, applied everywhere the old
  `draw_notification` was (creatures: interact/event-ready; statue: grove
  event pending OR tend-ready+affordable; druid: visitor event pending OR
  forage-ready).
- **Statue cutout extraction** — the statue has no separate sprite (baked
  into background.png), so there was no alpha mask to build a silhouette
  from. Attempted extracting one anyway via colour-threshold segmentation
  (saturation-based, since the painted art's ambient green tint meant hue
  didn't separate stone from grass) + morphological close (PIL MaxFilter/
  MinFilter) + border flood-fill hole-fill + light feather. Took several
  iterations (raw threshold was a noisy outline, not a filled silhouette;
  aggressive erode+largest-component cleanup overcorrected and ate the
  antlers/staff) before landing on a usable result — saved as
  `assets/sprites/statue.png`. Not pixel-perfect (rough edges, slight green
  tinge) but good enough since it only drives a blurred glow shape, never
  displayed directly. User: "Almost for the statue — will try working with
  AI as well" — open follow-up, not blocking.
- `game/renderer.py`:
  - `_SPRITE_LAYOUT["statue"]` added — position/size derived by mapping the
    cutout's extraction-crop bbox through the same scale/crop transform
    `_scaled_background()` uses, so the halo aligns with the statue's actual
    position in the rendered background. Used only for halo placement;
    `draw_statue()` still never blits this cutout image itself.
  - `_make_silhouette()` / `_get_halo()` — colour the sprite's alpha mask
    flat, scale up (`_HALO_SCALE`=1.18), blur via downscale/upscale
    (`_HALO_BLUR_DIV`), pulse via `halo_pulse()` (reuses the existing
    time_of_day-as-fast-oscillator pattern already used for blink_dog/
    flumph/etc. animations).
  - `draw_scene()` restructured: halo now drawn *before* each entity's sprite
    blit (statue/druid/creatures) so it appears behind/around the art;
    gained `statue_ready`/`druid_ready` params so `main.py` can pass the new
    action-readiness state through (cooldown + affordability for tend,
    cooldown only for forage).
  - `draw_notification()` deleted entirely, no remaining references.
- **Two rounds of visual fixes after user screenshots:**
  1. Statue's halo covered its *entire* body, not just an outline — because
     unlike creatures/druid (whose sprite gets redrawn on top of the halo,
     naturally hiding the centre), nothing redraws on top of the statue's
     halo. Fixed by punching the sprite's own footprint out of the blurred
     ring (`pygame.mask`-based, see below) for every entity uniformly, not
     just the statue — so the centre is always transparent and the
     background/sprite-art-already-drawn shows through.
  2. Several creatures (displacer beast especially) had visible flat/straight
     edges in the halo where the sprite's silhouette touches its crop
     bounding box (ears/tail/paws extending to the source art's edge).
     Fixed by increasing blur strength (`_HALO_BLUR_DIV` 6→3) — there's no
     curvature to recover from a hard-cropped edge, but a stronger blur
     softens it into something that reads as rounded rather than cut off.
- **Performance bug found via user report, not automated testing:** user
  noticed a multi-second freeze at startup that wasn't there before. Root
  cause: `_make_silhouette()`'s recolour step and the centre-punch step were
  both pure-Python per-pixel loops (`get_at`/`set_at`) running at full raw
  sprite resolution (~900px for several sprites) — ~6.7s total the first
  time all 10 halos needed building in the same frame (confirmed by direct
  benchmark, not just guessed). Rewrote both using `pygame.mask.from_surface()`
  + a single `BLEND_RGBA_MULT` blit each — C-level, no per-pixel Python
  access, no new dependency (considered numpy/`pygame.surfarray`, both
  available in this dev environment, but introducing numpy to a module the
  shipped game actually runs would break the project's stated "Pygame only"
  tech stack for anyone else running/cloning the public repo, so used
  pygame's own `mask` module instead). Brought the cold-start cost down to
  ~0.45s — confirmed no perceptible freeze after the fix, both via direct
  benchmark and live user confirmation. Visual output unchanged by the
  rewrite (same mask-multiply logic, just vectorised instead of looped).

**All 6 issues from the Session 13 HUD layout pass are now done.** Open
threads carried forward: player name placement (issue 3, never resolved —
see note there), statue halo quality (issue 6 — user may bring in an
AI-generated statue cutout to replace the extracted one).
- **Next:** back to the original Phase 5 IDEAS.md backlog — Shield rename,
  resource storage caps, multi-box visual indicator, fullscreen toggle,
  custom icon, text cross-reference pass, blink dog forage-pool bug.

### Session 14 — [23.06.2026]
**Phase 5 — Halo full-coverage fix; idle animation timing decoupled from game
speed; new backlog items captured.**

**Halo fix (follow-up to Session 13 issue 6).** The punch-out ring added to
fix the statue's halo (Session 13) was applied to every entity, but the hole
is fixed to a sprite's *base* layout position — for animated sprites (flumph
bob, etc.) the moving sprite no longer always covered that fixed hole, so the
ring's inner edge became visible at certain points in the animation cycle.
Root cause: only the statue actually needs a punched ring (nothing else
redraws on top of its halo); druid/creatures get their centre naturally
covered every frame by their own sprite redraw, at wherever they currently
are, animated or not. `game/renderer.py`: `_get_halo()`/`draw_halo()` gained
a `punch_center` flag (default `False`); only the statue's `draw_halo()` call
passes `punch_center=True`. Verified via rendered frames across a flumph bob
cycle — no exposed ring edge at any phase.

**Idle animation timing decoupled from game speed.** All idle animations
(blink_dog flicker, flumph bob, moss_wisp drift, pixie flutter, displacer_beast
ghost-offset, halo pulse) were keyed off `time_of_day`, which advances 60x
faster under dev speed — meaning no single tuning constant could look right
in both normal and dev mode (too slow normally, frantic in dev mode). Fixed
by switching all of them to `anim_time` — real elapsed wall-clock seconds via
`pygame.time.get_ticks()/1000.0` — which is completely unaffected by the
dev-speed multiplier. Threaded through `draw_scene()` and every per-creature
`draw_*()` function plus `halo_pulse()`; both `main.py` render call sites
(main loop and the name-entry screen) now pass `anim_time` through.

Also added idle "breathing" (a subtle vertical bob) to the four creatures
that previously had no animation at all — owlbear, druid, stirge,
pseudodragon — via a new `_breathe(anim_time, period, amplitude)` helper, and
to displacer_beast alongside its existing ghost-offset effect.

**Three rounds of speed tuning from live user feedback**, each value written
to `game/renderer.py` and confirmed before the next round (per
[[feedback_test_against_real_file]]):
1. Initial: blink_dog 0.35s, flumph 2.5s, moss_wisp 3.0/4.0s, pixie 0.5s, halo
   pulse 1.5s; breathing amplitude 2px, periods ~2.2–3.6s.
2. User: blink dog/moss/flumph/pixie "too quick" except blink dog "too quick
   in dev mode" specifically (symptom of the root cause above); breathing
   "too big". Slowed the flicker/drift group to 0.75x speed (period x1.333:
   blink_dog→0.467s, flumph→3.333s, moss_wisp→4.0/5.333s, pixie→0.667s) and
   cut breathing amplitude 2px→1px with periods x1.2 slower.
3. User: dog and pixie still way too fast (0.75x wasn't enough — much bigger
   correction needed for those two specifically); moss/flumph "almost
   perfect, slow a bit more"; breathing still read as "2 clicks up and 2
   down" on a "three point line" — since amplitude is already at the 1px
   floor (can't read as breathing at all below that), the fix was to space
   the discrete pixel transitions further apart by roughly doubling the
   breathing periods rather than reducing amplitude further. Final: blink_dog
   1.0s, pixie 1.3s, moss_wisp 4.6/6.13s, flumph 3.83s; breathing periods
   owlbear 6.0s, stirge 5.0s, pseudodragon 5.5s, displacer_beast 6.5s, druid
   7.0s, all amplitude 1px. **Accepted.**

**New backlog items captured this session** (not started — added to
`IDEAS.md`):
- Reconsider event/action menus for the statue and druid after all (Session
  13 issue 4 concluded a menu wasn't needed; revisit given subsequent work).
- Statue halo cleanup — the extracted `assets/sprites/statue.png` cutout
  (Session 13) is rough; clean it up or replace with an AI-generated cutout.
- Re-add player name display somewhere on-screen (removed in Session 13
  issue 3, placement never resolved since).
- Design the help/info menu for real (currently just a placeholder concept
  in IDEAS.md, several features — keybinds, feed limits — are waiting on it).
- Another design pass on the druid and owlbear sprites specifically — flagged
  as reading most out of place against the rest of the art.
- Reduce the flumph's sprite size.
- **Next:** original Phase 5 IDEAS.md backlog (Shield rename, resource
  storage caps, multi-box visual indicator, fullscreen toggle, custom icon,
  text cross-reference pass, blink dog forage-pool bug) plus the six new
  items above.