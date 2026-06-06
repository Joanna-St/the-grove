"""
Coded placeholder visuals — no image files.
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
# Trees

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

    brush_col = _lerp_colour(col, GROUND_COLOURS[period], 0.3)
    pygame.draw.rect(surface, brush_col, (0, horizon - 12, screen_w, 20))


# ------------------------------------------------------------------
# Heartstone clearing

def draw_clearing(surface, period, screen_w, screen_h):
    cx = screen_w // 2
    cy = int(screen_h * 0.72)

    base = GROUND_COLOURS[period]
    clearing_col = _lerp_colour(base, (60, 90, 40), 0.25)
    pygame.draw.ellipse(surface, clearing_col, (cx - 200, cy - 50, 400, 100))

    moss_col = _lerp_colour(clearing_col, (50, 110, 40), 0.4)
    spots = [(-90, 10, 22, 8), (60, 20, 18, 6), (-30, -18, 14, 5),
             (110, -5, 20, 7), (-140, -10, 16, 6)]
    for ox, oy, rw, rh in spots:
        pygame.draw.ellipse(surface, moss_col, (cx + ox - rw, cy + oy - rh, rw * 2, rh * 2))


# ------------------------------------------------------------------
# Silvanus statue

def draw_statue(surface, period, screen_w, screen_h):
    cx = screen_w // 2
    base_y = int(screen_h * 0.68)

    stone  = (90, 85, 80)
    shadow = (55, 52, 48)
    moss   = (60, 90, 55)

    pygame.draw.rect(surface, shadow, (cx - 26, base_y - 4,  52, 12))
    pygame.draw.rect(surface, stone,  (cx - 22, base_y - 8,  44, 12))
    pygame.draw.rect(surface, shadow, (cx - 14, base_y - 68, 28, 62))
    pygame.draw.rect(surface, stone,  (cx - 12, base_y - 70, 24, 62))
    pygame.draw.rect(surface, stone,  (cx - 36, base_y - 58, 24,  8))
    pygame.draw.rect(surface, stone,  (cx + 12, base_y - 58, 24,  8))
    pygame.draw.circle(surface, shadow, (cx + 1, base_y - 80), 13)
    pygame.draw.circle(surface, stone,  (cx,     base_y - 80), 12)
    pygame.draw.ellipse(surface, moss, (cx - 14, base_y - 14, 28, 8))

    glow = pygame.Surface((80, 80), pygame.SRCALPHA)
    pygame.draw.circle(glow, (140, 110, 200, 28), (40, 40), 38)
    surface.blit(glow, (cx - 40, base_y - 110))


def statue_rect(screen_w, screen_h):
    cx = screen_w // 2
    base_y = int(screen_h * 0.68)
    return pygame.Rect(cx - 38, base_y - 92, 76, 92)


# ------------------------------------------------------------------
# Druid figure

def draw_druid(surface, period, screen_w, screen_h):
    dx = int(screen_w * 0.34)
    dy = int(screen_h * 0.60)

    robe = (45, 55, 42)
    hood = (35, 44, 32)
    skin = (170, 135, 105)
    leaf = (60, 100, 50)

    robe_pts = [(dx - 14, dy), (dx + 14, dy),
                (dx + 20, dy + 70), (dx - 20, dy + 70)]
    pygame.draw.polygon(surface, robe, robe_pts)
    pygame.draw.line(surface, robe, (dx - 10, dy + 10), (dx - 26, dy + 38), 7)
    pygame.draw.line(surface, robe, (dx + 10, dy + 10), (dx + 26, dy + 38), 7)
    pygame.draw.circle(surface, skin, (dx - 26, dy + 40), 5)
    pygame.draw.circle(surface, skin, (dx + 26, dy + 40), 5)
    pygame.draw.rect(surface, skin, (dx - 5, dy - 10, 10, 12))
    pygame.draw.circle(surface, skin, (dx, dy - 16), 11)
    hood_pts = [(dx - 18, dy + 4), (dx + 18, dy + 4),
                (dx + 10, dy - 8), (dx, dy - 30), (dx - 10, dy - 8)]
    pygame.draw.polygon(surface, hood, hood_pts)
    pygame.draw.ellipse(surface, leaf, (dx - 5, dy + 20, 10, 18))
    pygame.draw.ellipse(surface, leaf, (dx + 2, dy + 28,  8, 14))


# ------------------------------------------------------------------
# Stirge — small dark creature with proboscis and wings

def stirge_pos(screen_w, screen_h):
    return (int(screen_w * 0.28), int(screen_h * 0.715))


def stirge_rect(screen_w, screen_h):
    x, y = stirge_pos(screen_w, screen_h)
    return pygame.Rect(x - 18, y - 14, 36, 28)


def draw_stirge(surface, screen_w, screen_h, period, is_present, can_interact):
    if not is_present:
        return
    x, y = stirge_pos(screen_w, screen_h)

    body   = (80, 40, 40)
    wing   = (55, 30, 30)
    eye    = (200, 60, 60)

    # Wings (two thin ellipses angled back)
    pygame.draw.ellipse(surface, wing, (x - 20, y - 10, 16, 6))
    pygame.draw.ellipse(surface, wing, (x +  5, y - 10, 16, 6))

    # Body
    pygame.draw.ellipse(surface, body, (x - 10, y - 8, 20, 14))

    # Proboscis
    pygame.draw.line(surface, body, (x - 10, y - 2), (x - 22, y + 4), 2)

    # Eye
    pygame.draw.circle(surface, eye, (x + 4, y - 3), 3)

    # Interaction highlight ring
    if can_interact:
        pygame.draw.circle(surface, (200, 180, 100), (x, y), 18, 1)


# ------------------------------------------------------------------
# Blink Dog — small canine with a magical shimmer

_blink_offset = [0, 0]   # subtle position jitter updated each frame


def blink_dog_pos(screen_w, screen_h):
    return (int(screen_w * 0.60), int(screen_h * 0.715))


def blink_dog_rect(screen_w, screen_h):
    x, y = blink_dog_pos(screen_w, screen_h)
    return pygame.Rect(x - 22, y - 16, 44, 28)


def draw_blink_dog(surface, screen_w, screen_h, period, is_present, can_interact, time_of_day):
    if not is_present:
        return
    bx, by = blink_dog_pos(screen_w, screen_h)

    # Subtle shimmer flicker — offset shifts slightly over time
    flicker = math.sin(time_of_day * math.pi * 40) * 1.5
    x = int(bx + flicker)
    y = by

    fur  = (140, 150, 180)
    dark = (90, 100, 130)
    nose = (60, 60, 80)
    glow = (160, 180, 220)

    # Body
    pygame.draw.ellipse(surface, fur, (x - 18, y - 10, 36, 16))

    # Head
    pygame.draw.circle(surface, fur, (x + 18, y - 8), 10)

    # Ears
    pygame.draw.polygon(surface, dark, [(x + 12, y - 16), (x + 16, y - 22), (x + 20, y - 16)])
    pygame.draw.polygon(surface, dark, [(x + 22, y - 14), (x + 26, y - 20), (x + 28, y - 14)])

    # Legs
    for lx in (x - 12, x - 4, x + 4, x + 12):
        pygame.draw.line(surface, dark, (lx, y + 5), (lx, y + 14), 3)

    # Tail
    pygame.draw.line(surface, fur, (x - 18, y - 4), (x - 26, y - 12), 3)

    # Nose
    pygame.draw.circle(surface, nose, (x + 27, y - 8), 3)

    # Eye
    pygame.draw.circle(surface, (220, 230, 255), (x + 22, y - 11), 2)

    # Faint glow aura
    aura = pygame.Surface((60, 40), pygame.SRCALPHA)
    pygame.draw.ellipse(aura, (160, 180, 220, 25), (0, 0, 60, 40))
    surface.blit(aura, (x - 30, y - 20))

    # Interaction highlight ring
    if can_interact:
        pygame.draw.circle(surface, (200, 180, 100), (x, y), 22, 1)


# ------------------------------------------------------------------
# Dialogue bubble

def draw_dialogue(surface, font, text, anchor_x, anchor_y):
    if not text:
        return
    words = text.split()
    lines, line = [], []
    for w in words:
        line.append(w)
        if font.size(" ".join(line))[0] > 260:
            lines.append(" ".join(line[:-1]))
            line = [w]
    if line:
        lines.append(" ".join(line))

    pad = 8
    lh  = font.get_linesize()
    bw  = max(font.size(l)[0] for l in lines) + pad * 2
    bh  = lh * len(lines) + pad * 2

    bx = anchor_x - bw // 2
    by = anchor_y - bh - 10
    bx = max(4, min(bx, surface.get_width() - bw - 4))

    bg = pygame.Surface((bw, bh), pygame.SRCALPHA)
    bg.fill((15, 25, 15, 200))
    surface.blit(bg, (bx, by))
    pygame.draw.rect(surface, (80, 110, 70), (bx, by, bw, bh), 1)

    for i, ln in enumerate(lines):
        txt = font.render(ln, True, (210, 225, 200))
        surface.blit(txt, (bx + pad, by + pad + i * lh))

    # Tail
    pygame.draw.polygon(surface, (15, 25, 15),
                        [(anchor_x - 4, by + bh),
                         (anchor_x + 4, by + bh),
                         (anchor_x,     by + bh + 8)])


# ------------------------------------------------------------------
# Action panel (bottom-right)

def draw_action_panel(surface, font, screen_w, screen_h, actions):
    """
    actions: list of (label, key_hint, cooldown_fraction, available)
    cooldown_fraction: 0.0 = ready, 1.0 = just used
    """
    pad    = 8
    btn_w  = 160
    btn_h  = 28
    gap    = 6
    total_h = len(actions) * (btn_h + gap) - gap + pad * 2
    total_w = btn_w + pad * 2

    panel_x = screen_w - total_w - 12
    panel_y = screen_h - total_h - 12

    bg = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
    bg.fill((15, 20, 15, 180))
    surface.blit(bg, (panel_x, panel_y))

    for i, (label, key_hint, cd_frac, available) in enumerate(actions):
        bx = panel_x + pad
        by = panel_y + pad + i * (btn_h + gap)

        col = (40, 60, 35) if available else (30, 35, 30)
        pygame.draw.rect(surface, col, (bx, by, btn_w, btn_h), border_radius=3)
        pygame.draw.rect(surface, (60, 80, 55), (bx, by, btn_w, btn_h), 1, border_radius=3)

        # Cooldown overlay
        if cd_frac > 0:
            cd_w = int(btn_w * cd_frac)
            cd_surf = pygame.Surface((cd_w, btn_h), pygame.SRCALPHA)
            cd_surf.fill((0, 0, 0, 100))
            surface.blit(cd_surf, (bx, by))

        text_col = (200, 220, 180) if available else (100, 110, 95)
        hint_col = (130, 150, 110) if available else (70, 80, 65)

        lbl = font.render(label, True, text_col)
        hint = font.render(key_hint, True, hint_col)
        surface.blit(lbl,  (bx + 8,           by + (btn_h - lbl.get_height()) // 2))
        surface.blit(hint, (bx + btn_w - hint.get_width() - 6,
                            by + (btn_h - hint.get_height()) // 2))


# ------------------------------------------------------------------
# Creature action menu

_MENU_W      = 190
_MENU_ITEM_H = 28
_MENU_PAD    = 8


def _menu_origin(anchor_x, anchor_y, n_options, screen_w, screen_h):
    menu_h = n_options * _MENU_ITEM_H + _MENU_PAD * 2
    mx = anchor_x - _MENU_W // 2
    my = anchor_y - menu_h - 14
    mx = max(4, min(mx, screen_w - _MENU_W - 4))
    my = max(4, min(my, screen_h - menu_h - 4))
    return mx, my


def action_menu_item_rects(anchor_x, anchor_y, n_options, screen_w, screen_h):
    """Item rects in game_surf coordinates — use for click detection."""
    mx, my = _menu_origin(anchor_x, anchor_y, n_options, screen_w, screen_h)
    return [
        pygame.Rect(mx, my + _MENU_PAD + i * _MENU_ITEM_H, _MENU_W, _MENU_ITEM_H)
        for i in range(n_options)
    ]


def draw_action_menu(surface, font, options, anchor_x, anchor_y,
                     screen_w, screen_h, hover_idx=-1):
    """
    options: list of (label, detail, available)
      label     — primary text
      detail    — right-aligned secondary text (e.g. "-3 forage"), or ""
      available — False renders greyed out and is not clickable
    """
    n = len(options)
    mx, my = _menu_origin(anchor_x, anchor_y, n, screen_w, screen_h)
    menu_h = n * _MENU_ITEM_H + _MENU_PAD * 2

    bg = pygame.Surface((_MENU_W, menu_h), pygame.SRCALPHA)
    bg.fill((12, 20, 12, 225))
    surface.blit(bg, (mx, my))
    pygame.draw.rect(surface, (70, 100, 60), (mx, my, _MENU_W, menu_h), 1)

    for i, (label, detail, available) in enumerate(options):
        ry = my + _MENU_PAD + i * _MENU_ITEM_H

        if i == hover_idx and available:
            pygame.draw.rect(surface, (30, 50, 25),
                             pygame.Rect(mx + 1, ry, _MENU_W - 2, _MENU_ITEM_H))

        col  = (200, 220, 180) if available else (90, 100, 85)
        dcol = (140, 160, 120) if available else (70, 80, 65)

        surface.blit(font.render(label, True, col), (mx + 10, ry + 6))
        if detail:
            dtxt = font.render(detail, True, dcol)
            surface.blit(dtxt, (mx + _MENU_W - dtxt.get_width() - 8, ry + 6))

    # Tail pointing down toward the creature
    tx = max(mx + 6, min(anchor_x, mx + _MENU_W - 6))
    ty = my + menu_h
    pygame.draw.polygon(surface, (12, 20, 12),
                        [(tx - 5, ty), (tx + 5, ty), (tx, ty + 9)])
    pygame.draw.line(surface, (70, 100, 60), (tx - 5, ty), (tx, ty + 9))
    pygame.draw.line(surface, (70, 100, 60), (tx + 5, ty), (tx, ty + 9))


# ------------------------------------------------------------------
# Ambient motes

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
        pygame.draw.circle(glow, (200, 230, 160, a),          (r * 3, r * 3), r * 3)
        pygame.draw.circle(glow, (240, 255, 200, min(255, a + 60)), (r * 3, r * 3), r)
        surface.blit(glow, (mx - r * 3, my - r * 3))


# ------------------------------------------------------------------
# Master scene draw

def draw_scene(surface, period, time_of_day, screen_w, screen_h,
               creatures=None):
    draw_background(surface, period, screen_w, screen_h)
    draw_trees(surface, period, screen_w, screen_h)
    draw_clearing(surface, period, screen_w, screen_h)
    draw_statue(surface, period, screen_w, screen_h)
    draw_druid(surface, period, screen_w, screen_h)

    if creatures:
        stirge    = creatures.get("stirge")
        blink_dog = creatures.get("blink_dog")
        if stirge:
            draw_stirge(surface, screen_w, screen_h, period,
                        stirge.is_present, stirge.can_interact)
        if blink_dog:
            draw_blink_dog(surface, screen_w, screen_h, period,
                           blink_dog.is_present, blink_dog.can_interact,
                           time_of_day)

    draw_motes(surface, period, time_of_day, screen_w, screen_h)
