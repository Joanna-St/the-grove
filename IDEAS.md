# Ideas & Revisits

Things to consider for later phases. Not current phase scope.

---

## Tuning & Balance

- **Resource storage caps** — bars are scaled to 500 (protection to 100) but values are currently uncapped and will overflow the visual. Options: (A) scale cap with grove size (500 × num_areas unlocked), (B) keep caps visual-only and let values bank freely. Revisit after Phase 3 when late-game generation rates are observable and unlock costs are balanced.



- **Ward decay rate** — current value (0.02/s, scaling with area count) may need adjustment once more areas are unlocked and the full late-game decay rate is observable. Revisit in Phase 3 playtesting.

- **Too many pop-up interactions even at regular (non-dev) speed** — flagged
  Session 15 by the user: creature events, grove events, and visitor beats
  are firing too frequently in normal play. Revisit the interval config
  values in `config.json` (`creature_event_interval_seconds`,
  `creature_event_stagger_seconds`, `grove_event_interval_seconds`, and the
  visitor arc gap timings in `dialogue.py`'s `VISITOR_ARCS`) and reduce
  frequency. Needs a normal-speed playtest to judge the right cadence, not
  just a dev-speed check.

---

## Bugs / Polish

- **Forage message references blink dog before it arrives** — `dlg.FORAGE`
  (game/dialogue.py) includes a line about the blink dog following you on a
  foraging trip. `dlg.pick(dlg.FORAGE)` doesn't check creature presence, so
  this can show up before the blink dog has arrived. Either gate that line on
  `creatures.blink_dog.is_present` or split FORAGE into presence-gated pools.

- **Dismiss-glyph zoom feels a bit too wobbly** — the rune disc's zoom
  animation (`_draw_dismiss_glyph`, game/renderer.py) reads slightly too
  jittery at the current amplitude/speed. Left as-is for now (signed off
  with the caveat), but worth tuning the scale range or easing later.

- **Text pass: maximise area/creature cross-references** — go over all written
  text (FORAGE, TEND_STATUE, FIXED_EVENTS, REPEATABLE_EVENTS, GROVE_EVENTS,
  VISITOR_ARCS, milestones) and check that creatures and areas are referenced
  by name consistently and as often as natural, so the grove reads as a single
  connected place rather than isolated creature/area vignettes. Do this as a
  full pass once all text content is otherwise final — revisit in Phase 5.

- **Creature reveal: outline-to-sprite fill** — instead of a creature simply
  popping into existence on arrival, show a faint outline/silhouette of its
  shape beforehand (mirroring the area greyscale-to-colour treatment), which
  fills in with the full sprite once the creature actually arrives. Nice-to-have,
  not core to the Phase 5 art swap — revisit once base sprite integration is done.

- **Locked-area desaturation isn't reading well in practice** — the Session 12
  implementation uses rough rectangular `_ZONE_RECTS` (game/renderer.py) since
  no real per-zone art masks exist; flagged then as "revisit if the rectangle
  edges read as visually wrong" — user confirmed Session 15 that it does. Plan:
  manually trace each locked area (thicket, canopy, feywild_boundary, oldwood)
  against `background.png` and add them as separate mask assets, replacing the
  rectangle approximation.

- **Dawn/day/dusk/night transition isn't reading well** — flagged Session 15,
  no root cause diagnosed yet. `draw_period_tint()` (game/renderer.py) is the
  overlay driving this since the sky got baked into the background art
  (Session 12) — needs investigation into whether it's a timing issue, a
  colour/opacity issue, or something else before deciding a fix.

---

## Creatures & Resources

- **Interaction-triggered resource drops** — rather than (or in addition to)
  passive drip, clicking a creature could trigger an immediate resource drop
  at that moment. Makes interactions feel purposeful beyond just dialogue and
  bond XP. Revisit when Phase 3 has more creatures contributing simultaneously
  and the passive model starts to feel invisible.

- **Random object drops / event seeds** — blink dog in particular should
  occasionally bring non-resource items (a boot, a coin, a button — noted in
  design doc). These breadcrumbs could seed or unlock visitor events in Phase 4.
  Track as a separate inventory or event-flag list rather than a resource.

---

## Window & Display

- **Windowed/fullscreen toggle at runtime** — F11 toggle didn't work reliably
  due to SDL2 window repositioning issues on Windows. Currently config-only
  (`"fullscreen": true/false` in config.json, requires restart). Worth
  revisiting in Phase 5 when polishing — may need a pygame._sdl2 approach
  or a launcher settings screen.

- **Custom window icon** — replace the default Pygame icon with something
  grove-themed (a leaf, the Silvanus symbol). Low effort, nice finish.
  Defer to Phase 5 alongside other art tasks.

---

## UI / Info

- **Info / help overlay** — a dedicated screen (key-bind TBD) showing controls,
  per-creature feeding limits (feeds/day, cooldown), and other reference info
  that used to live in the always-on HUD. Came up when the bond-status sidebar
  was replaced with per-creature bond bars (Session 13) — feed status
  (`Creature.feed_indicator`, game/creatures.py) no longer renders anywhere
  in-game, so this is where it should resurface rather than being shown live.
  Scope alongside the rest of the Phase 5 UI pass.

- **Help-menu indicator takes over the dev-speed badge's spot** — the "DEV
  SPEED [D]" badge currently sits top-right (Session 13) as a stopgap, since
  dev mode is a development-only tool and that corner was empty. When dev
  mode is eventually retired (pre-release), put the help-menu indicator/icon
  in that same top-right spot instead.

- **Help/info menu — actual design pass** — the "Info / help overlay" item
  above has only ever been a placeholder concept (key-bind TBD, contents
  sketched). Needs a real design pass: layout, what exactly it lists
  (controls, feed limits, anything else retired from the live HUD), how it's
  opened/closed. Several other parked items (keybinds cheat sheet, feed
  indicator) are blocked on this actually existing. Flagged Session 14.

- **Reconsider event/action menus for statue and druid** — Session 13 issue 4
  deliberately concluded a popup menu (Forage/Tend/Event) wasn't needed,
  extending the statue's existing event-if-pending-else-action click pattern
  to the druid instead. Revisit after living with that decision longer —
  flagged Session 14 as worth a second look, no specific complaint yet, just
  "possibly add after all." User asked Session 15 for an explicit pros/cons
  discussion next time before deciding either way.

- **Player name display — re-add somewhere on-screen** — removed from the
  live HUD in Session 13 issue 3 (alongside the keybinds cheat sheet);
  keybinds were folded into the future help menu, but the player name's
  placement was never resolved and the thread went cold. Needs an actual home
  on-screen. Flagged again Session 14.

- **Statue halo cutout cleanup** — `assets/sprites/statue.png` (Session 13
  issue 6) was extracted from the background art via colour-threshold
  segmentation purely to drive the halo silhouette; it's rough (uneven edges,
  slight green tinge) and only looks acceptable because the halo blurs it
  heavily. User decided Session 15: trace it manually as a separate asset
  (same approach as the locked-area masks above) rather than another AI
  extraction pass.

- **Sprite pixelation consistency — druid, owlbear, displacer_beast (maybe
  blink_dog)** — these read as most visually out of place against the rest
  of the art (flagged Session 14 re: druid/owlbear specifically). Session 15
  reframed this as a pixelation-level mismatch: try regenerating those
  smoother-looking sprites to be more pixelated, OR regenerate the rest of
  the set to be less pixelated to match them instead — a decision the user
  wants to make next session, not just a redo.

- **Reduce flumph sprite size** — flagged Session 14, not yet sized or
  positioned.
