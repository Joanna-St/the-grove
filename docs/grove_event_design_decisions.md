# The Grove — Event System Design Decisions
*Session summary for handoff. For authored text, see grove_event_lines.md.*

---

## Scope of This Session
We are designing the **Phase 4 event system** before implementation in Claude Code. This covers creature events, grove events, and visitor events.

---

## Event Categories (High Level)
Three distinct event sources exist in the game:

- **Creature events** — spontaneous creature behaviour, bond-gated
- **Grove events** — area restoration milestones, state changes
- **Visitor events** — scripted arrivals with authored arcs

---

## Creature Events — Full Design

### Two Event Types Per Creature

**1. Fixed events (bond-level tied)**
- Fire once during a bond level at a random point after reaching it
- Never repeat
- ~2–3 per creature total
- Written with character specificity — these are the storytelling moments
- Reward: small bond gain on player dismissal

**2. Repeatable event (generic per creature)**
- One per creature
- Fires on a real-time cooldown indefinitely
- Flavoured per creature but mechanically identical across all
- Reward: small amount of all four resources + small bond gain
- The flavour of the interaction is the interesting part; the resource is ambient

---

### Trigger Logic
- Fixed events: random chance fires during the appropriate bond level window, after the level has been reached. Each has a cooldown to prevent back-to-back repeats.
- Repeatable event: real-time cooldown, no bond gate.
- Bond milestone events (existing) are separate and triggered through interaction/feeding — not part of this system.

---

### UI / Player Interaction
- When an event is available, a notification bubble appears above the creature sprite (consistent with the existing golden ring for interaction cooldown reset). Exclamation mark is a placeholder — final visual TBD.
- Player clicks the creature → bottom text box shows the event as a **new list item** alongside the existing interact/feed options.
- Interact and feed options remain in whatever state they are in (active or inactive) — the event does not block or replace them.
- Player clicks the event item → event text displays → rewards delivered → item disappears.
- A small portrait preview of the relevant creature (and for visitor events, the visitor) will appear above the top right edge of the message box. To be implemented across all message types.

---

### Resource Reward (Repeatable Event)
- Gives a small amount of **all four resources** (Forage, Heartwood, Glamour, Bond).
- Not creature-native specific — feels like the creature is contributing to the grove generally.
- Focus is on the flavour of the interaction, not resource specificity.

---

## Fixed Event Content
→ See grove_event_lines.md — Creature Fixed Events

## Repeatable Event Content
→ See grove_event_lines.md — Creature Repeatable Events

---

## Grove Events — Full Design

### Structure
- Pure flavour only — no mechanical weight, no rewards
- Triggered by notification bubble over the Silvanus statue; player clicks through. Visual placeholder TBD.
- Single shared pool, area-gated by unlock state, shared cooldown
- Events from unrestored areas do not fire until that area exists
- 2–3 events per area

### Register
Scales from quiet to uncanny by area:
- **Heartstone** — quiet, domestic, familiar
- **Thicket** — earthy, alive, slightly wild
- **Canopy** — airy, expansive, something watching from above
- **Feywild Boundary** — uncanny, pressured, occasionally wrong
- **Oldwood** — ancient, heavy, barely legible

## Grove Event Content
→ See grove_event_lines.md — Grove Events

---

## Visitor Events — Full Design

### Structure
- Six visitors, six finite authored arcs. Each visitor concludes and does not return.
- 2–3 beats per visitor arc, determined per character. Longer beats may span two message boxes.
- Notification bubble appears above the druid sprite (distinguishing visitor events from creature events above creatures, and grove events above the statue). Visual placeholder TBD.
- A small portrait preview of the visitor appears above the top right edge of the message box.
- Each beat is a discrete message moment. Time passes between beats — gap length is per character and noted below.
- No branching choices. Flavoured responses all lead to the same resolution.
- Rewards are diegetic — framed as objects or actions, with resource translation happening underneath.

### Visitor Roster & Triggers

| Visitor | Trigger | Arc length | Gap between beats |
|---|---|---|---|
| The Kid | Blink dog bond 2 | 2 beats (3 boxes) | Morning / midday |
| The Girl | Oldwood restored | 3 beats | Day 1 arrival / night / morning of day 2 |
| The Druid | Time gate | 3 beats | Day 1 arrival / days 2–3 / morning of day 3 |
| The Healer | Canopy restored | 3 beats | Day 1 arrival / few days / morning of day 4 |
| The Soldier | Random within time window | 3 beats (4 boxes) | Dusk / same night / first light |
| The Smith | Thicket restored | 2 beats (3 boxes) | Morning / midday |

## Visitor Event Content
→ See grove_event_lines.md — Visitor Events

---

## Ideas & Pending Decisions
- Notification visuals (exclamation mark is a placeholder throughout — creature events, grove events, visitor events all use the same system, final visual TBD)
- Portrait preview above top right of message box — to be implemented across all message types (creature events, grove events, visitor events)
