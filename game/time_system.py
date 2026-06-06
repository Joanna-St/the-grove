class TimeSystem:
    """
    Session time: game_seconds advance only while the game is open.
    The grove waits — it does not suffer while closed.
    One in-game day = day_length_real_seconds of real time (multiplied by dev_speed when active).
    """

    def __init__(self, config):
        self._day_len  = config["time"]["day_length_real_seconds"]
        self._dev_mult = config["time"]["dev_speed_multiplier"]
        self._segments = config["time"]["time_of_day_segments"]

        self.dev_speed    = False
        self._game_seconds = 0.0

    # ------------------------------------------------------------------
    # Persistence

    def to_dict(self):
        return {"game_seconds": self._game_seconds}

    def from_dict(self, data):
        self._game_seconds = float(data.get("game_seconds", 0.0))

    # ------------------------------------------------------------------
    # Update

    def update(self, dt_real):
        """Advance time by dt_real seconds of real time."""
        self._game_seconds += dt_real * self._effective_multiplier()

    def _effective_multiplier(self):
        return self._dev_mult if self.dev_speed else 1.0

    # ------------------------------------------------------------------
    # Queries

    @property
    def game_seconds(self):
        return self._game_seconds

    @property
    def day_number(self):
        return int(self._game_seconds // self._day_len) + 1

    @property
    def time_of_day(self):
        """0.0 (midnight) → 1.0 (midnight next day)."""
        return (self._game_seconds % self._day_len) / self._day_len

    @property
    def period(self):
        t = self.time_of_day
        for name, (lo, hi) in self._segments.items():
            if lo <= t < hi:
                return name
        return "night"

    def toggle_dev_speed(self):
        self.dev_speed = not self.dev_speed
        return self.dev_speed
