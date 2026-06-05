import random
from game import dialogue as dlg


class Creature:
    def __init__(self, name, config):
        self.name = name
        self._rates = config["creatures"].get(name, {})
        self._arrival = config["arrival_game_seconds"].get(name, 300)
        bond_cfg = config["bond"]
        self._xp_per_interact = bond_cfg["xp_per_interact"]
        self._xp_thresholds   = bond_cfg["xp_thresholds"]
        self._interact_cd     = bond_cfg["interact_cooldown_real_seconds"]

        self.is_present      = False
        self.bond_xp         = 0.0
        self.bond_level      = 0
        self._cd_remaining   = 0.0   # real seconds until next interact
        self.dialogue_text   = ""
        self.dialogue_ttl    = 0.0   # real seconds to show dialogue
        self.bond_flash_ttl  = 0.0   # real seconds to show bond gain flash
        self.just_arrived    = False  # cleared after one frame

    # ------------------------------------------------------------------
    # Persistence

    def to_dict(self):
        return {
            "is_present": self.is_present,
            "bond_xp":    self.bond_xp,
            "bond_level": self.bond_level,
        }

    def from_dict(self, data):
        self.is_present = data.get("is_present", False)
        self.bond_xp    = float(data.get("bond_xp", 0.0))
        self.bond_level = int(data.get("bond_level", 0))

    # ------------------------------------------------------------------
    # Simulation

    def update(self, dt_real, game_seconds):
        if not self.is_present and game_seconds >= self._arrival:
            self.is_present  = True
            self.just_arrived = True

        if self._cd_remaining > 0:
            self._cd_remaining -= dt_real
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
        self.bond_xp        += self._xp_per_interact
        self._cd_remaining  = self._interact_cd
        self.bond_flash_ttl = 0.6

        levelled = (
            self.bond_level < len(self._xp_thresholds)
            and self.bond_xp >= self._xp_thresholds[self.bond_level]
        )
        if levelled:
            self.bond_level += 1
            text = dlg.MILESTONES.get(self.name, {}).get(self.bond_level, "")
        else:
            text = dlg.pick(dialogue_pool.get(self.bond_level, []))

        self.dialogue_text = text
        self.dialogue_ttl  = 6.0
        return levelled

    @property
    def cd_fraction(self):
        """0.0 = ready, 1.0 = just interacted."""
        return max(0.0, self._cd_remaining / self._interact_cd)


# ------------------------------------------------------------------

class Creatures:
    def __init__(self, config=None):
        if config:
            self.stirge    = Creature("stirge",    config)
            self.blink_dog = Creature("blink_dog", config)
        else:
            self.stirge    = None
            self.blink_dog = None
        self._all = [c for c in (self.stirge, self.blink_dog) if c]

    def to_dict(self):
        out = {}
        for c in self._all:
            out[c.name] = c.to_dict()
        return out

    def from_dict(self, data):
        for c in self._all:
            if c.name in data:
                c.from_dict(data[c.name])

    def update(self, dt_real, dt_game, game_seconds, resources):
        for c in self._all:
            c.update(dt_real, game_seconds)
            c.contribute(dt_game, resources)

    def get(self, name):
        return next((c for c in self._all if c.name == name), None)

    def present(self):
        return [c for c in self._all if c.is_present]
