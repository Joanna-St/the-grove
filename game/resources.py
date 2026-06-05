class ResourceTracker:
    """
    Tracks forage, heartwood, glamour.
    Passive generation scales with active grove areas (size) and glamour health.
    """

    RESOURCES = ("forage", "heartwood", "glamour")
    COLOURS = {
        "forage":    (106, 168,  79),
        "heartwood": (153,  76,   0),
        "glamour":   (103,  78, 167),
    }
    LABEL_COLOURS = {
        "forage":    (180, 230, 150),
        "heartwood": (210, 140,  80),
        "glamour":   (180, 150, 230),
    }

    def __init__(self, config):
        self._cfg = config
        self._rates = config["resources"]["passive_base_rate_per_second"]
        start = config["resources"]["starting"]
        self.forage    = float(start["forage"])
        self.heartwood = float(start["heartwood"])
        self.glamour   = float(start["glamour"])

    # ------------------------------------------------------------------
    # Persistence

    def to_dict(self):
        return {
            "forage":    self.forage,
            "heartwood": self.heartwood,
            "glamour":   self.glamour,
        }

    def from_dict(self, data):
        self.forage    = float(data.get("forage",    self.forage))
        self.heartwood = float(data.get("heartwood", self.heartwood))
        self.glamour   = float(data.get("glamour",   self.glamour))

    # ------------------------------------------------------------------
    # Simulation

    def tick(self, dt_game, areas):
        """
        dt_game: in-game seconds elapsed this frame.
        areas:   Areas instance — provides grove_size and glamour_ratio.
        """
        glamour_ratio = min(1.0, self.glamour / max(1.0, areas.glamour_threshold()))
        size_mult = areas.size_multiplier()
        tick_mult = glamour_ratio * size_mult * dt_game

        self.forage    += self._rates["forage"]    * tick_mult
        self.heartwood += self._rates["heartwood"] * tick_mult
        self.glamour   += self._rates["glamour"]   * tick_mult

    def add(self, resource, amount):
        current = getattr(self, resource, 0.0)
        setattr(self, resource, max(0.0, current + amount))

    # ------------------------------------------------------------------
    # Rendering

    def render(self, surface, font, x, y):
        import pygame
        bar_w, bar_h = 220, 22
        padding = 10
        panel_w = bar_w + 120
        panel_h = len(self.RESOURCES) * (bar_h + padding) + padding

        bg = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        bg.fill((20, 20, 30, 180))
        surface.blit(bg, (x, y))

        for i, name in enumerate(self.RESOURCES):
            val = getattr(self, name)
            row_y = y + padding + i * (bar_h + padding)

            label = font.render(name.capitalize(), True, self.LABEL_COLOURS[name])
            surface.blit(label, (x + 8, row_y + 3))

            bar_x = x + 90
            pygame.draw.rect(surface, (50, 50, 60), (bar_x, row_y, bar_w, bar_h), border_radius=4)
            fill = min(int(bar_w * (val / 500.0)), bar_w)
            if fill > 0:
                pygame.draw.rect(surface, self.COLOURS[name], (bar_x, row_y, fill, bar_h), border_radius=4)
            pygame.draw.rect(surface, (100, 100, 120), (bar_x, row_y, bar_w, bar_h), 1, border_radius=4)

            num = font.render(f"{val:.1f}", True, (220, 220, 220))
            surface.blit(num, (bar_x + bar_w + 6, row_y + 3))
