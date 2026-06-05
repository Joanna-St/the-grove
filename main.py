import json
import sys
import time

import pygame

from game.time_system import TimeSystem
from game.resources import ResourceTracker
from game.areas import Areas
from game.creatures import Creatures
from game.events import Events
from game import save_load

CONFIG_PATH = "config.json"


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


# ------------------------------------------------------------------
# Colours

BG_DARK  = (18, 22, 18)
BG_PANEL = (28, 36, 28)
WHITE    = (230, 230, 230)
DIM      = (120, 120, 120)
GOLD     = (200, 170,  80)

PERIOD_TINTS = {
    "dawn":  (40, 30, 20),
    "day":   (20, 35, 20),
    "dusk":  (40, 20, 10),
    "night": (10, 10, 30),
}


# ------------------------------------------------------------------
# HUD helpers

def render_time_hud(surface, font_sm, time_sys, x, y):
    import pygame
    period = time_sys.period
    day    = time_sys.day_number
    tod    = time_sys.time_of_day

    # Day arc bar
    bar_w = 200
    pygame.draw.rect(surface, (40, 40, 50), (x, y, bar_w, 12), border_radius=6)
    fill = int(bar_w * tod)
    arc_col = {"dawn": (230, 160, 80), "day": (220, 200, 100),
                "dusk": (200, 100, 50), "night": (60, 60, 130)}[period]
    if fill > 0:
        pygame.draw.rect(surface, arc_col, (x, y, fill, 12), border_radius=6)
    pygame.draw.rect(surface, (80, 80, 90), (x, y, bar_w, 12), 1, border_radius=6)

    label = font_sm.render(f"Day {day}  —  {period.capitalize()}", True, WHITE)
    surface.blit(label, (x, y + 16))


def render_dev_badge(surface, font_sm, x, y):
    import pygame
    badge = font_sm.render("DEV SPEED  [D]", True, (255, 220, 60))
    surface.blit(badge, (x, y))


def render_keybinds(surface, font_sm, x, y):
    lines = ["[S] Save", "[D] Dev speed", "[ESC] Quit"]
    for i, line in enumerate(lines):
        t = font_sm.render(line, True, DIM)
        surface.blit(t, (x, y + i * 18))


def render_save_flash(surface, font_sm, x, y, alpha):
    import pygame
    msg = font_sm.render("Saved.", True, (160, 220, 160))
    msg.set_alpha(alpha)
    surface.blit(msg, (x, y))


# ------------------------------------------------------------------
# Main

def main():
    config = load_config()
    win_cfg = config["window"]

    pygame.init()
    screen = pygame.display.set_mode((win_cfg["width"], win_cfg["height"]))
    pygame.display.set_caption(win_cfg["title"])
    clock = pygame.time.Clock()

    font    = pygame.font.SysFont("Consolas", 15)
    font_sm = pygame.font.SysFont("Consolas", 13)
    font_lg = pygame.font.SysFont("Consolas", 20, bold=True)

    time_sys  = TimeSystem(config)
    resources = ResourceTracker(config)
    areas     = Areas(config)
    creatures = Creatures()
    events    = Events()

    save_load.load_game(time_sys, resources, areas, creatures)

    autosave_interval = config["autosave_interval_seconds"]
    last_autosave     = time.time()
    save_flash_ttl    = 0.0     # seconds remaining to show flash

    running = True
    while running:
        dt_real = clock.tick(win_cfg["fps"]) / 1000.0

        # ---- Events ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_s:
                    save_load.save_game(time_sys, resources, areas, creatures)
                    save_flash_ttl = 2.5
                elif event.key == pygame.K_d:
                    time_sys.toggle_dev_speed()

        # ---- Update ----
        time_sys.update(dt_real)
        eff_mult   = config["time"]["dev_speed_multiplier"] if time_sys.dev_speed else 1.0
        dt_game    = dt_real * eff_mult
        resources.tick(dt_game, areas)
        events.update(dt_game)

        if save_flash_ttl > 0:
            save_flash_ttl -= dt_real

        now = time.time()
        if now - last_autosave >= autosave_interval:
            save_load.save_game(time_sys, resources, areas, creatures)
            last_autosave = now

        # ---- Render ----
        tint = PERIOD_TINTS[time_sys.period]
        bg = tuple(max(0, BG_DARK[i] + tint[i]) for i in range(3))
        screen.fill(bg)

        # Title
        title = font_lg.render("The Grove", True, (160, 210, 140))
        screen.blit(title, (20, 20))

        # Resources panel
        resources.render(screen, font, 20, 60)

        # Time HUD
        render_time_hud(screen, font_sm, time_sys, 20, 210)

        # Dev speed badge
        if time_sys.dev_speed:
            render_dev_badge(screen, font_sm, 20, 240)

        # Save flash
        if save_flash_ttl > 0:
            alpha = int(255 * min(1.0, save_flash_ttl))
            render_save_flash(screen, font_sm, 20, 260, alpha)

        # Keybind hints (bottom-left)
        render_keybinds(screen, font_sm, 20, win_cfg["height"] - 60)

        pygame.display.flip()

    # Save on clean exit
    save_load.save_game(time_sys, resources, areas, creatures)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
