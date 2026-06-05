# The Grove
*An Idle Creature Sanctuary Game*

Design Document — Final

---

## Overview

The Grove is a chill idle game built in Pygame. You play as a druid caretaker tending a magical grove on the edge of the Feywild — somewhere in Faerûn, within the broader Baldur's Gate 3 world. Your role is not to conquer or quest, but to maintain a space that creatures feel safe enough to inhabit. Resources accumulate passively. Creatures arrive, develop trust, and leave things behind. Small events fire in the background. The grove breathes.

*Tone reference: Undertale — creatures have individual personalities, emotional specificity, and small stories. Nothing is trivial. The stirge matters as much as the displacer beast.*

---

## Platform & Save System

- Built in Pygame (Python)
- Save system: JSON file on disk, loads on startup
- Time: hybrid — real elapsed time tracked even when closed; in-game day/night cycle visible while playing

---

## Resources

Four resource types. All can be gathered actively by the druid or brought passively by creatures (rate depends on bond level).

### Forage
- Berries, roots, herbs — used to feed and care for creatures
- Most creatures can bring forage; varies by personality

### Heartwood
- Fallen branches, timber — used for building and restoring grove areas
- Owlbear is a natural heartwood source (collateral forest damage)

### Glamour
- Magical energy — maintains the grove's protection via the Silvanus statue
- Low glamour = reduced passive generation across everything; visible grove decay
- Sources: pseudodragon, flumph, pixie (all leak Feywild energy passively)

### Bond
- Relational currency — individual per creature, earned through interactions
- Unlocks bond milestones, better resource contributions, and creature-specific perks

### Passive Generation Logic
- Base passive income tied to glamour level — healthier protection = more productive grove
- Rate also scales with grove size (number of restored areas)
- Creatures contribute passively based on their individual bond level

---

## Time System

- Hybrid real-time + in-game day cycle
- Real elapsed time calculated on load — grove has been ticking over while closed
- Visible day/night cycle while playing — affects creature behaviour, resource availability, atmosphere
- Day length TBD — roughly X real minutes per in-game day

---

## Game Loop

### Passive (idle)
- Resources tick in over time (rate: glamour level × grove size)
- Bonded creatures bring resources periodically
- Small flavour events fire on timers (creature behaviour, grove atmosphere)
- Visitor cameo events trigger occasionally based on conditions

### Active (player-driven)
- Forage — spend time, gain forage + heartwood (small glamour chance)
- Tend the Silvanus statue — spend glamour to maintain/restore protection level
- Interact with creatures — builds bond, triggers dialogue, occasionally prompts a gift
- Restore grove areas — spend heartwood + glamour to unlock new zones

---

## Event System

- **Creature events** — personality-driven flavour ("the blink dog has teleported into the pond again")
- **Grove events** — state-driven warnings or windfalls (glamour dropping, rare bloom)
- **Visitor cameos** — humanoid characters from the wider BG3 world appear with requests/quests; reward on resolution
- Visitor events imply the world beyond the grove without centering it

---

## Creature Roster

Eight creatures. Each has a distinct personality, arrival timing, resource contribution, bond milestones, and day/night behaviour. Bond milestones unlock perks and deepen the relationship — some creatures also have mechanical abilities at max bond.

### 1. Owlbear
- **Personality:** Big, anxious, accidentally destructive, deeply loyal once bonded. Doesn't understand its own size. Knocks things over and looks guilty.
- **Arrival:** Fairly early — lingers at grove edge before entering
- **Brings:** Heartwood (collateral forest damage)
- **Bond milestones:** Stops fleeing → lets you approach → follows on foraging trips → sleeps near the statue
- **Day/night:** Active at dawn, sleepy in the afternoon, makes distressing noises at night for no clear reason

### 2. Pseudodragon
- **Personality:** Tiny, telepathic, arrived uninvited and has decided it was here first. Communicates in impressions — you just suddenly know it finds you adequate. Sits on the highest point available. Has opinions about everything.
- **Arrival:** Early, uninvited, gives no indication it intends to leave
- **Brings:** Glamour (magical creature, constantly radiating mild telepathic static)
- **Bond milestones:** Stops hissing → lands on your shoulder once (just once) → gives early warning on incoming visitor events → purrs at you telepathically while you work
- **Max bond perk:** Early warning on visitor events (specific and actionable)
- **Day/night:** Peak insufferability in the morning, tolerable at dusk, glows faintly at night

### 3. Blink Dog
- **Personality:** Relentlessly enthusiastic, means well with every atom of its being. Teleports mid-fetch, mid-run, mid-sit, always looks briefly surprised. Cannot be still. The pseudodragon finds it offensive.
- **Arrival:** Early, loudly — appears one morning like it was always planning to
- **Brings:** Random mix of all resources (weighted away from glamour) + occasional non-resource items (a boot, a coin, a button) — breadcrumbs for visitor events
- **Bond milestones:** Stops teleporting onto you → comes back when called → brings more consistent resources → scouts foraging trips, doubles active yield
- **Day/night:** Feral energy at dawn, crashes in afternoon sun patch, chaos again by evening

### 4. Flumph
- **Personality:** Drifts in from the Feywild boundary, extremely courteous, slightly bewildered by material plane physics. Deeply empathetic — absorbs and reflects the emotional state of the grove. Glows warmly when the grove thrives; looks faintly distressed when glamour is low.
- **Arrival:** Mid-game — its arrival signals the grove is becoming something more than ordinary
- **Brings:** Glamour (leaks ambient psychic/magical energy constantly)
- **Bond milestones:** Stops drifting away → reflects your mood (visual/text cue) → becomes passive grove health indicator → occasionally softens negative events
- **Max bond perk:** Passive event dampener for negative grove events
- **Day/night:** Most present at twilight, almost invisible at noon; pulses at night in sync with the moss wisp

### 5. Moss Wisp
- **Personality:** Has no legible personality. More presence than creature. Ancient, unhurried, possibly not aware you exist as distinct from the grove. Doesn't arrive — becomes visible. You can't remember when it first appeared.
- **Arrival:** Mechanically early, but the text acknowledges you only just noticed it
- **Brings:** Forage — areas it drifts through are subtly more abundant
- **Bond:** Not conventional — responds to grove health, not direct interaction. You tend the grove; the wisp responds.
- **Max grove health perk:** Permanently illuminates the Oldwood, slightly increases passive generation across everything
- **Day/night:** Barely visible at noon, strengthens toward dusk, most present at night near the Silvanus statue

### 6. Pixie
- **Personality:** Chaotic neutral, cannot tell if it's being helpful, neither can it. Moves things. Rearranges things. Occasionally improves things by accident. Finds the flumph interesting and the stirge disgusting.
- **Arrival:** Mid-game, slips through the Feywild boundary — you notice because something small has been relocated
- **Brings:** Glamour (leaking Feywild energy everywhere, can't help it)
- **Bond milestones:** Stops hiding → helps intentionally (50/50 on whether it actually helps) → stops rearranging critical things → can be pointed at visitor events as a wildcard intervention
- **Max bond perk:** Wildcard visitor event intervention — you aim it at a problem and hope
- **Day/night:** Invisible at dawn, chaotic through the day, peak mischief at dusk, gone entirely at midnight

### 7. Displacer Beast
- **Personality:** Proud, intensely protective, carries grief from past encounters. Not indifferent — emotionally present, but that's exactly why it keeps distance. The displacement is self-protection, not aloofness. Has cared before and remembers how that went.
- **Arrival:** Late game — requires significantly expanded grove and consistently high glamour. Its arrival signals you've built something worth noticing.
- **Brings:** Heartwood and Glamour equally (moves through deep forest and Feywild boundary simultaneously)
- **Bond milestones:** Stops displacing away → found sleeping in the grove occasionally → appears on foraging trips (parallel, not with you) → stays permanently at grove edge. No fanfare. It has decided.
- **Max bond perk:** Actively protective of the grove — dampens threatening visitor events by presence alone
- **Note:** Only creature the pseudodragon acknowledges; even that is just a slow blink
- **Day/night:** Never fully visible in daylight; most present at night when its shimmer blends with shadows

### 8. Stirge
- **Personality:** Pathetic in the most endearing way. Hungry constantly, not apologetic about it. Loyal once fed. Not intelligent, but has a strong sense of who has been kind to it. Ugly. Knows it's ugly. Has made a kind of peace with this. The pixie finds it revolting; the stirge ignores this with quiet dignity.
- **Arrival:** Very early — first or second creature. No mystical reason. Just hungry.
- **Brings:** Forage (ranges wide looking for food, some comes back to the grove)
- **Bond milestones:** Stops targeting you specifically → roosts nearby → consistent forage contributions → becomes vigilant in an unexplained way
- **Max bond perk:** Early warning on grove health events (vague, instinctual — you notice it's agitated and check on things)
- **Note:** Distinct from pseudodragon's warning (specific visitor events) — stirge senses grove state, not minds
- **Day/night:** Most active at dusk and dawn, sluggish at midday, roosts near you at night specifically

---

## Grove Areas

Five areas unlocked progressively. Framing: restoration, not expansion — each area is damaged, overgrown, or Feywild-unstable and needs healing. All areas are visible from the start but clearly wrong; restoring them is a meaningful act. Creatures are tied to their home area and arrive only once it is restored.

### 1. The Heartstone — always active
- The centre of the grove; the Silvanus statue is here
- **Creatures:** Stirge, Blink Dog
- **Resources generated:** Forage, some Heartwood
- **Unlock requirement:** None — the grove just needs to exist and have food

### 2. The Thicket — first unlock
- Dense woodland edge — wilder, overgrown, needs clearing
- **Creatures:** Owlbear
- **Resources generated:** Heartwood (significantly — the owlbear cannot stop breaking things)
- **Unlock requirement:** Heartwood (low-moderate). Early game.

### 3. The Canopy — second unlock
- Treetops and high branches — damaged, unstable, needs structural restoration
- **Creatures:** Pseudodragon (has been making do with an inferior perch since early game, radiating disdain)
- **Resources generated:** Glamour — first and only glamour source until the Feywild Boundary. Critical for progression.
- **Unlock requirement:** Heartwood + some Glamour (moderate). Mid game. Note: glamour must come from the druid's own foraging until the pseudodragon settles — a deliberate early bottleneck.

### 4. The Feywild Boundary — third unlock
- The thin place where the material plane and the Feywild blur. Unstable, not damaged — the boundary is too volatile and needs stabilising. Light behaves slightly wrong; colours are too saturated; you sometimes see trees that aren't quite there.
- **Creatures:** Pixie, Flumph
- **Resources generated:** Glamour (significantly — both creatures leak Feywild energy constantly)
- **Unlock requirement:** Glamour-heavy (requires pseudodragon already generating glamour from the Canopy). Mid-to-late game.
- **Ongoing maintenance:** Glamour must stay above a threshold to keep the boundary stable — neglect it and it destabilises again

### 5. The Oldwood — final unlock
- The deep ancient part of the grove — centuries of tangled decay, heavy and quiet. Cannot be rushed.
- **Creatures:** Moss Wisp (fully manifests here), Displacer Beast
- **Resources generated:** Forage (wisp) + Heartwood and Glamour (displacer beast)
- **Unlock requirement:** Significant Heartwood + Glamour + time. Late game. The displacer beast's arrival additionally requires consistently high glamour.

### Progression Chain Summary

```
Stirge + Blink Dog (Forage/Heartwood)
  → restore Thicket
  → Owlbear (more Heartwood)
  → restore Canopy
  → Pseudodragon (first Glamour)
  → restore Feywild Boundary
  → Pixie + Flumph (more Glamour)
  → restore Oldwood
  → Moss Wisp + Displacer Beast
```

*Each unlock is gated not just by cost but by which creatures you have generating what. The progression is baked into the resource logic, not imposed artificially.*

---

## Creature Resource Profiles

Exact quantities and tick rates are not hardcoded — all values live in an external config file (JSON/YAML) for easy tuning. A dev speed mode (day cycle multiplier) will allow testing full progression arcs quickly.

**Forage sources:**
- Stirge — small but consistent; primary purpose, most reliable source
- Moss Wisp — moderate, ambient (areas it drifts through become more abundant)
- Blink Dog — small random amounts, unreliable by nature

**Heartwood sources:**
- Owlbear — large amounts, primary purpose; cannot stop breaking things
- Displacer Beast — moderate, equal split with glamour
- Blink Dog — small random amounts, unreliable

**Glamour sources:**
- Pseudodragon — moderate; sole early source and critical bottleneck for mid-game progression
- Flumph — moderate
- Pixie — moderate
- Displacer Beast — moderate, equal split with heartwood
- Blink Dog — negligible, rare

**Bond scaling:** All contributions increase with bond level — exact multipliers defined in config file.

**Config file covers:**
- Resource tick rates per creature per bond level
- Restoration costs per area
- Day cycle length + dev speed multiplier
- Glamour decay rate for Feywild Boundary maintenance
- Event trigger frequencies

---

## The Druid

- Name chosen by the player at the start of the game
- Appearance: hooded robe with natural detailing (leaves, moss, bark elements) — gender neutral by design, readable at small pixel art scale
- Animation: idle only (gentle breathing, cloak ripple, ambient leaves) — no walking cycle needed
- No separate stats or progression — the druid is the vehicle, not the subject. Their growth is expressed through what the grove becomes.
- Actions: forage, tend the Silvanus statue, interact with creatures, restore grove areas — all handled through UI, not physical movement
- The druid is the still centre — creatures move, the wisp drifts, the blink dog teleports chaotically. The druid stands quietly and tends.

---

## Win Condition & Postgame

- **Win condition:** All five areas fully restored + max bond with all eight creatures
- Game does not end — continues in a quiet postgame maintenance mode. The grove is whole; you just tend it.
- **Flavour events:** Procedural, template-based with variable pools. Repetition fine — charm is in the templates.
- **Creature dialogue:** Finite pool per bond level, expands as bond deepens, stops expanding at max. Repetition fine in postgame.
- **Visitor cameos:** Fully authored, finite arcs. Each visitor concludes and does not return. The grove outlasts them.
- **Postgame cadence** slows deliberately — fewer interruptions, more quiet. Intentional, not a gap.

---

## Visitor Cameo Cast

Six visitors, six finite authored arcs. All are BG3 side characters — no origin companions. Each has a distinct reason to visit and a conclusion to their arc.

- **Mol** — small, chaotic, probably connected to something the blink dog dragged in. Side character energy; lighter arc.
- **Arabella** — deeper emotional arc; her BG3 journey involves the grove directly, lots to work with as a returning presence.
- **Rath** — duty-bound and serious; comes to assess what the grove has become. Leaves with complicated feelings.
- **Nettie** — practical healer energy, direct grove ties; comes with a specific problem to solve. Slightly prickly, ultimately warm.
- **Zevlor** — weightier, more emotional visit; gratitude with grief underneath. The most quietly affecting arc.
- **Dammon** — looking for something specific from the grove; transactional but warm. Probably the most fun arc to write.

---

## Development Phases

Each phase must be fully working before moving to the next. New ideas during build go on a list, not into the current phase. This document is the stable design bible; CLAUDE.md is the living reference updated each session.

### Phase 1 — Foundation
- Project structure, Pygame window, core game loop
- Config file (all tunable values: resource rates, restoration costs, day length, event frequencies, glamour decay, dev speed multiplier)
- Save/load system (JSON)
- Hybrid time system: real elapsed time tracked when closed, in-game day/night cycle while playing, dev speed mode
- Resource tracking (no art yet — rectangles and text only)

*Deliverable: the game launches, time passes, resources are tracked, save and reload works.*

### Phase 1.5 — Minimal Visual Layer
- Rough placeholder pixel sprites: druid idle, stirge, blink dog
- Basic Heartstone background, minimal UI (resource counters, interaction prompts)

*Deliverable: it looks vaguely like a grove. Not final, not precious — enough to feel like something.*

### Phase 2 — The Heartstone (Demo)
- Stirge and blink dog arrive with full interaction, bond tracking, and resource generation
- Silvanus statue tending, glamour system working
- Player name entry at first launch

*Deliverable: playable demo — you can tend the grove, feed the stirge, watch the blink dog cause chaos.*

### Phase 3 — Full Progression
- Remaining four areas unlock in order (Thicket, Canopy, Feywild Boundary, Oldwood)
- Remaining six creatures arrive with personalities, bond milestones, and perks
- Restoration mechanic fully working, passive generation scaling with glamour and grove size

*Deliverable: full progression arc playable from start to win condition.*

### Phase 4 — Events & Visitors
- Procedural flavour event system with template pools
- Creature dialogue pools per bond level
- All six visitor arcs scripted and implemented

*Deliverable: the grove feels alive, populated with story and personality.*

### Phase 5 — Art & Polish
- Final pixel art sprites replacing all placeholders: druid idle animation, all eight creatures, all five area backgrounds
- UI refinement
- Sound (ambient, interactions) — optional, to be decided during development

*Deliverable: the game looks and feels like we imagined it.*
