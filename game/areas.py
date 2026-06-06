class Areas:
    """
    Tracks which grove areas are unlocked and when they were unlocked.
    Heartstone is always active; others are unlocked by spending resources.
    """

    ALL = ["heartstone", "thicket", "canopy", "feywild_boundary", "oldwood"]

    def __init__(self, config):
        self._cfg          = config["areas"]
        self._unlocked     = {"heartstone"}
        self._unlock_times = {"heartstone": 0.0}  # game_seconds at time of unlock

    # ------------------------------------------------------------------
    # Persistence

    def to_dict(self):
        return {
            "unlocked":     list(self._unlocked),
            "unlock_times": self._unlock_times,
        }

    def from_dict(self, data):
        self._unlocked     = set(data.get("unlocked", ["heartstone"]))
        saved_times        = data.get("unlock_times", {})
        self._unlock_times = {"heartstone": 0.0}
        for name in self._unlocked:
            self._unlock_times[name] = float(saved_times.get(name, 0.0))

    # ------------------------------------------------------------------
    # Queries

    def is_unlocked(self, name):
        return name in self._unlocked

    def unlock(self, name, game_seconds=0.0):
        self._unlocked.add(name)
        self._unlock_times[name] = float(game_seconds)

    def unlock_time(self, name):
        """Returns game_seconds when area was unlocked, or None if not yet unlocked."""
        return self._unlock_times.get(name)

    def size_multiplier(self):
        return float(len(self._unlocked))

    def has_feywild_boundary(self):
        return "feywild_boundary" in self._unlocked

    def next_to_unlock(self):
        for name in self.ALL:
            if name not in self._unlocked:
                return name
        return None

    def unlock_cost(self, name):
        return self._cfg[name].get("unlock_cost") or {}

    def can_afford(self, name, resources):
        for res, cost in self.unlock_cost(name).items():
            if getattr(resources, res, 0.0) < cost:
                return False
        return True
