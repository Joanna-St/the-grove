import json
import os
import sys
import time

import pygame

from game.time_system import TimeSystem
from game.resources import ResourceTracker
from game.areas import Areas
from game.creatures import Creatures
from game.events import Events
from game import save_load
from game.renderer import draw_scene

CONFIG_PATH = "config.json"


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


# ------------------------------------------------------------------
# Colours

WHITE = (230, 230, 230)
DIM   = (120, 120, 120)


# ------------------------------------------------------------------
# HUD helpers

def render_time_hud(surface, font_sm, time_sys, x, y):
    period = time_sys.period
    day    = time_sys.day_number
    tod    = time_sys.time_of_day

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
    badge = font_sm.render("DEV SPEED  [D]", True, (255, 220, 60))
    surface.blit(badge, (x, y))


def render_keybinds(surface, font_sm, x, y):
    lines = ["[S] Save", "[D] Dev speed", "[ESC] Quit"]
    for i, line in enumerate(lines):
        t = font_sm.render(line, True, DIM)
        surface.blit(t, (x, y + i * 18))


def render_save_flash(surface, font_sm, x, y, alpha):
    msg = font_sm.render("Saved.", True, (160, 220, 160))
    msg.set_alpha(alpha)
    surface.blit(msg, (x, y))


# ------------------------------------------------------------------
# Main

def main():
    config = load_config()
    win_cfg = config["window"]

    game_w, game_h = win_cfg["width"], win_cfg["height"]
    fullscreen = win_cfg.get("fullscreen", False)

    # Must read desktop resolution before any set_mode call
    pygame.init()
    if fullscreen:
        info = pygame.display.Info()
        os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'
        screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME)
        blit_x = (info.current_w - game_w) // 2
        blit_y = (info.current_h - game_h) // 2
        game_surf = pygame.Surface((game_w, game_h))
    else:
        screen = pygame.display.set_mode((game_w, game_h))
        game_surf = screen
        blit_x = blit_y = 0

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
    save_flash_ttl    = 0.0

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
        eff_mult = config["time"]["dev_speed_multiplier"] if time_sys.dev_speed else 1.0
        dt_game  = dt_real * eff_mult
        resources.tick(dt_game, areas)
        events.update(dt_game)

        if save_flash_ttl > 0:
            save_flash_ttl -= dt_real

        now = time.time()
        if now - last_autosave >= autosave_interval:
            save_load.save_game(time_sys, resources, areas, creatures)
            last_autosave = now

        # ---- Render ----
        draw_scene(game_surf, time_sys.period, time_sys.time_of_day, game_w, game_h)

        title = font_lg.render("The Grove", True, (200, 230, 180))
        game_surf.blit(title, (20, 20))

        resources.render(game_surf, font, 20, 50)
        render_time_hud(game_surf, font_sm, time_sys, 20, 200)

        if time_sys.dev_speed:
            render_dev_badge(game_surf, font_sm, 20, 230)

        if save_flash_ttl > 0:
            alpha = int(255 * min(1.0, save_flash_ttl))
            render_save_flash(game_surf, font_sm, 20, 250, alpha)

        render_keybinds(game_surf, font_sm, 20, game_h - 60)

        if fullscreen:
            screen.fill((0, 0, 0))
            screen.blit(game_surf, (blit_x, blit_y))

        pygame.display.flip()

    save_load.save_game(time_sys, resources, areas, creatures)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
