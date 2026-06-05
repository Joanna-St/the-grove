import json
import os
import random
import sys
import time

import pygame

from game.time_system import TimeSystem
from game.resources import ResourceTracker
from game.areas import Areas
from game.creatures import Creatures
from game.events import Events
from game import save_load
from game import dialogue as dlg
from game.renderer import (
    draw_scene, draw_dialogue, draw_action_panel,
    stirge_rect, blink_dog_rect, statue_rect,
    stirge_pos, blink_dog_pos,
)

CONFIG_PATH = "config.json"


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


# ------------------------------------------------------------------
# Colours

WHITE = (230, 230, 230)
DIM   = (120, 120, 120)


# ------------------------------------------------------------------
# Name entry screen

def run_name_entry(screen, game_surf, clock, config, blit_x, blit_y,
                   fullscreen, game_w, game_h):
    font    = pygame.font.SysFont("Consolas", 15)
    font_lg = pygame.font.SysFont("Consolas", 22, bold=True)
    name    = ""

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode and event.unicode.isprintable() and len(name) < 20:
                    name += event.unicode

        # Background: always dawn for the opening screen
        draw_scene(game_surf, "dawn", 0.05, game_w, game_h)

        pw, ph = 420, 170
        px = (game_w - pw) // 2
        py = (game_h - ph) // 2

        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel.fill((12, 22, 12, 215))
        game_surf.blit(panel, (px, py))
        pygame.draw.rect(game_surf, (60, 90, 55), (px, py, pw, ph), 1)

        title = font_lg.render("The Grove", True, (190, 225, 170))
        game_surf.blit(title, (px + (pw - title.get_width()) // 2, py + 18))

        prompt = font.render("What is your name, druid?", True, (165, 200, 150))
        game_surf.blit(prompt, (px + (pw - prompt.get_width()) // 2, py + 60))

        fw = 300
        fx = px + (pw - fw) // 2
        fy = py + 95
        pygame.draw.rect(game_surf, (30, 48, 28), (fx, fy, fw, 30), border_radius=3)
        pygame.draw.rect(game_surf, (75, 105, 65), (fx, fy, fw, 30), 1, border_radius=3)

        cursor  = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
        display = font.render(name + cursor, True, (215, 230, 205))
        game_surf.blit(display, (fx + 10, fy + 7))

        if name.strip():
            hint = font.render("Press Enter to begin", True, (110, 145, 90))
            game_surf.blit(hint, (px + (pw - hint.get_width()) // 2, py + 143))

        if fullscreen:
            screen.fill((0, 0, 0))
            screen.blit(game_surf, (blit_x, blit_y))
        pygame.display.flip()


# ------------------------------------------------------------------
# HUD helpers

def render_resource_hud(surface, font, font_sm, resources, x, y):
    resources.render(surface, font, x, y)


def render_time_hud(surface, font_sm, time_sys, x, y):
    period = time_sys.period
    tod    = time_sys.time_of_day

    bar_w = 200
    pygame.draw.rect(surface, (40, 40, 50), (x, y, bar_w, 12), border_radius=6)
    fill = int(bar_w * tod)
    arc_col = {"dawn": (230, 160, 80), "day": (220, 200, 100),
               "dusk": (200, 100, 50), "night": (60, 60, 130)}[period]
    if fill > 0:
        pygame.draw.rect(surface, arc_col, (x, y, fill, 12), border_radius=6)
    pygame.draw.rect(surface, (80, 80, 90), (x, y, bar_w, 12), 1, border_radius=6)

    label = font_sm.render(f"Day {time_sys.day_number}  —  {period.capitalize()}",
                           True, WHITE)
    surface.blit(label, (x, y + 16))


def render_player_name(surface, font_sm, name, x, y):
    if name:
        t = font_sm.render(name, True, (160, 195, 140))
        surface.blit(t, (x, y))


def render_dev_badge(surface, font_sm, x, y):
    badge = font_sm.render("DEV SPEED  [D]", True, (255, 220, 60))
    surface.blit(badge, (x, y))


def render_flash(surface, font_sm, text, x, y, alpha):
    msg = font_sm.render(text, True, (160, 220, 160))
    msg.set_alpha(alpha)
    surface.blit(msg, (x, y))


def render_keybinds(surface, font_sm, x, y):
    for i, line in enumerate(["[S] Save", "[D] Dev speed", "[ESC] Quit"]):
        t = font_sm.render(line, True, DIM)
        surface.blit(t, (x, y + i * 18))


def render_bond_status(surface, font_sm, creatures, x, y):
    for i, c in enumerate(creatures.present()):
        label   = c.name.replace("_", " ").title()
        bond    = "[" + "*" * c.bond_level + "-" * (3 - c.bond_level) + "]"
        flashing = c.bond_flash_ttl > 0
        colour  = (240, 230, 130) if flashing else (170, 195, 150)
        text    = font_sm.render(f"{label}  {bond}", True, colour)
        surface.blit(text, (x, y + i * 18))


# ------------------------------------------------------------------
# Main

def main():
    config  = load_config()
    win_cfg = config["window"]

    game_w, game_h = win_cfg["width"], win_cfg["height"]
    fullscreen      = win_cfg.get("fullscreen", False)

    pygame.init()
    if fullscreen:
        info = pygame.display.Info()
        os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"
        screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME)
        blit_x = (info.current_w - game_w) // 2
        blit_y = (info.current_h - game_h) // 2
        game_surf = pygame.Surface((game_w, game_h))
    else:
        screen    = pygame.display.set_mode((game_w, game_h))
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
    creatures = Creatures(config)
    events    = Events()

    loaded, player_name = save_load.load_game(time_sys, resources, areas, creatures)

    if not loaded or not player_name:
        player_name = run_name_entry(screen, game_surf, clock, config,
                                     blit_x, blit_y, fullscreen, game_w, game_h)
        save_load.save_game(time_sys, resources, areas, creatures, player_name)

    # Active action state
    action_cfg       = config["active_actions"]
    forage_cd        = 0.0
    tend_cd          = 0.0
    forage_cd_max    = action_cfg["forage"]["cooldown_real_seconds"]
    tend_cd_max      = action_cfg["tend_statue"]["cooldown_real_seconds"]

    autosave_interval = config["autosave_interval_seconds"]
    last_autosave     = time.time()
    flash_text        = ""
    flash_ttl         = 0.0

    # Clickable rects (in game_surf coordinates)
    s_rect  = stirge_rect(game_w, game_h)
    bd_rect = blink_dog_rect(game_w, game_h)
    st_rect = statue_rect(game_w, game_h)

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
                    save_load.save_game(time_sys, resources, areas, creatures, player_name)
                    flash_text, flash_ttl = "Saved.", 2.5
                elif event.key == pygame.K_d:
                    time_sys.toggle_dev_speed()
                elif event.key == pygame.K_f:
                    if forage_cd <= 0:
                        fc  = action_cfg["forage"]
                        resources.add("forage",    fc["forage_yield"])
                        resources.add("heartwood", fc["heartwood_yield"])
                        if random.random() < fc["glamour_chance"]:
                            resources.add("glamour", fc["glamour_yield"])
                        forage_cd  = forage_cd_max
                        flash_text = dlg.pick(dlg.FORAGE)
                        flash_ttl  = 4.0
                elif event.key == pygame.K_t:
                    if tend_cd <= 0:
                        resources.add("glamour", action_cfg["tend_statue"]["glamour_yield"])
                        tend_cd    = tend_cd_max
                        flash_text = dlg.pick(dlg.TEND_STATUE)
                        flash_ttl  = 4.0

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Translate screen click → game_surf coordinates
                mx, my = event.pos
                gx, gy = mx - blit_x, my - blit_y

                stirge    = creatures.get("stirge")
                blink_dog = creatures.get("blink_dog")

                if stirge and s_rect.collidepoint(gx, gy) and stirge.can_interact:
                    levelled = stirge.interact(dlg.STIRGE)
                    if levelled:
                        flash_text = stirge.dialogue_text
                        flash_ttl  = 5.0

                elif blink_dog and bd_rect.collidepoint(gx, gy) and blink_dog.can_interact:
                    levelled = blink_dog.interact(dlg.BLINK_DOG)
                    if levelled:
                        flash_text = blink_dog.dialogue_text
                        flash_ttl  = 5.0

                elif st_rect.collidepoint(gx, gy) and tend_cd <= 0:
                    resources.add("glamour", action_cfg["tend_statue"]["glamour_yield"])
                    tend_cd    = tend_cd_max
                    flash_text = dlg.pick(dlg.TEND_STATUE)
                    flash_ttl  = 4.0

        # ---- Update ----
        time_sys.update(dt_real)
        eff_mult = config["time"]["dev_speed_multiplier"] if time_sys.dev_speed else 1.0
        dt_game  = dt_real * eff_mult

        resources.tick(dt_game, areas)
        creatures.update(dt_real, dt_game, time_sys.game_seconds, resources)
        events.update(dt_game)

        if forage_cd > 0: forage_cd -= dt_real
        if tend_cd   > 0: tend_cd   -= dt_real
        if flash_ttl > 0: flash_ttl -= dt_real
        else:             flash_text  = ""

        now = time.time()
        if now - last_autosave >= autosave_interval:
            save_load.save_game(time_sys, resources, areas, creatures, player_name)
            last_autosave = now

        # ---- Render ----
        draw_scene(game_surf, time_sys.period, time_sys.time_of_day,
                   game_w, game_h, creatures)

        # Title + player name
        title = font_lg.render("The Grove", True, (200, 230, 180))
        game_surf.blit(title, (20, 16))
        render_player_name(game_surf, font_sm, player_name,
                           game_w - font_sm.size(player_name)[0] - 14, 18)

        # Resource bars
        resources.render(game_surf, font, 20, 46)

        # Time HUD (bar + "Day N — Period" label)
        render_time_hud(game_surf, font_sm, time_sys, 20, 158)

        # Bond status — starts safely below the time label (label is at 158+16=174)
        render_bond_status(game_surf, font_sm, creatures, 20, 192)

        # Dev speed badge
        if time_sys.dev_speed:
            render_dev_badge(game_surf, font_sm, 20, 232)

        # Flash message (event text / save confirmation)
        if flash_ttl > 0:
            alpha = int(255 * min(1.0, flash_ttl))
            render_flash(game_surf, font_sm, flash_text, 20, 252, alpha)

        # Creature dialogue bubbles
        stirge    = creatures.get("stirge")
        blink_dog = creatures.get("blink_dog")

        if stirge and stirge.dialogue_text and stirge.dialogue_ttl > 0:
            sx, sy = stirge_pos(game_w, game_h)
            draw_dialogue(game_surf, font_sm, stirge.dialogue_text, sx, sy - 16)

        if blink_dog and blink_dog.dialogue_text and blink_dog.dialogue_ttl > 0:
            bx, by = blink_dog_pos(game_w, game_h)
            draw_dialogue(game_surf, font_sm, blink_dog.dialogue_text, bx, by - 18)

        # Action panel
        forage_avail = forage_cd <= 0
        tend_avail   = tend_cd   <= 0
        draw_action_panel(game_surf, font_sm, game_w, game_h, [
            ("Forage",       "[F]", forage_cd / forage_cd_max if forage_cd > 0 else 0.0, forage_avail),
            ("Tend Statue",  "[T]", tend_cd   / tend_cd_max   if tend_cd   > 0 else 0.0, tend_avail),
        ])

        # Keybinds
        render_keybinds(game_surf, font_sm, 20, game_h - 60)

        if fullscreen:
            screen.fill((0, 0, 0))
            screen.blit(game_surf, (blit_x, blit_y))

        pygame.display.flip()

    save_load.save_game(time_sys, resources, areas, creatures, player_name)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
