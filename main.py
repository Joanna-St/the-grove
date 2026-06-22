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
    draw_scene, draw_action_panel,
    draw_text_box, draw_center_flash, text_box_item_rects,
    draw_areas_panel,
    stirge_rect, stirge_pos,
    blink_dog_rect, blink_dog_pos,
    owlbear_rect, owlbear_pos,
    pseudodragon_rect, pseudodragon_pos,
    flumph_rect, flumph_pos,
    moss_wisp_rect, moss_wisp_pos,
    pixie_rect, pixie_pos,
    displacer_beast_rect, displacer_beast_pos,
    statue_rect, druid_rect,
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
                   fullscreen, game_w, game_h, areas):
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
        draw_scene(game_surf, "dawn", 0.05, game_w, game_h, areas=areas)

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


def render_keybinds(surface, font_sm, x, y, right_align=False):
    for i, line in enumerate(["[S] Save", "[D] Dev speed", "[R] Restore areas", "[ESC] Quit"]):
        t = font_sm.render(line, True, DIM)
        blit_x = x - t.get_width() if right_align else x
        surface.blit(t, (blit_x, y + i * 18))


def render_bond_status(surface, font_sm, creatures, x, y):
    for i, c in enumerate(creatures.present()):
        label    = c.name.replace("_", " ").title()
        bond     = "[" + "*" * c.bond_level + "-" * (3 - c.bond_level) + "]"
        flashing = c.bond_flash_ttl > 0
        colour   = (240, 230, 130) if flashing else (170, 195, 150)
        text     = font_sm.render(f"{label}  {bond}  {c.feed_indicator}", True, colour)
        surface.blit(text, (x, y + i * 18))


# ------------------------------------------------------------------
# Creature menu helpers

def _creature_menu_options(creature, resources, config):
    feed_cfg  = config["creatures"].get(creature.name, {}).get("feeding", {})
    feed_cost = feed_cfg.get("forage_cost", 3)
    can_feed  = creature.can_feed and resources.forage >= feed_cost
    options = [
        ("Interact", "",                   creature.can_interact),
        ("Feed",     f"-{feed_cost:.0f} forage", can_feed),
    ]
    if creature.has_event:
        options.append(("Event", "", True))
    return options


def _apply_creature_event(creature, resources):
    """Clears the creature's pending event, applies its reward, returns its text."""
    event = creature.pending_event
    for res, amount in event.get("reward", {}).items():
        if res == "bond":
            creature.bond_xp += amount
        else:
            resources.add(res, amount)
    creature.pending_event = None
    return event["text"]


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
    events    = Events(config)

    loaded, player_name = save_load.load_game(time_sys, resources, areas, creatures, events)

    if not loaded or not player_name:
        player_name = run_name_entry(screen, game_surf, clock, config,
                                     blit_x, blit_y, fullscreen, game_w, game_h, areas)
        save_load.save_game(time_sys, resources, areas, creatures, events, player_name)

    # Active action state
    action_cfg       = config["active_actions"]
    forage_cd        = 0.0
    tend_cd          = 0.0
    forage_cd_max    = action_cfg["forage"]["cooldown_real_seconds"]
    tend_cd_max      = action_cfg["tend_statue"]["cooldown_real_seconds"]

    text_box          = None   # {"mode":"options"|"text","speaker":str,"text":str,
                               #  "creature":c|None,"pool":...,"feed_pool":...,"ttl":float,"hover":int}
    show_areas_panel  = False
    areas_clickable   = {}     # {area_name: rect}, rebuilt each frame when panel is open

    autosave_interval   = config["autosave_interval_seconds"]
    last_autosave       = time.time()
    center_flash_text   = ""
    center_flash_ttl    = 0.0

    # Data-driven creature registry — drives click detection and dialogue routing
    _CREATURE_REGISTRY = [
        {"name": "stirge",          "pool": dlg.STIRGE,          "feed_pool": dlg.STIRGE_FEED,
         "rect_fn": stirge_rect,          "pos_fn": stirge_pos},
        {"name": "blink_dog",       "pool": dlg.BLINK_DOG,       "feed_pool": dlg.BLINK_DOG_FEED,
         "rect_fn": blink_dog_rect,       "pos_fn": blink_dog_pos},
        {"name": "owlbear",         "pool": dlg.OWLBEAR,         "feed_pool": dlg.OWLBEAR_FEED,
         "rect_fn": owlbear_rect,         "pos_fn": owlbear_pos},
        {"name": "pseudodragon",    "pool": dlg.PSEUDODRAGON,    "feed_pool": dlg.PSEUDODRAGON_FEED,
         "rect_fn": pseudodragon_rect,    "pos_fn": pseudodragon_pos},
        {"name": "flumph",          "pool": dlg.FLUMPH,          "feed_pool": dlg.FLUMPH_FEED,
         "rect_fn": flumph_rect,          "pos_fn": flumph_pos},
        {"name": "moss_wisp",       "pool": dlg.MOSS_WISP,       "feed_pool": dlg.MOSS_WISP_FEED,
         "rect_fn": moss_wisp_rect,       "pos_fn": moss_wisp_pos},
        {"name": "pixie",           "pool": dlg.PIXIE,           "feed_pool": dlg.PIXIE_FEED,
         "rect_fn": pixie_rect,           "pos_fn": pixie_pos},
        {"name": "displacer_beast", "pool": dlg.DISPLACER_BEAST, "feed_pool": dlg.DISPLACER_BEAST_FEED,
         "rect_fn": displacer_beast_rect, "pos_fn": displacer_beast_pos},
    ]

    st_rect = statue_rect(game_w, game_h)
    dr_rect = druid_rect(game_w, game_h)

    def _grove_text(text):
        return {"mode": "text", "speaker": "The Grove", "text": text,
                "creature": None, "pool": None, "feed_pool": None,
                "ttl": None, "hover": -1, "boxes": None, "box_idx": 0, "is_visitor": False}

    def _creature_text(creature):
        return {"mode": "text",
                "speaker": creature.name.replace("_", " ").title(),
                "text": creature.dialogue_text,
                "creature": None, "pool": None, "feed_pool": None,
                "ttl": None, "hover": -1, "boxes": None, "box_idx": 0, "is_visitor": False}

    def _event_text(creature, text):
        return {"mode": "text",
                "speaker": creature.name.replace("_", " ").title(),
                "text": text,
                "creature": None, "pool": None, "feed_pool": None,
                "ttl": None, "hover": -1, "boxes": None, "box_idx": 0, "is_visitor": False}

    def _visitor_text(text, speaker, boxes=None):
        return {"mode": "text", "speaker": speaker, "text": text,
                "creature": None, "pool": None, "feed_pool": None,
                "ttl": None, "hover": -1, "boxes": boxes, "box_idx": 0, "is_visitor": True}

    running = True
    while running:
        dt_real = clock.tick(win_cfg["fps"]) / 1000.0

        # ---- Events ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEMOTION:
                if text_box and text_box["mode"] == "options":
                    mx, my = event.pos
                    gx, gy = mx - blit_x, my - blit_y
                    opts  = _creature_menu_options(text_box["creature"], resources, config)
                    rects = text_box_item_rects(
                        font_sm, text_box["speaker"], len(opts), game_w, game_h)
                    text_box["hover"] = next(
                        (i for i, r in enumerate(rects) if r.collidepoint(gx, gy)), -1)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if show_areas_panel:
                        show_areas_panel = False
                    elif text_box and text_box["mode"] == "text":
                        boxes = text_box.get("boxes")
                        if boxes is not None and text_box["box_idx"] < len(boxes) - 1:
                            pass  # non-last box: ESC suppressed to hint there's more
                        else:
                            if text_box.get("is_visitor"):
                                events.advance_visitor(resources, time_sys.game_seconds)
                            text_box = None
                    elif text_box:
                        text_box = None
                    else:
                        running = False
                elif event.key == pygame.K_s:
                    save_load.save_game(time_sys, resources, areas, creatures, events, player_name)
                    center_flash_text, center_flash_ttl = "Saved.", 2.5
                elif event.key == pygame.K_r:
                    show_areas_panel = not show_areas_panel
                    if show_areas_panel:
                        action_menu = None
                elif event.key == pygame.K_d:
                    time_sys.toggle_dev_speed()
                elif event.key == pygame.K_f:
                    if forage_cd <= 0:
                        fc  = action_cfg["forage"]
                        resources.add("forage",    fc["forage_yield"])
                        resources.add("heartwood", fc["heartwood_yield"])
                        if random.random() < fc["glamour_chance"]:
                            resources.add("glamour", fc["glamour_yield"])
                        forage_cd = forage_cd_max
                        text_box  = _grove_text(dlg.pick(dlg.FORAGE))
                elif event.key == pygame.K_t:
                    tc = action_cfg["tend_statue"]
                    if tend_cd <= 0 and resources.glamour >= tc["glamour_cost"]:
                        resources.add("glamour",    -tc["glamour_cost"])
                        resources.add("protection",  tc["protection_restore"])
                        tend_cd  = tend_cd_max
                        text_box = _grove_text(dlg.pick(dlg.TEND_STATUE))
                    elif tend_cd <= 0:
                        center_flash_text = "Not enough glamour to tend the statue."
                        center_flash_ttl  = 3.0

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Translate screen click → game_surf coordinates
                mx, my = event.pos
                gx, gy = mx - blit_x, my - blit_y

                if show_areas_panel:
                    for area_name, rect in areas_clickable.items():
                        if rect.collidepoint(gx, gy):
                            if areas.can_afford(area_name, resources):
                                for res, amount in areas.unlock_cost(area_name).items():
                                    resources.add(res, -amount)
                                areas.unlock(area_name, time_sys.game_seconds)
                                msg      = dlg.AREA_RESTORED.get(area_name,
                                    f"The {area_name.replace('_',' ').title()} has been restored.")
                                text_box         = _grove_text(msg)
                                show_areas_panel = False
                            else:
                                center_flash_text = "Not enough resources."
                                center_flash_ttl  = 3.0
                            break

                elif text_box and text_box["mode"] == "options":
                    creature = text_box["creature"]
                    opts  = _creature_menu_options(creature, resources, config)
                    rects = text_box_item_rects(
                        font_sm, text_box["speaker"], len(opts), game_w, game_h)
                    acted = False
                    for r, (label, _, available) in zip(rects, opts):
                        if r.collidepoint(gx, gy) and available:
                            if label == "Interact":
                                creature.interact(text_box["pool"])
                                text_box = _creature_text(creature)
                            elif label == "Feed":
                                feed_cfg = config["creatures"].get(creature.name, {}).get("feeding", {})
                                resources.add("forage", -feed_cfg["forage_cost"])
                                creature.feed(text_box["feed_pool"])
                                text_box = _creature_text(creature)
                            elif label == "Event":
                                text = _apply_creature_event(creature, resources)
                                text_box = _event_text(creature, text)
                            acted = True
                            break
                    if not acted:
                        text_box = None   # click outside options → dismiss

                elif text_box and text_box["mode"] == "text":
                    boxes = text_box.get("boxes")
                    if boxes is not None and text_box["box_idx"] < len(boxes) - 1:
                        text_box["box_idx"] += 1
                        text_box["text"] = boxes[text_box["box_idx"]]
                    else:
                        if text_box.get("is_visitor"):
                            events.advance_visitor(resources, time_sys.game_seconds)
                        text_box = None

                else:
                    # Check creature clicks (data-driven)
                    clicked_creature = False
                    for entry in _CREATURE_REGISTRY:
                        c = creatures.get(entry["name"])
                        if c and c.is_present and entry["rect_fn"](game_w, game_h).collidepoint(gx, gy):
                            text_box = {
                                "mode":       "options",
                                "speaker":    c.name.replace("_", " ").title(),
                                "text":       "",
                                "creature":   c,
                                "pool":       entry["pool"],
                                "feed_pool":  entry["feed_pool"],
                                "ttl":        None,
                                "hover":      -1,
                                "boxes":      None,
                                "box_idx":    0,
                                "is_visitor": False,
                            }
                            clicked_creature = True
                            break

                    if not clicked_creature and st_rect.collidepoint(gx, gy):
                        if events.grove_pending_event:
                            text_box = _grove_text(events.grove_pending_event["text"])
                            events.grove_pending_event = None
                        elif tend_cd <= 0:
                            tc = action_cfg["tend_statue"]
                            if resources.glamour >= tc["glamour_cost"]:
                                resources.add("glamour",    -tc["glamour_cost"])
                                resources.add("protection",  tc["protection_restore"])
                                tend_cd  = tend_cd_max
                                text_box = _grove_text(dlg.pick(dlg.TEND_STATUE))
                            else:
                                center_flash_text = "Not enough glamour to tend the statue."
                                center_flash_ttl  = 3.0

                    elif (not clicked_creature and events.visitor_pending_event
                          and dr_rect.collidepoint(gx, gy)):
                        boxes    = events.visitor_pending_event["boxes"]
                        text_box = _visitor_text(boxes[0], events.visitor_display_name(), boxes)

        # ---- Update ----
        time_sys.update(dt_real)
        eff_mult = config["time"]["dev_speed_multiplier"] if time_sys.dev_speed else 1.0
        dt_game  = dt_real * eff_mult

        resources.tick(dt_real, dt_game, areas)
        creatures.update(dt_real, dt_game, time_sys.game_seconds, time_sys.day_number, areas, resources, events)
        events.update(dt_real, areas, creatures, time_sys)

        if forage_cd > 0: forage_cd -= dt_real
        if tend_cd   > 0: tend_cd   -= dt_real

        if center_flash_ttl > 0:
            center_flash_ttl -= dt_real
        else:
            center_flash_text = ""

        if text_box and text_box["mode"] == "text" and text_box.get("ttl") is not None:
            text_box["ttl"] -= dt_real
            if text_box["ttl"] <= 0:
                text_box = None

        now = time.time()
        if now - last_autosave >= autosave_interval:
            save_load.save_game(time_sys, resources, areas, creatures, events, player_name)
            last_autosave = now

        # ---- Render ----
        draw_scene(game_surf, time_sys.period, time_sys.time_of_day,
                   game_w, game_h, creatures, events, areas)

        # Title + player name
        title = font_lg.render("The Grove", True, (200, 230, 180))
        game_surf.blit(title, (20, 16))
        render_player_name(game_surf, font_sm, player_name,
                           game_w - font_sm.size(player_name)[0] - 14, 18)

        # Resource bars
        resources.render(game_surf, font, 20, 46)

        # Time HUD (bar + "Day N — Period" label)
        # Resource panel: 4 rows × 32px + 10px padding = 138px, starts at y=46 → ends at 184
        render_time_hud(game_surf, font_sm, time_sys, 20, 196)

        # Bond status — below time label (label is at 196+16=212)
        bond_y = 232
        render_bond_status(game_surf, font_sm, creatures, 20, bond_y)

        # Dev badge sits below the last bond line
        bond_end_y = bond_y + max(len(creatures.present()), 1) * 18
        if time_sys.dev_speed:
            render_dev_badge(game_surf, font_sm, 20, bond_end_y + 6)

        # Areas restoration panel
        if show_areas_panel:
            areas_clickable = draw_areas_panel(
                game_surf, font, font_sm, areas, resources, game_w, game_h)

        # Bottom text box (creature options / dialogue / grove messages)
        if text_box:
            opts = (_creature_menu_options(text_box["creature"], resources, config)
                    if text_box["mode"] == "options" else [])
            draw_text_box(game_surf, font, font_sm,
                          text_box["speaker"], text_box["text"],
                          opts, text_box["hover"], game_w, game_h)

        # Centre flash (errors, save confirmation)
        if center_flash_ttl > 0:
            alpha = int(255 * min(1.0, center_flash_ttl))
            draw_center_flash(game_surf, font_sm, center_flash_text, alpha, game_w, game_h)

        # Action panel — anchored above the text box
        forage_avail = forage_cd <= 0
        tend_avail   = tend_cd   <= 0
        draw_action_panel(game_surf, font_sm, game_w, game_h, [
            ("Forage",       "[F]", forage_cd / forage_cd_max if forage_cd > 0 else 0.0, forage_avail),
            ("Tend Statue",  "[T]", tend_cd   / tend_cd_max   if tend_cd   > 0 else 0.0, tend_avail),
        ], bottom=game_h - 120 - 12)

        # Keybinds — top-right, below player name
        render_keybinds(game_surf, font_sm, game_w - 14, 36, right_align=True)

        if fullscreen:
            screen.fill((0, 0, 0))
            screen.blit(game_surf, (blit_x, blit_y))

        pygame.display.flip()

    save_load.save_game(time_sys, resources, areas, creatures, events, player_name)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
