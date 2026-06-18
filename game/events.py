import random

from game import dialogue as dlg


class Events:
    """
    Phase 4 event scheduler: creature stagger, grove events, and visitor arcs.
    """

    def __init__(self, config=None):
        self.grove_pending_event   = None   # {"text": str} or None
        self.visitor_pending_event = None   # {"boxes": [str, ...]} or None

        events_cfg = (config or {}).get("events", {})

        self._stagger_duration   = events_cfg.get("creature_event_stagger_seconds", 60)
        self._stagger_remaining  = 0.0

        self._grove_interval     = events_cfg.get("grove_event_interval_seconds", 600)
        self._grove_cd_remaining = self._grove_interval

        self._druid_min_day = events_cfg.get("visitor_druid_min_day", 10)

        self._visitor_done   = set()   # keys of completed arcs
        self._visitor_active = None    # {key, beat_idx, arrival_day, beat_consumed_game_seconds} or None

    # ------------------------------------------------------------------
    # Main update

    def update(self, dt_real, areas=None, creatures=None, time_sys=None):
        if self._stagger_remaining > 0:
            self._stagger_remaining -= dt_real

        if areas is not None and self.grove_pending_event is None:
            self._grove_cd_remaining -= dt_real
            if self._grove_cd_remaining <= 0:
                text = self._pick_grove_event(areas)
                if text is not None:
                    self.grove_pending_event = {"text": text}
                    self._grove_cd_remaining = self._grove_interval

        if time_sys is not None:
            if self._visitor_active is None and creatures is not None and areas is not None:
                self._try_activate_visitor(creatures, areas, time_sys)
            if self._visitor_active is not None and self.visitor_pending_event is None:
                self._check_beat_timing(time_sys)

    # ------------------------------------------------------------------
    # Visitor arc — trigger scanning

    def _check_trigger(self, key, creatures, areas, time_sys):
        if key == "kid":
            return creatures.blink_dog.bond_level >= 2
        if key == "girl":
            return areas.is_unlocked("oldwood")
        if key == "druid":
            return time_sys.day_number >= self._druid_min_day
        if key == "healer":
            return areas.is_unlocked("canopy")
        if key == "soldier":
            return creatures.displacer_beast.bond_level >= 3
        if key == "smith":
            return areas.is_unlocked("thicket")
        return False

    def _try_activate_visitor(self, creatures, areas, time_sys):
        for arc in dlg.VISITOR_ARCS:
            key = arc["key"]
            if key not in self._visitor_done and self._check_trigger(key, creatures, areas, time_sys):
                self._visitor_active = {
                    "key":                        key,
                    "beat_idx":                   0,
                    "beat_consumed_game_seconds": time_sys.game_seconds,
                }
                return

    # ------------------------------------------------------------------
    # Visitor arc — beat timing

    def _arc(self):
        return next(a for a in dlg.VISITOR_ARCS if a["key"] == self._visitor_active["key"])

    def _check_beat_timing(self, time_sys):
        active = self._visitor_active
        beat   = self._arc()["beats"][active["beat_idx"]]

        period_ok = (beat["unlock_periods"] is None
                     or time_sys.period in beat["unlock_periods"])
        gap_ok    = time_sys.game_seconds >= (
            active["beat_consumed_game_seconds"] + beat.get("min_gap_game_seconds", 0)
        )

        if period_ok and gap_ok:
            self.visitor_pending_event = {"boxes": beat["boxes"]}

    # ------------------------------------------------------------------
    # Visitor arc — player interaction

    def advance_visitor(self, resources, game_seconds=0.0):
        """Called when player dismisses the last box of a beat. Advances beat; delivers reward on arc completion."""
        if self._visitor_active is None:
            return

        active = self._visitor_active
        arc    = self._arc()

        self.visitor_pending_event = None
        active["beat_consumed_game_seconds"] = game_seconds
        active["beat_idx"] += 1

        if active["beat_idx"] >= len(arc["beats"]):
            for res, amount in arc["reward"].items():
                resources.add(res, amount)
            self._visitor_done.add(active["key"])
            self._visitor_active = None

    def visitor_display_name(self):
        """Returns the display name of the currently active visitor, or None."""
        if self._visitor_active is None:
            return None
        arc = self._arc()
        return arc.get("display_name", self._visitor_active["key"].capitalize())

    # ------------------------------------------------------------------
    # Grove events

    def _pick_grove_event(self, areas):
        pool = [
            (area, idx)
            for area, lines in dlg.GROVE_EVENTS.items()
            if areas.is_unlocked(area)
            for idx in range(len(lines))
        ]
        if not pool:
            return None
        area, idx = random.choice(pool)
        return dlg.GROVE_EVENTS[area][idx]

    # ------------------------------------------------------------------
    # Creature event stagger

    def can_fire_creature_event(self):
        return self._stagger_remaining <= 0

    def mark_creature_event_fired(self):
        self._stagger_remaining = self._stagger_duration

    # ------------------------------------------------------------------
    # Persistence

    def to_dict(self):
        return {
            "grove_pending_event":              self.grove_pending_event,
            "visitor_pending_event":            self.visitor_pending_event,
            "creature_event_stagger_remaining": self._stagger_remaining,
            "grove_cd_remaining":               self._grove_cd_remaining,
            "visitor_done":                     sorted(self._visitor_done),
            "visitor_active":                   self._visitor_active,
        }

    def from_dict(self, data):
        self.grove_pending_event   = data.get("grove_pending_event")
        self.visitor_pending_event = data.get("visitor_pending_event")
        self._stagger_remaining    = float(data.get("creature_event_stagger_remaining", 0.0))
        self._grove_cd_remaining   = float(data.get("grove_cd_remaining", self._grove_interval))
        self._visitor_done         = set(data.get("visitor_done", []))
        raw = data.get("visitor_active")
        if raw is not None:
            # Migrate old save shapes
            raw.pop("box_idx", None)
            raw.pop("arrival_day", None)
            if "beat_consumed_game_seconds" not in raw:
                raw["beat_consumed_game_seconds"] = 0.0
        self._visitor_active = raw
