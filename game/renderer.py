"""
Phase 1.5 — coded placeholder visuals.
All shapes are geometric stand-ins; no image files.
Replace individual draw_* functions with sprite blits when art is ready.
"""

import pygame
import math


# ------------------------------------------------------------------
# Palette by period

SKY_COLOURS = {
    "dawn":  [(60, 35, 50), (180, 90, 60)],
    "day":   [(30, 60, 100), (90, 140, 180)],
    "dusk":  [(80, 30, 20), (200, 100, 40)],
    "night": [(8, 8, 25), (18, 18, 50)],
}

GROUND_COLOURS = {
    "dawn":  (28, 38, 22),
    "day":   (34, 52, 28),
    "dusk":  (30, 36, 20),
    "night": (14, 20, 14),
}

TREE_COLOURS = {
    "dawn":  (20, 30, 18),
    "day":   (22, 42, 20),
    "dusk":  (18, 26, 14),
    "night": (10, 16, 10),
}


def _lerp_colour(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def _gradient_rect(surface, top_colour, bot_colour, rect):
    x, y, w, h = rect
    for row in range(h):
        t = row / max(h - 1, 1)
        pygame.draw.line(surface, _lerp_colour(top_colour, bot_colour, t),
                         (x, y + row), (x + w - 1, y + row))


# ------------------------------------------------------------------
# Background

def draw_background(surface, period, screen_w, screen_h):
    sky_h = int(screen_h * 0.58)
    sky_cols = SKY_COLOURS[period]
    _gradient_rect(surface, sky_cols[0], sky_cols[1], (0, 0, screen_w, sky_h))

    ground_col = GROUND_COLOURS[period]
    _gradient_rect(surface, ground_col,
                   _lerp_colour(ground_col, (0, 0, 0), 0.4),
                   (0, sky_h, screen_w, screen_h - sky_h))


# ------------------------------------------------------------------
# Trees (silhouette triangles along the edges)

def draw_trees(surface, period, screen_w, screen_h):
    col = TREE_COLOURS[period]
    sky_h = int(screen_h * 0.58)
    horizon = sky_h

    left_trees = [
        (0,   horizon - 160, 70,  260),
        (45,  horizon - 210, 80,  290),
        (90,  horizon - 180, 65,  270),
        (130, horizon - 230, 90,  300),
        (170, horizon - 190, 70,  270),
    ]
    right_trees = [
        (screen_w,       horizon - 170, -75,  270),
        (screen_w - 50,  horizon - 220, -85,  295),
        (screen_w - 100, horizon - 185, -70,  275),
        (screen_w - 145, horizon - 240, -95,  305),
        (screen_w - 190, horizon - 195, -72,  278),
    ]

    for bx, by, dx, height in left_trees + right_trees:
        tip   = (bx + dx // 2, by)
        left  = (bx,           by + height)
        right = (bx + dx,      by + height)
        pygame.draw.polygon(surface, col, [tip, left, right])

    # Underbrush strip at horizon
    brush_col = _lerp_colour(col, GROUND_COLOURS[period], 0.3)
    pygame.draw.rect(surface, brush_col, (0, horizon - 12, screen_w, 20))


# ------------------------------------------------------------------
# Heartstone clearing — oval of lighter ground + moss details

def draw_clearing(surface, period, screen_w, screen_h):
    cx = screen_w // 2
    cy = int(screen_h * 0.72)

    base = GROUND_COLOURS[period]
    clearing_col = _lerp_colour(base, (60, 90, 40), 0.25)
    pygame.draw.ellipse(surface, clearing_col, (cx - 200, cy - 50, 400, 100))

    # Scattered moss spots
    moss_col = _lerp_colour(clearing_col, (50, 110, 40), 0.4)
    spots = [(-90, 10, 22, 8), (60, 20, 18, 6), (-30, -18, 14, 5),
             (110, -5, 20, 7), (-140, -10, 16, 6)]
    for ox, oy, rw, rh in spots:
        pygame.draw.ellipse(surface, moss_col, (cx + ox - rw, cy + oy - rh, rw * 2, rh * 2))


# ------------------------------------------------------------------
# Silvanus statue — stylised stone figure

def draw_statue(surface, period, screen_w, screen_h):
    cx = screen_w // 2
    base_y = int(screen_h * 0.68)

    stone = (90, 85, 80)
    shadow = (55, 52, 48)
    moss   = (60, 90, 55)

    # Base plinth
    pygame.draw.rect(surface, shadow, (cx - 26, base_y - 4, 52, 12))
    pygame.draw.rect(surface, stone,  (cx - 22, base_y - 8, 44, 12))

    # Column / body
    pygame.draw.rect(surface, shadow, (cx - 14, base_y - 68, 28, 62))
    pygame.draw.rect(surface, stone,  (cx - 12, base_y - 70, 24, 62))

    # Arms outstretched
    pygame.draw.rect(surface, stone, (cx - 36, base_y - 58, 24, 8))
    pygame.draw.rect(surface, stone, (cx + 12, base_y - 58, 24, 8))

    # Head / circle
    pygame.draw.circle(surface, shadow, (cx + 1, base_y - 80), 13)
    pygame.draw.circle(surface, stone,  (cx,     base_y - 80), 12)

    # Moss accent near base
    pygame.draw.ellipse(surface, moss, (cx - 14, base_y - 14, 28, 8))

    # Faint glow if glamour is high (placeholder — always on for now)
    glow = pygame.Surface((80, 80), pygame.SRCALPHA)
    pygame.draw.circle(glow, (140, 110, 200, 28), (40, 40), 38)
    surface.blit(glow, (cx - 40, base_y - 110))


# ------------------------------------------------------------------
# Druid figure — hooded silhouette

def draw_druid(surface, period, screen_w, screen_h):
    dx = int(screen_w * 0.34)
    dy = int(screen_h * 0.60)

    robe  = (45, 55, 42)
    hood  = (35, 44, 32)
    skin  = (170, 135, 105)
    leaf  = (60, 100, 50)

    # Robe (trapezoid)
    robe_pts = [(dx - 14, dy), (dx + 14, dy),
                (dx + 20, dy + 70), (dx - 20, dy + 70)]
    pygame.draw.polygon(surface, robe, robe_pts)

    # Arms
    pygame.draw.line(surface, robe, (dx - 10, dy + 10), (dx - 26, dy + 38), 7)
    pygame.draw.line(surface, robe, (dx + 10, dy + 10), (dx + 26, dy + 38), 7)

    # Hands
    pygame.draw.circle(surface, skin, (dx - 26, dy + 40), 5)
    pygame.draw.circle(surface, skin, (dx + 26, dy + 40), 5)

    # Neck + face
    pygame.draw.rect(surface, skin, (dx - 5, dy - 10, 10, 12))
    pygame.draw.circle(surface, skin, (dx, dy - 16), 11)

    # Hood
    hood_pts = [(dx - 18, dy + 4), (dx + 18, dy + 4),
                (dx + 10, dy - 8), (dx, dy - 30), (dx - 10, dy - 8)]
    pygame.draw.polygon(surface, hood, hood_pts)

    # Leaf detail on robe
    pygame.draw.ellipse(surface, leaf, (dx - 5, dy + 20, 10, 18))
    pygame.draw.ellipse(surface, leaf, (dx + 2, dy + 28, 8, 14))


# ------------------------------------------------------------------
# Ambient: fireflies / motes (night and dusk only)

_motes = [(i * 137 % 700 + 162, i * 97 % 300 + 200) for i in range(18)]

def draw_motes(surface, period, time_of_day, screen_w, screen_h):
    if period not in ("night", "dusk"):
        return
    alpha = 180 if period == "night" else 80
    t = time_of_day * math.pi * 2
    for i, (mx, my) in enumerate(_motes):
        flicker = 0.5 + 0.5 * math.sin(t * (1.2 + i * 0.17) + i)
        a = int(alpha * flicker)
        r = int(2 + flicker * 2)
        glow = pygame.Surface((r * 6, r * 6), pygame.SRCALPHA)
        pygame.draw.circle(glow, (200, 230, 160, a), (r * 3, r * 3), r * 3)
        pygame.draw.circle(glow, (240, 255, 200, min(255, a + 60)), (r * 3, r * 3), r)
        surface.blit(glow, (mx - r * 3, my - r * 3))


# ------------------------------------------------------------------
# Master scene draw (call once per frame before HUD)

def draw_scene(surface, period, time_of_day, screen_w, screen_h):
    draw_background(surface, period, screen_w, screen_h)
    draw_trees(surface, period, screen_w, screen_h)
    draw_clearing(surface, period, screen_w, screen_h)
    draw_statue(surface, period, screen_w, screen_h)
    draw_druid(surface, period, screen_w, screen_h)
    draw_motes(surface, period, time_of_day, screen_w, screen_h)
