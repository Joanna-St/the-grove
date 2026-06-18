import random
from game import dialogue as dlg


class Creature:
    def __init__(self, name, config):
        self.name   = name
        c_cfg       = config["creatures"].get(name, {})
        self._rates = c_cfg

        self._area          = c_cfg.get("area", "heartstone")
        self._arrival_delay = c_cfg.get("arrival_delay_game_seconds", 120)

        bond_cfg = config["bond"]
        self._xp_per_interact = bond_cfg["xp_per_interact"]
        self._xp_thresholds   = bond_cfg["xp_thresholds"]
        self._interact_cd     = bond_cfg["interact_cooldown_real_seconds"]

        feed_cfg = c_cfg.get("feeding", {})
        self._feeds_per_day = feed_cfg.get("feeds_per_day", 1)
        self._feed_xp       = feed_cfg.get("bond_xp_per_feed", 8)
        self._feed_cd       = feed_cfg.get("cooldown_real_seconds", 0)

        events_cfg = config["events"]
        self._fixed_delay_range        = tuple(events_cfg["fixed_event_delay_range_seconds"])
        self._fixed_event_bond_xp      = events_cfg["fixed_event_bond_xp"]
        self._repeatable_interval      = events_cfg["creature_event_interval_seconds"]
        self._repeatable_event_bond_xp = events_cfg["repeatable_event_bond_xp"]
        self._repeatable_resource_yield = events_cfg["repeatable_event_resource_yield"]

        self.is_present        = False
        self.bond_xp           = 0.0
        self.bond_level        = 0
        self._cd_remaining     = 0.0
        self.dialogue_text     = ""
        self.dialogue_ttl      = 0.0
        self.bond_flash_ttl    = 0.0
        self.just_arrived      = False
        self.feeds_today       = 0
        self._last_day         = 0
        self._feed_cd_remaining = 0.0
        self.pending_event     = None   # {"text": str, "reward": {...}} or None

        self._fixed_fired           = set()   # bond levels with a fired fixed event
        self._fixed_event_pending   = None    # {"level": N, "delay": seconds} or None
        self._repeatable_cd_remaining = self._repeatable_interval

    # ------------------------------------------------------------------
    # Persistence

    def to_dict(self):
        return {
            "is_present":       self.is_present,
            "bond_xp":          self.bond_xp,
            "bond_level":       self.bond_level,
            "feeds_today":      self.feeds_today,
            "last_day":         self._last_day,
            "feed_cd_remaining": self._feed_cd_remaining,
            "pending_event":    self.pending_event,
            "fixed_fired":            sorted(self._fixed_fired),
            "fixed_event_pending":    self._fixed_event_pending,
            "repeatable_cd_remaining": self._repeatable_cd_remaining,
        }

    def from_dict(self, data):
        self.is_present        = data.get("is_present", False)
        self.bond_xp           = float(data.get("bond_xp", 0.0))
        self.bond_level        = int(data.get("bond_level", 0))
        self.feeds_today       = int(data.get("feeds_today", 0))
        self._last_day         = int(data.get("last_day", 0))
        self._feed_cd_remaining = float(data.get("feed_cd_remaining", 0.0))
        self.pending_event      = data.get("pending_event")
        self._fixed_fired         = set(data.get("fixed_fired", []))
        self._fixed_event_pending = data.get("fixed_event_pending")
        self._repeatable_cd_remaining = float(
            data.get("repeatable_cd_remaining", self._repeatable_interval)
        )

    # ------------------------------------------------------------------
    # Simulation

    def update(self, dt_real, game_seconds, day_number, areas, events):
        if not self.is_present:
            unlock_t = areas.unlock_time(self._area)
            if unlock_t is not None and game_seconds >= unlock_t + self._arrival_delay:
                self.is_present   = True
                self.just_arrived = True

        if day_number > self._last_day:
            self.feeds_today = 0
            self._last_day   = day_number

        if self._cd_remaining > 0:
            self._cd_remaining -= dt_real
        if self._feed_cd_remaining > 0:
            self._feed_cd_remaining -= dt_real
        if self.dialogue_ttl > 0:
            self.dialogue_ttl -= dt_real
        else:
            self.dialogue_text = ""
        if self.bond_flash_ttl > 0:
            self.bond_flash_ttl -= dt_real

        if self.is_present and self.pending_event is None:
            self._update_events(dt_real, events)

    def _update_events(self, dt_real, events):
        # Step 1: schedule the next un-fired fixed event, if any.
        if self._fixed_event_pending is None:
            for level in range(1, self.bond_level + 1):
                if level not in self._fixed_fired and level in dlg.FIXED_EVENTS.get(self.name, {}):
                    self._fixed_event_pending = {
                        "level": level,
                        "delay": random.uniform(*self._fixed_delay_range),
                    }
                    break

        # Step 2: deliver the scheduled fixed event once its delay elapses.
        if self._fixed_event_pending is not None:
            self._fixed_event_pending["delay"] -= dt_real
            if self._fixed_event_pending["delay"] <= 0 and events.can_fire_creature_event():
                level = self._fixed_event_pending["level"]
                self.pending_event = {
                    "text":   dlg.FIXED_EVENTS[self.name][level],
                    "reward": {"bond": self._fixed_event_bond_xp},
                }
                self._fixed_fired.add(level)
                self._fixed_event_pending = None
                events.mark_creature_event_fired()
            return

        # Step 3: otherwise, deliver a repeatable event once its cooldown elapses.
        self._repeatable_cd_remaining -= dt_real
        if self._repeatable_cd_remaining <= 0 and events.can_fire_creature_event():
            self.pending_event = {
                "text": dlg.REPEATABLE_EVENTS.get(self.name, ""),
                "reward": {
                    "forage":    self._repeatable_resource_yield,
                    "heartwood": self._repeatable_resource_yield,
                    "glamour":   self._repeatable_resource_yield,
                    "bond":      self._repeatable_event_bond_xp,
                },
            }
            self._repeatable_cd_remaining = self._repeatable_interval
            events.mark_creature_event_fired()

    def contribute(self, dt_game, resources):
        if not self.is_present:
            return
        lvl = self.bond_level
        for key, rates in self._rates.items():
            if key.endswith("_per_second"):
                res = key[:-len("_per_second")]
                resources.add(res, rates[lvl] * dt_game)

    # ------------------------------------------------------------------
    # Interaction

    @property
    def can_interact(self):
        return self.is_present and self._cd_remaining <= 0

    def interact(self, dialogue_pool):
        self.bond_xp       += self._xp_per_interact
        self._cd_remaining  = self._interact_cd
        self.bond_flash_ttl = 0.6
        return self._resolve_bond(dialogue_pool)

    # ------------------------------------------------------------------
    # Feeding

    @property
    def can_feed(self):
        return (self.is_present
                and self.feeds_today < self._feeds_per_day
                and self._feed_cd_remaining <= 0)

    @property
    def feed_indicator(self):
        remaining = self._feeds_per_day - self.feeds_today
        return "[f:" + "*" * remaining + "-" * self.feeds_today + "]"

    def feed(self, dialogue_pool):
        self.feeds_today        += 1
        self.bond_xp            += self._feed_xp
        self.bond_flash_ttl      = 0.6
        self._feed_cd_remaining  = self._feed_cd
        return self._resolve_bond(dialogue_pool)

    # ------------------------------------------------------------------
    # Shared

    def _resolve_bond(self, dialogue_pool):
        levelled = (
            self.bond_level < len(self._xp_thresholds)
            and self.bond_xp >= self._xp_thresholds[self.bond_level]
        )
        if levelled:
            self.bond_level += 1
            text = dlg.MILESTONES.get(self.name, {}).get(self.bond_level, "")
        else:
            if isinstance(dialogue_pool, dict):
                text = dlg.pick(dialogue_pool.get(self.bond_level, []))
            else:
                text = dlg.pick(dialogue_pool)

        self.dialogue_text = text
        self.dialogue_ttl  = 6.0
        return levelled

    @property
    def cd_fraction(self):
        return max(0.0, self._cd_remaining / self._interact_cd)

    # ------------------------------------------------------------------
    # Events

    @property
    def has_event(self):
        return self.pending_event is not None


# ------------------------------------------------------------------

class Creatures:
    _NAMES = [
        "stirge", "blink_dog", "owlbear", "pseudodragon",
        "flumph", "moss_wisp", "pixie", "displacer_beast",
    ]

    def __init__(self, config=None):
        self._all = []
        if config:
            for name in self._NAMES:
                c = Creature(name, config)
                setattr(self, name, c)
                self._all.append(c)

    def to_dict(self):
        return {c.name: c.to_dict() for c in self._all}

    def from_dict(self, data):
        for c in self._all:
            if c.name in data:
                c.from_dict(data[c.name])

    def update(self, dt_real, dt_game, game_seconds, day_number, areas, resources, events):
        for c in self._all:
            c.update(dt_real, game_seconds, day_number, areas, events)
            c.contribute(dt_game, resources)

    def get(self, name):
        return next((c for c in self._all if c.name == name), None)

    def present(self):
        return [c for c in self._all if c.is_present]
