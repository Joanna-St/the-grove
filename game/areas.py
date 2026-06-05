class Areas:
    """
    Tracks which grove areas are unlocked.
    Heartstone is always active; others are unlocked by spending resources.
    """

    ALL = ["heartstone", "thicket", "canopy", "feywild_boundary", "oldwood"]

    def __init__(self, config):
        self._cfg = config["areas"]
        self._unlocked = {"heartstone"}

    # ------------------------------------------------------------------
    # Persistence

    def to_dict(self):
        return {"unlocked": list(self._unlocked)}

    def from_dict(self, data):
        self._unlocked = set(data.get("unlocked", ["heartstone"]))

    # ------------------------------------------------------------------
    # Queries

    def is_unlocked(self, name):
        return name in self._unlocked

    def unlock(self, name):
        self._unlocked.add(name)

    def size_multiplier(self):
        return float(len(self._unlocked))

    def glamour_threshold(self):
        """Minimum glamour needed to keep the feywild boundary stable."""
        if "feywild_boundary" in self._unlocked:
            return self._cfg["feywild_boundary"]["unlock_cost"].get("glamour", 30.0)
        return 1.0

    def unlock_cost(self, name):
        return self._cfg[name].get("unlock_cost") or {}

    def can_afford(self, name, resources):
        for res, cost in self.unlock_cost(name).items():
            if getattr(resources, res, 0.0) < cost:
                return False
        return True
