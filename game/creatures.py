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
        }

    def from_dict(self, data):
        self.is_present        = data.get("is_present", False)
        self.bond_xp           = float(data.get("bond_xp", 0.0))
        self.bond_level        = int(data.get("bond_level", 0))
        self.feeds_today       = int(data.get("feeds_today", 0))
        self._last_day         = int(data.get("last_day", 0))
        self._feed_cd_remaining = float(data.get("feed_cd_remaining", 0.0))

    # ------------------------------------------------------------------
    # Simulation

    def update(self, dt_real, game_seconds, day_number, areas):
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

    def update(self, dt_real, dt_game, game_seconds, day_number, areas, resources):
        for c in self._all:
            c.update(dt_real, game_seconds, day_number, areas)
            c.contribute(dt_game, resources)

    def get(self, name):
        return next((c for c in self._all if c.name == name), None)

    def present(self):
        return [c for c in self._all if c.is_present]
