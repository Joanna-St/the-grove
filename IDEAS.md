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

- **Dawn/day/dusk/night transition isn't reading well** — flagged Session 15.
  Addressed Session 19, pending a normal-speed check before closing: periods
  switched hard (sky + tint popped in one frame) and night was only 75s of a
  600s day. Now the sky gradient and tint crossfade over
  `period_crossfade_fraction` (0.04 ≈ 24s) via `TimeSystem.period_blend`, and
  segments are dawn 60s / day ~264s / dusk 60s / night ~216s. Close once the
  user has watched a few transitions at normal speed.

---

## Post-art-integration tuning (flagged Session 19)

Raised once the Session 18 art was wired in at spec positions/sizes.
**Agreed order (Session 19):** (1) remove displacer beast ghost, (2) tighten
halo, (3) ambient glow for wisp/pixie/flumph, (4) ground shadows, (5) idle
animation pass, (6) UI/interaction pass (bond bar + shape-accurate clicks).
Statue glow tuning slots into (3) or (4). Owlbear overlapping the message
box was checked live and is fine — not an issue.

- **Remove the displacer beast's ghost-offset double image** — the
  translucent second blit in `draw_displacer_beast` (game/renderer.py);
  user wants it gone. Keep its breathing.

- **Ambient glow behind moss wisp, pixie, flumph** — render-time blurred
  coloured ellipse behind the sprite, following its animation offset; built
  once and cached like the halos. Spec values (docs/phase5_art_spec.csv):
  wisp green-white r≈1.1× height, pixie violet-blue r≈0.8×, flumph soft pink
  r≈0.9×.

- **Shadows under grounded sprites** — needs a short design pass first:
  which sprites (druid, stirge, blink dog, owlbear, displacer beast; blink
  dog is mid-leap so its shadow sits below it, not touching), and whether
  the statue gets one at all (a root contact shadow was tried and rejected
  in Session 18 — see "Statue root/ground blend treatment" below). Shadows
  should stay put while sprites bob, so do this before the idle pass.

- **Statue ambient glow barely visible** — re-anchored in Session 19 to the
  new statue (`_STATUE_GLOW_*` in game/renderer.py) but the much larger
  sprite now hides most of it. Tune or drop.

- **Idle motion pass, everyone — moss wisp especially** — the wisp's drift
  (`draw_moss_wisp`, game/renderer.py: ±3px on x/y, periods 4.6s/6.13s)
  reads as very erratic on the new sprite. Revisit all idle animations
  (breathing, blink dog flicker, flumph bob, pixie flutter) now that sprites
  are larger and differently shaped — the Session 14 amplitudes/periods were
  tuned against the old, smaller art.

- **Tighten the notification halo** — the halo spreads too far around every
  sprite. Tunables are `_HALO_SCALE` (1.18) and `_HALO_BLUR_DIV` (3) in
  game/renderer.py; the blur was raised in Session 13 to soften flat edges
  where old sprites touched their crop box, which may matter less with the
  new art.

- **Bond bar placement** — bars currently sit under each sprite, which
  breaks for the owlbear (its bottom edge runs off-screen by design, so its
  bar is invisible) and depends on per-creature gap overrides
  (`_BOND_BAR_GAP_OVERRIDE`). Options: (A) move bars above each sprite,
  (B) a status bar off to the side listing every present creature,
  (C) show bond inside the message box when a creature is selected.

- **Shape-accurate click areas** — `sprite_rect()` hit-tests a plain
  rectangle, which is far bigger than the art for the owlbear (covers most
  of the bottom-left brambles) and displacer beast (empty space around the
  tentacles). Hit-test against the sprite's alpha mask instead (same
  `pygame.mask` approach the halo already uses). Part of the UI pass with
  the bond bar move.

- **Area unlock transition** — unlocking an area currently swaps its
  greyscale for colour instantly. Consider animating colour back in (fade,
  or spreading out from the area's creatures). Pairs naturally with the
  "creature reveal: outline-to-sprite fill" idea under Bugs / Polish.

- **Mist over locked areas** — locked zones are currently plain greyscale
  (kept as-is in Session 19 when the zones were retraced). Consider adding a
  faint mist/fog layer over them so they read as dormant or veiled rather
  than just desaturated. Would reuse the same combined locked-zone mask
  (`_locked_zones_mask`, game/renderer.py); pairs with the unlock transition
  above (mist clearing as an area unlocks).

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

- **Statue root/ground blend treatment** — Session 18's full-art redo made
  the statue a real standalone sprite (living-wood figure rooted into the
  ground, no base/plinth), which makes the old "rough hand-extracted cutout"
  item above obsolete. Tried, in a throwaway mockup, blending the sprite's
  root-tips into the clearing floor via (1) a soft alpha feather on the
  bottom ~15% of the sprite and (2) a blurred dark contact-shadow ellipse
  underneath. Mixed result — visibly softer, but didn't quite read right;
  user chose to skip it and keep the hard-edged sprite as placed. Worth
  another attempt later with a different technique (color-matching the root
  tips to the dirt, or scattering a few ground-level moss/grass elements
  over the seam) once more of the redo set exists and there's more to judge
  it against.