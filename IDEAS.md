# Ideas & Revisits

Things to consider for later phases. Not current phase scope.

---

## Tuning & Balance

- **Resource storage caps** — bars are scaled to 500 (protection to 100) but values are currently uncapped and will overflow the visual. Options: (A) scale cap with grove size (500 × num_areas unlocked), (B) keep caps visual-only and let values bank freely. Revisit after Phase 3 when late-game generation rates are observable and unlock costs are balanced.



- **Shield decay rate** — current value (0.02/s, scaling with area count) may need adjustment once more areas are unlocked and the full late-game decay rate is observable. Revisit in Phase 3 playtesting.

- **"Shield" display name** — "Shield" is functional but may not fit the grove tone. Consider something more druidic/Feywild-flavoured (e.g. "Ward", "Veil", "Sanctity"). Decide when the full HUD is finalised in Phase 5.

---

## Bugs / Polish

- **Forage message references blink dog before it arrives** — `dlg.FORAGE`
  (game/dialogue.py) includes a line about the blink dog following you on a
  foraging trip. `dlg.pick(dlg.FORAGE)` doesn't check creature presence, so
  this can show up before the blink dog has arrived. Either gate that line on
  `creatures.blink_dog.is_present` or split FORAGE into presence-gated pools.

- **Multi-box text: visual "next" indicator and ESC hint** — when a text box has more content to click through (e.g. visitor beat 2a→2b), there's no visual cue that another box follows. ESC is suppressed on non-last boxes (so it can't be used to close), but the text box still shows "[ESC] close" in the keybinds. Consider: (A) hiding or greying out the ESC hint on non-last boxes, (B) adding a small "▶" / "more..." glyph at the bottom-right. Revisit in Phase 5 alongside other UI polish.

- **Event text overflows the text box** — `draw_text_box` (game/renderer.py)
  caps event/dialogue text at 3 wrapped lines (`lines[:3]`); anything beyond
  that is silently cut off. The blink dog Bond 1 fixed event (5 sentences)
  overruns this badly. Revisit the FIXED_EVENTS / REPEATABLE_EVENTS text in
  `dialogue.py` — either trim the longer entries to fit ~3 lines at the
  current box width/font, or split into multi-box. Worth a pass over all 8 creatures' fixed + repeatable events, not
  just blink dog.

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
  "possibly add after all."

- **Player name display — re-add somewhere on-screen** — removed from the
  live HUD in Session 13 issue 3 (alongside the keybinds cheat sheet);
  keybinds were folded into the future help menu, but the player name's
  placement was never resolved and the thread went cold. Needs an actual home
  on-screen. Flagged again Session 14.

- **Statue halo cutout cleanup** — `assets/sprites/statue.png` (Session 13
  issue 6) was extracted from the background art via colour-threshold
  segmentation purely to drive the halo silhouette; it's rough (uneven edges,
  slight green tinge) and only looks acceptable because the halo blurs it
  heavily. Clean up the extraction or replace with an AI-generated cutout.

- **Druid and owlbear sprite redesign pass** — of all 8 creatures + the
  druid, these two read as most visually out of place against the rest of
  the art (per user feedback, Session 14). Worth a dedicated look — possibly
  new AI generation passes, similar to how owlbear/displacer_beast needed
  reference images in Session 10.

- **Reduce flumph sprite size** — flagged Session 14, not yet sized or
  positioned.
