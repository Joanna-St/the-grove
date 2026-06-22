class ResourceTracker:
    """
    Tracks forage, heartwood, glamour, and protection.
    Passive generation scales with protection level × grove size.
    Protection decays in real time; glamour is spent to restore it via statue tending.
    """

    RESOURCES = ("forage", "heartwood", "glamour", "protection")
    MAXES = {
        "forage": 500, "heartwood": 500, "glamour": 500, "protection": 100,
    }
    COLOURS = {
        "forage":     (106, 168,  79),
        "heartwood":  (153,  76,   0),
        "glamour":    (103,  78, 167),
        "protection": (190, 155,  45),
    }
    LABEL_COLOURS = {
        "forage":     (180, 230, 150),
        "heartwood":  (210, 140,  80),
        "glamour":    (180, 150, 230),
        "protection": (230, 205, 110),
    }
    DISPLAY_NAMES = {
        "forage": "Forage", "heartwood": "Heartwood",
        "glamour": "Glamour", "protection": "Shield",
    }

    # Slim HUD panel geometry — exposed so callers can position the panel
    # relative to other bottom-right UI without duplicating its dimensions.
    PANEL_BAR_W   = 80
    PANEL_BAR_H   = 15
    PANEL_PAD     = 8
    PANEL_LABEL_W = 72
    PANEL_VALUE_W = 46
    PANEL_W = PANEL_LABEL_W + PANEL_BAR_W + PANEL_VALUE_W + PANEL_PAD * 2
    PANEL_H = len(RESOURCES) * (PANEL_BAR_H + PANEL_PAD) + PANEL_PAD

    def __init__(self, config):
        self._cfg      = config
        self._rates    = config["resources"]["passive_base_rate_per_second"]
        self._prot_cfg = config["protection"]
        start = config["resources"]["starting"]
        self.forage     = float(start["forage"])
        self.heartwood  = float(start["heartwood"])
        self.glamour    = float(start["glamour"])
        self.protection = float(self._prot_cfg["starting"])

    # ------------------------------------------------------------------
    # Persistence

    def to_dict(self):
        return {
            "forage":     self.forage,
            "heartwood":  self.heartwood,
            "glamour":    self.glamour,
            "protection": self.protection,
        }

    def from_dict(self, data):
        self.forage     = float(data.get("forage",     self.forage))
        self.heartwood  = float(data.get("heartwood",  self.heartwood))
        self.glamour    = float(data.get("glamour",    self.glamour))
        self.protection = float(data.get("protection", self.protection))

    # ------------------------------------------------------------------
    # Simulation

    def tick(self, dt_real, dt_game, areas):
        """
        dt_real: real seconds this frame (for protection decay).
        dt_game: in-game seconds this frame (for resource generation).
        """
        # Generation scales with protection; floor ensures a faint trickle at 0
        prot_ratio = self.protection / self._prot_cfg["max"]
        min_mult   = self._prot_cfg["min_generation_multiplier"]
        gen_mult   = min_mult + (1.0 - min_mult) * prot_ratio

        size_mult  = areas.size_multiplier()
        tick_mult  = gen_mult * size_mult * dt_game

        self.forage    += self._rates["forage"]    * tick_mult
        self.heartwood += self._rates["heartwood"] * tick_mult
        self.glamour   += self._rates["glamour"]   * tick_mult

        # Protection decays in real time (not game time — stays meaningful in dev mode)
        decay = self._prot_cfg["decay_per_real_second"] * size_mult
        if areas.has_feywild_boundary():
            decay += self._prot_cfg["feywild_boundary_extra_decay"]
        self.protection = max(0.0, self.protection - decay * dt_real)

    def add(self, resource, amount):
        current = getattr(self, resource, 0.0)
        if resource == "protection":
            setattr(self, resource, min(self._prot_cfg["max"], max(0.0, current + amount)))
        else:
            setattr(self, resource, max(0.0, current + amount))

    # ------------------------------------------------------------------
    # Rendering

    def render(self, surface, font, x, y):
        import pygame
        bar_w, bar_h = self.PANEL_BAR_W, self.PANEL_BAR_H
        padding      = self.PANEL_PAD
        label_w      = self.PANEL_LABEL_W
        panel_w      = self.PANEL_W
        panel_h      = self.PANEL_H

        bg = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        bg.fill((20, 20, 30, 190))
        surface.blit(bg, (x, y))

        for i, name in enumerate(self.RESOURCES):
            val   = getattr(self, name)
            row_y = y + padding + i * (bar_h + padding)

            label = font.render(self.DISPLAY_NAMES[name], True, self.LABEL_COLOURS[name])
            surface.blit(label, (x + 6, row_y + 1))

            bar_x = x + label_w
            pygame.draw.rect(surface, (50, 50, 60), (bar_x, row_y, bar_w, bar_h), border_radius=3)
            fill = min(int(bar_w * (val / self.MAXES[name])), bar_w)
            if fill > 0:
                pygame.draw.rect(surface, self.COLOURS[name], (bar_x, row_y, fill, bar_h), border_radius=3)
            pygame.draw.rect(surface, (100, 100, 120), (bar_x, row_y, bar_w, bar_h), 1, border_radius=3)

            num_text = f"{val:.0f}%" if name == "protection" else f"{val:.0f}"
            num = font.render(num_text, True, (220, 220, 220))
            surface.blit(num, (bar_x + bar_w + 4, row_y + 1))
