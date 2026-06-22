"""
Sprite-based visuals — background and creature art loaded from assets/.
"""

import os
import pygame
import math


_ASSET_DIR   = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
_BG_PATH     = os.path.join(_ASSET_DIR, "background", "background.png")
_SPRITE_DIR  = os.path.join(_ASSET_DIR, "sprites")

# Period tint overlays — applied over the finished scene to convey time of day.
# (r, g, b, alpha); None = no overlay.
_PERIOD_TINT = {
    "dawn":  (255, 170, 110, 35),
    "day":   None,
    "dusk":  (200, 90, 40, 60),
    "night": (15, 15, 60, 110),
}

# Sprite placement, fixed by the Session 11 composite mockup:
# name -> (centre_x_frac, centre_y_frac, width_frac)
_SPRITE_LAYOUT = {
    # Statue art is baked into the background (no _blit_sprite call uses this
    # entry) — position/size derived from extracting a cutout of it for the
    # halo silhouette only. See assets/sprites/statue.png.
    "statue":          (0.470, 0.491, 0.1875),
    "druid":           (0.313, 0.547, 0.074),
    "stirge":          (0.633, 0.618, 0.076),
    "blink_dog":       (0.369, 0.727, 0.083),
    "owlbear":         (0.105, 0.670, 0.160),
    "pseudodragon":    (0.700, 0.203, 0.077),
    "flumph":          (0.870, 0.351, 0.090),
    "moss_wisp":       (0.209, 0.182, 0.062),
    "pixie":           (0.959, 0.232, 0.049),
    "displacer_beast": (0.107, 0.350, 0.198),
}

_bg_cache             = {}
_sprite_raw_cache     = {}
_sprite_scaled_cache  = {}


# ------------------------------------------------------------------
# Sprite / background loading

def _load_sprite_raw(name):
    """Loads a sprite and crops it to its non-transparent bounding box."""
    surf = _sprite_raw_cache.get(name)
    if surf is None:
        raw = pygame.image.load(os.path.join(_SPRITE_DIR, f"{name}.png")).convert_alpha()
        surf = raw.subsurface(raw.get_bounding_rect(1)).copy()
        _sprite_raw_cache[name] = surf
    return surf


def _get_sprite_scaled(name, target_w):
    key = (name, target_w)
    surf = _sprite_scaled_cache.get(key)
    if surf is None:
        raw = _load_sprite_raw(name)
        target_h = max(1, round(raw.get_height() * (target_w / raw.get_width())))
        surf = pygame.transform.smoothscale(raw, (target_w, target_h))
        _sprite_scaled_cache[key] = surf
    return surf


def _scaled_background(screen_w, screen_h):
    key = (screen_w, screen_h)
    surf = _bg_cache.get(key)
    if surf is None:
        raw   = pygame.image.load(_BG_PATH).convert()
        scale = max(screen_w / raw.get_width(), screen_h / raw.get_height())
        sw, sh = round(raw.get_width() * scale), round(raw.get_height() * scale)
        scaled = pygame.transform.smoothscale(raw, (sw, sh))
        cx, cy = (sw - screen_w) // 2, (sh - screen_h) // 2
        surf = scaled.subsurface((cx, cy, screen_w, screen_h)).copy()
        _bg_cache[key] = surf
    return surf


def sprite_pos(name, screen_w, screen_h):
    cx_f, cy_f, _ = _SPRITE_LAYOUT[name]
    return (round(cx_f * screen_w), round(cy_f * screen_h))


def sprite_rect(name, screen_w, screen_h):
    cx_f, cy_f, w_f = _SPRITE_LAYOUT[name]
    cx, cy   = round(cx_f * screen_w), round(cy_f * screen_h)
    target_w = max(1, round(w_f * screen_w))
    raw      = _load_sprite_raw(name)
    target_h = max(1, round(raw.get_height() * (target_w / raw.get_width())))
    return pygame.Rect(cx - target_w // 2, cy - target_h // 2, target_w, target_h)


def _blit_sprite(surface, name, screen_w, screen_h, offset=(0, 0), alpha=255):
    cx_f, cy_f, w_f = _SPRITE_LAYOUT[name]
    cx, cy   = round(cx_f * screen_w) + offset[0], round(cy_f * screen_h) + offset[1]
    target_w = max(1, round(w_f * screen_w))
    img      = _get_sprite_scaled(name, target_w)
    if alpha < 255:
        img = img.copy()
        img.set_alpha(alpha)
    surface.blit(img, (cx - img.get_width() // 2, cy - img.get_height() // 2))


# ------------------------------------------------------------------
# Background — locked-area desaturation
#
# Rough rectangular zones (fractions of the background image) matching where
# each area's creatures sit. Heartstone has no rect — it's always unlocked.

_ZONE_RECTS = {
    "oldwood":          (0.00, 0.00, 0.27, 0.50),
    "thicket":          (0.00, 0.50, 0.27, 1.00),
    "canopy":           (0.30, 0.00, 0.82, 0.40),
    "feywild_boundary": (0.83, 0.00, 1.00, 1.00),
}

_FEATHER_FRAC = 0.04   # feather width as a fraction of screen width

_bg_locked_cache = {}


def _feathered_zone_mask(w, h, rect_px, feather_px):
    """Solid-white rect, blurred via downscale/upscale to feather its edges."""
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), rect_px)
    small_w = max(1, w // max(1, feather_px))
    small_h = max(1, h // max(1, feather_px))
    small   = pygame.transform.smoothscale(mask, (small_w, small_h))
    return pygame.transform.smoothscale(small, (w, h))


def _background_with_locked_zones(screen_w, screen_h, locked_zones):
    key = (screen_w, screen_h, frozenset(locked_zones))
    surf = _bg_locked_cache.get(key)
    if surf is not None:
        return surf

    colour = _scaled_background(screen_w, screen_h)
    if not locked_zones:
        _bg_locked_cache[key] = colour
        return colour

    surf = colour.copy()
    grey = pygame.transform.grayscale(colour)
    feather_px = max(1, round(screen_w * _FEATHER_FRAC))

    for name in locked_zones:
        rect_f = _ZONE_RECTS.get(name)
        if not rect_f:
            continue
        x0, y0, x1, y1 = rect_f
        rect_px = pygame.Rect(round(x0 * screen_w), round(y0 * screen_h),
                              round((x1 - x0) * screen_w), round((y1 - y0) * screen_h))
        mask = _feathered_zone_mask(screen_w, screen_h, rect_px, feather_px)

        grey_rgba = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        grey_rgba.blit(grey, (0, 0))
        grey_rgba.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surf.blit(grey_rgba, (0, 0))

    _bg_locked_cache[key] = surf
    return surf


def draw_background(surface, period, screen_w, screen_h, areas=None):
    locked = [name for name in _ZONE_RECTS
              if areas is not None and not areas.is_unlocked(name)]
    surface.blit(_background_with_locked_zones(screen_w, screen_h, locked), (0, 0))


def draw_period_tint(surface, period, screen_w, screen_h):
    tint = _PERIOD_TINT.get(period)
    if not tint:
        return
    overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    overlay.fill(tint)
    surface.blit(overlay, (0, 0))


# ------------------------------------------------------------------
# Silvanus statue — baked into the background art; this draws only the
# ambient glow and provides the click rect.

def draw_statue(surface, period, screen_w, screen_h):
    cx = screen_w // 2
    base_y = round(screen_h * 0.684)
    glow = pygame.Surface((90, 90), pygame.SRCALPHA)
    pygame.draw.circle(glow, (140, 110, 200, 28), (45, 45), 42)
    surface.blit(glow, (cx - 45, base_y - 235))


def statue_rect(screen_w, screen_h):
    cx = screen_w // 2
    base_y = round(screen_h * 0.684)
    w = round(screen_w * 0.114)
    h = round(screen_h * 0.43)
    return pygame.Rect(cx - w // 2, base_y - h, w, h)


# ------------------------------------------------------------------
# Druid figure

def druid_pos(screen_w, screen_h):
    return sprite_pos("druid", screen_w, screen_h)


def druid_rect(screen_w, screen_h):
    return sprite_rect("druid", screen_w, screen_h)


# All idle-animation timings below are driven by anim_time — real elapsed
# seconds (pygame.time.get_ticks()/1000), NOT time_of_day/game time. They used
# to be keyed off time_of_day, which advances 60x faster under dev speed; that
# made every idle animation either too slow at normal speed or frantic in dev
# mode, with no single constant that worked for both. anim_time is immune to
# the dev-speed multiplier, so animation speed now reads the same in both.

def _breathe(anim_time, period, amplitude):
    return round(math.sin(anim_time * 2 * math.pi / period) * amplitude)


def draw_druid(surface, period, screen_w, screen_h, anim_time=0.0):
    breath = _breathe(anim_time, 7.0, 1)
    _blit_sprite(surface, "druid", screen_w, screen_h, offset=(0, breath))


# ------------------------------------------------------------------
# Stirge

def stirge_pos(screen_w, screen_h):
    return sprite_pos("stirge", screen_w, screen_h)


def stirge_rect(screen_w, screen_h):
    return sprite_rect("stirge", screen_w, screen_h)


def draw_stirge(surface, screen_w, screen_h, period, is_present, anim_time=0.0):
    if not is_present:
        return
    breath = _breathe(anim_time, 5.0, 1)
    _blit_sprite(surface, "stirge", screen_w, screen_h, offset=(0, breath))


# ------------------------------------------------------------------
# Blink Dog — subtle shimmer-flicker jitter

def blink_dog_pos(screen_w, screen_h):
    return sprite_pos("blink_dog", screen_w, screen_h)


def blink_dog_rect(screen_w, screen_h):
    return sprite_rect("blink_dog", screen_w, screen_h)


def draw_blink_dog(surface, screen_w, screen_h, period, is_present, anim_time):
    if not is_present:
        return
    flicker = _breathe(anim_time, 1.0, 1.5)
    _blit_sprite(surface, "blink_dog", screen_w, screen_h, offset=(flicker, 0))


# ------------------------------------------------------------------
# Owlbear

def owlbear_pos(screen_w, screen_h):
    return sprite_pos("owlbear", screen_w, screen_h)


def owlbear_rect(screen_w, screen_h):
    return sprite_rect("owlbear", screen_w, screen_h)


def draw_owlbear(surface, screen_w, screen_h, period, is_present, anim_time=0.0):
    if not is_present:
        return
    breath = _breathe(anim_time, 6.0, 1)
    _blit_sprite(surface, "owlbear", screen_w, screen_h, offset=(0, breath))


# ------------------------------------------------------------------
# Pseudodragon

def pseudodragon_pos(screen_w, screen_h):
    return sprite_pos("pseudodragon", screen_w, screen_h)


def pseudodragon_rect(screen_w, screen_h):
    return sprite_rect("pseudodragon", screen_w, screen_h)


def draw_pseudodragon(surface, screen_w, screen_h, period, is_present, anim_time=0.0):
    if not is_present:
        return
    breath = _breathe(anim_time, 5.5, 1)
    _blit_sprite(surface, "pseudodragon", screen_w, screen_h, offset=(0, breath))


# ------------------------------------------------------------------
# Flumph — gentle bob

def flumph_pos(screen_w, screen_h):
    return sprite_pos("flumph", screen_w, screen_h)


def flumph_rect(screen_w, screen_h):
    return sprite_rect("flumph", screen_w, screen_h)


def draw_flumph(surface, screen_w, screen_h, period, is_present, anim_time):
    if not is_present:
        return
    bob = _breathe(anim_time, 3.83, 4)
    _blit_sprite(surface, "flumph", screen_w, screen_h, offset=(0, bob))


# ------------------------------------------------------------------
# Moss Wisp — slow drift

def moss_wisp_pos(screen_w, screen_h):
    return sprite_pos("moss_wisp", screen_w, screen_h)


def moss_wisp_rect(screen_w, screen_h):
    return sprite_rect("moss_wisp", screen_w, screen_h)


def draw_moss_wisp(surface, screen_w, screen_h, period, is_present, anim_time):
    if not is_present:
        return
    drift_x = round(math.sin(anim_time * 2 * math.pi / 4.6) * 3)
    drift_y = round(math.cos(anim_time * 2 * math.pi / 6.13) * 3)
    _blit_sprite(surface, "moss_wisp", screen_w, screen_h, offset=(drift_x, drift_y))


# ------------------------------------------------------------------
# Pixie — flutter

def pixie_pos(screen_w, screen_h):
    return sprite_pos("pixie", screen_w, screen_h)


def pixie_rect(screen_w, screen_h):
    return sprite_rect("pixie", screen_w, screen_h)


def draw_pixie(surface, screen_w, screen_h, period, is_present, anim_time):
    if not is_present:
        return
    flutter = _breathe(anim_time, 1.3, 3)
    _blit_sprite(surface, "pixie", screen_w, screen_h, offset=(0, flutter))


# ------------------------------------------------------------------
# Displacer Beast — faint ghost-offset double image (displacement illusion)

def displacer_beast_pos(screen_w, screen_h):
    return sprite_pos("displacer_beast", screen_w, screen_h)


def displacer_beast_rect(screen_w, screen_h):
    return sprite_rect("displacer_beast", screen_w, screen_h)


def draw_displacer_beast(surface, screen_w, screen_h, period, is_present, anim_time):
    if not is_present:
        return
    ghost_x = _breathe(anim_time, 2.5, 6) + 10
    breath  = _breathe(anim_time, 6.5, 1)
    _blit_sprite(surface, "displacer_beast", screen_w, screen_h,
                 offset=(ghost_x, breath), alpha=50)
    _blit_sprite(surface, "displacer_beast", screen_w, screen_h, offset=(0, breath))


# ------------------------------------------------------------------
# Halo — pulsing glow tracing a sprite's silhouette, shown whenever there's
# something to do with it (interact/event ready on a creature, grove event
# or tend-ready on the statue, visitor event or forage-ready on the druid).
# Replaces the old placeholder "!" marker everywhere.

_HALO_COLOR      = (255, 225, 140)
_HALO_SCALE      = 1.18
_HALO_BLUR_DIV   = 3   # higher blur softens flat edges (sprite touching its crop bbox) into curves
_HALO_PULSE_PERIOD = 1.5   # real seconds per pulse cycle, independent of dev speed

_silhouette_cache = {}
_halo_cache       = {}


def _make_silhouette(raw, color):
    """
    One-time per (sprite, colour): flat-colour silhouette matching raw's alpha
    mask. Built via pygame.mask + a single BLEND_RGBA_MULT blit rather than a
    per-pixel Python loop — at raw sprite resolution (~900px) the per-pixel
    loop took multiple seconds per sprite and froze startup.
    """
    sil = pygame.Surface(raw.get_size(), pygame.SRCALPHA)
    sil.fill((*color, 255))
    mask_surf = pygame.mask.from_surface(raw).to_surface(
        setcolor=(255, 255, 255, 255), unsetcolor=(255, 255, 255, 0))
    sil.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return sil


def _get_halo(name, target_w, color=_HALO_COLOR, punch_center=False):
    key = (name, target_w, color, punch_center)
    surf = _halo_cache.get(key)
    if surf is None:
        raw = _load_sprite_raw(name)
        sil = _silhouette_cache.get((name, color))
        if sil is None:
            sil = _make_silhouette(raw, color)
            _silhouette_cache[(name, color)] = sil

        halo_w = max(1, round(target_w * _HALO_SCALE))
        halo_h = max(1, round(raw.get_height() * (halo_w / raw.get_width())))
        scaled = pygame.transform.smoothscale(sil, (halo_w, halo_h))

        small_w = max(1, halo_w // _HALO_BLUR_DIV)
        small_h = max(1, halo_h // _HALO_BLUR_DIV)
        blurred = pygame.transform.smoothscale(
            pygame.transform.smoothscale(scaled, (small_w, small_h)), (halo_w, halo_h))

        # Punch the sprite's own footprint out of the blurred ring, so only the
        # glow outside it shows. Only needed for entities nothing redraws on
        # top of the halo (the statue) — for animated sprites (druid,
        # creatures), their own redraw each frame already covers the centre
        # at wherever they *currently* are, including idle-animation offsets;
        # punching a hole fixed to the base layout position instead exposed
        # the ring's inner edge whenever the sprite bobbed/drifted away from
        # that fixed spot (e.g. flumph).
        if punch_center:
            inner_w = max(1, target_w)
            inner_h = max(1, round(raw.get_height() * (inner_w / raw.get_width())))
            inner = pygame.transform.smoothscale(raw, (inner_w, inner_h))
            ox, oy = (halo_w - inner_w) // 2, (halo_h - inner_h) // 2
            punch = pygame.mask.from_surface(inner).to_surface(
                setcolor=(255, 255, 255, 0), unsetcolor=(255, 255, 255, 255))
            blurred.blit(punch, (ox, oy), special_flags=pygame.BLEND_RGBA_MULT)

        surf = blurred
        _halo_cache[key] = surf
    return surf


def halo_pulse(anim_time):
    return 0.5 + 0.5 * math.sin(anim_time * 2 * math.pi / _HALO_PULSE_PERIOD)


def draw_halo(surface, name, screen_w, screen_h, pulse, punch_center=False):
    cx_f, cy_f, w_f = _SPRITE_LAYOUT[name]
    cx, cy   = round(cx_f * screen_w), round(cy_f * screen_h)
    target_w = max(1, round(w_f * screen_w))
    halo     = _get_halo(name, target_w, punch_center=punch_center).copy()
    halo.set_alpha(int(110 + 90 * pulse))
    surface.blit(halo, (cx - halo.get_width() // 2, cy - halo.get_height() // 2))


# ------------------------------------------------------------------
# Bond bar — small segmented bar under a present creature's sprite,
# replacing the old sidebar bond-status list.

_BOND_SEG_W = 13
_BOND_SEG_H = 5
_BOND_GAP   = 1
_BOND_MAX   = 3

# Some sprites have a lot of transparent "air" below their visual mass
# (e.g. flumph's tapering tentacle tips), which pads out their bounding-box
# bottom — pull the bar up closer to the body for those.
_BOND_BAR_GAP = 4
_BOND_BAR_GAP_OVERRIDE = {
    "blink_dog": -4,
    "flumph":    -16,
}


def draw_bond_bar(surface, anchor_x, top_y, bond_level, flashing=False):
    total_w = _BOND_MAX * _BOND_SEG_W + (_BOND_MAX - 1) * _BOND_GAP
    x = anchor_x - total_w // 2

    fill_col   = (255, 240, 180) if flashing else (210, 180, 90)
    empty_col  = (40, 40, 40)
    border_col = (15, 15, 15)

    for i in range(_BOND_MAX):
        sx = x + i * (_BOND_SEG_W + _BOND_GAP)
        col = fill_col if i < bond_level else empty_col
        pygame.draw.rect(surface, col, (sx, top_y, _BOND_SEG_W, _BOND_SEG_H))
        pygame.draw.rect(surface, border_col, (sx, top_y, _BOND_SEG_W, _BOND_SEG_H), 1)


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
# Areas restoration panel

_AREA_DISPLAY_NAMES = {
    "heartstone":       "The Heartstone",
    "thicket":          "The Thicket",
    "canopy":           "The Canopy",
    "feywild_boundary": "The Feywild Boundary",
    "oldwood":          "The Oldwood",
}

_AP_ROW_H   = 50
_AP_PAD     = 14
_AP_W       = 410
_AP_TITLE_H = 36
_AP_HINT_H  = 24


def draw_areas_panel(surface, font, font_sm, areas, resources, screen_w, screen_h):
    """
    Draw the grove restoration panel.
    Returns {area_name: rect} for clickable (next-unlockable) rows.
    """
    n       = len(areas.ALL)
    panel_h = _AP_TITLE_H + n * _AP_ROW_H + _AP_HINT_H + _AP_PAD * 2
    px      = (screen_w - _AP_W) // 2
    py      = (screen_h - panel_h) // 2

    # Dim scene behind panel
    dim = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 150))
    surface.blit(dim, (0, 0))

    # Panel background
    bg = pygame.Surface((_AP_W, panel_h), pygame.SRCALPHA)
    bg.fill((12, 20, 12, 235))
    surface.blit(bg, (px, py))
    pygame.draw.rect(surface, (70, 100, 60), (px, py, _AP_W, panel_h), 1)

    title = font.render("Grove Restoration", True, (190, 220, 165))
    surface.blit(title, (px + _AP_PAD, py + _AP_PAD))

    next_name = areas.next_to_unlock()
    clickable = {}

    for i, name in enumerate(areas.ALL):
        ry        = py + _AP_PAD + _AP_TITLE_H + i * _AP_ROW_H
        row_rect  = pygame.Rect(px + _AP_PAD, ry, _AP_W - _AP_PAD * 2, _AP_ROW_H - 6)
        unlocked  = areas.is_unlocked(name)
        is_next   = name == next_name
        affordable = is_next and areas.can_afford(name, resources)

        if is_next:
            bg_col     = (25, 45, 20) if affordable else (35, 28, 12)
            border_col = (100, 150, 80) if affordable else (120, 100, 40)
            pygame.draw.rect(surface, bg_col,     row_rect, border_radius=3)
            pygame.draw.rect(surface, border_col, row_rect, 1, border_radius=3)
            clickable[name] = row_rect

        # Area name
        if unlocked:
            name_col = (155, 200, 130)
        elif is_next:
            name_col = (215, 205, 150) if affordable else (185, 168, 105)
        else:
            name_col = (72, 82, 68)

        display = _AREA_DISPLAY_NAMES.get(name, name.replace("_", " ").title())
        surface.blit(font.render(display, True, name_col), (row_rect.x + 8, ry + 7))

        # Right-side status / cost
        if unlocked:
            st = font_sm.render("Active", True, (105, 170, 90))
            surface.blit(st, (row_rect.right - st.get_width() - 8, ry + 11))
        else:
            cost     = areas.unlock_cost(name)
            cost_str = "  +  ".join(f"{int(v)} {k}" for k, v in cost.items())
            if affordable:
                cost_col = (170, 190, 120)
            elif is_next:
                cost_col = (145, 130, 75)
            else:
                cost_col = (52, 60, 48)
            ct = font_sm.render(cost_str, True, cost_col)
            surface.blit(ct, (row_rect.right - ct.get_width() - 8, ry + 11))
            if is_next and affordable:
                ht = font_sm.render("click to restore", True, (90, 140, 70))
                surface.blit(ht, (row_rect.x + 8, ry + 28))

    # Close hint
    ch = font_sm.render("[R]  close", True, (62, 82, 55))
    surface.blit(ch, (px + (_AP_W - ch.get_width()) // 2, py + panel_h - _AP_HINT_H))

    return clickable


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
# Bottom text box (creature options + dialogue + grove messages)

_TB_H      = 100
_TB_PAD    = 10
_TB_MARGIN = 20


def draw_text_box(surface, font, font_sm, speaker, text, options,
                  hover_idx, screen_w, screen_h, right_inset=0):
    """
    Fixed bottom panel. Two modes:
      options mode — options is a non-empty list of (label, detail, available);
                     returns item rects for click detection.
      text mode    — text is a string, options is None or [];
                     returns [].
    Only call when there is content to show.

    right_inset: extra space reserved on the right (e.g. for the resource
    panel sharing the same row) — shrinks the box width without moving its
    left edge.
    """
    bx = _TB_MARGIN
    by = screen_h - _TB_H - _TB_MARGIN
    bw = screen_w - _TB_MARGIN * 2 - right_inset

    bg = pygame.Surface((bw, _TB_H), pygame.SRCALPHA)
    bg.fill((10, 18, 10, 220))
    surface.blit(bg, (bx, by))
    pygame.draw.rect(surface, (70, 100, 60), (bx, by, bw, _TB_H), 1)

    # Speaker label
    label_h = 0
    if speaker:
        sp = font_sm.render(speaker, True, (130, 180, 110))
        surface.blit(sp, (bx + _TB_PAD, by + _TB_PAD))
        label_h = font_sm.get_linesize() + 4

    content_y = by + _TB_PAD + label_h
    item_rects = []

    if options:
        item_h = 22
        for i, (label, detail, available) in enumerate(options):
            ry = content_y + i * item_h
            r  = pygame.Rect(bx + _TB_PAD, ry, bw - _TB_PAD * 2, item_h)
            item_rects.append(r)

            if i == hover_idx and available:
                pygame.draw.rect(surface, (30, 50, 25), r)

            col  = (200, 220, 180) if available else (90, 100, 85)
            dcol = (140, 160, 120) if available else (70, 80, 65)

            surface.blit(font_sm.render(label, True, col), (r.x + 6, ry + 4))
            if detail:
                dtxt = font_sm.render(detail, True, dcol)
                surface.blit(dtxt, (r.right - dtxt.get_width() - 6, ry + 4))

    else:
        if text:
            words    = text.split()
            lines, line = [], []
            max_w    = bw - _TB_PAD * 2
            for w in words:
                line.append(w)
                if font.size(" ".join(line))[0] > max_w:
                    lines.append(" ".join(line[:-1]))
                    line = [w]
            if line:
                lines.append(" ".join(line))

            lh = font.get_linesize()
            for i, ln in enumerate(lines[:3]):
                t = font.render(ln, True, (210, 225, 200))
                surface.blit(t, (bx + _TB_PAD, content_y + i * lh))

        hint = font_sm.render("[ESC] dismiss", True, (60, 85, 50))
        surface.blit(hint, (bx + bw - hint.get_width() - _TB_PAD,
                            by + _TB_H - font_sm.get_linesize() - 4))

    return item_rects


def text_box_item_rects(font_sm, speaker, n_options, screen_w, screen_h, right_inset=0):
    """Returns option rects for text box options mode without drawing."""
    bx        = _TB_MARGIN
    by        = screen_h - _TB_H - _TB_MARGIN
    bw        = screen_w - _TB_MARGIN * 2 - right_inset
    label_h   = (font_sm.get_linesize() + 4) if speaker else 0
    content_y = by + _TB_PAD + label_h
    return [
        pygame.Rect(bx + _TB_PAD, content_y + i * 22, bw - _TB_PAD * 2, 22)
        for i in range(n_options)
    ]


# ------------------------------------------------------------------
# Centre flash (errors, save confirmation)

def draw_center_flash(surface, font_sm, text, alpha, screen_w, screen_h):
    """Small semi-transparent panel centred on screen. Alpha 0–255."""
    if not text or alpha <= 0:
        return
    t  = font_sm.render(text, True, (215, 230, 205))
    tw = t.get_width()
    th = t.get_height()
    pad = 10
    bw  = tw + pad * 2
    bh  = th + pad * 2
    bx  = (screen_w - bw) // 2
    by  = screen_h // 2 - bh - 20   # slightly above centre

    bg = pygame.Surface((bw, bh), pygame.SRCALPHA)
    bg.fill((10, 18, 10, min(200, alpha)))
    surface.blit(bg, (bx, by))

    border = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(border, (70, 100, 60, min(255, alpha)), (0, 0, bw, bh), 1)
    surface.blit(border, (bx, by))

    t.set_alpha(alpha)
    surface.blit(t, (bx + pad, by + pad))


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
               creatures=None, events=None, areas=None,
               statue_ready=False, druid_ready=False, anim_time=0.0):
    draw_background(surface, period, screen_w, screen_h, areas)

    pulse = halo_pulse(anim_time)

    statue_glow = bool(events and events.grove_pending_event) or statue_ready
    if statue_glow:
        draw_halo(surface, "statue", screen_w, screen_h, pulse, punch_center=True)
    draw_statue(surface, period, screen_w, screen_h)

    druid_glow = bool(events and events.visitor_pending_event) or druid_ready
    if druid_glow:
        draw_halo(surface, "druid", screen_w, screen_h, pulse)
    draw_druid(surface, period, screen_w, screen_h, anim_time)

    if creatures:
        for name in ("stirge", "blink_dog", "owlbear", "pseudodragon",
                     "flumph", "moss_wisp", "pixie", "displacer_beast"):
            c = creatures.get(name)
            if not c or not c.is_present:
                continue

            if c.can_interact or c.has_event:
                draw_halo(surface, name, screen_w, screen_h, pulse)

            if name == "stirge":
                draw_stirge(surface, screen_w, screen_h, period, c.is_present, anim_time)
                rect = stirge_rect(screen_w, screen_h)
            elif name == "blink_dog":
                draw_blink_dog(surface, screen_w, screen_h, period,
                               c.is_present, anim_time)
                rect = blink_dog_rect(screen_w, screen_h)
            elif name == "owlbear":
                draw_owlbear(surface, screen_w, screen_h, period, c.is_present, anim_time)
                rect = owlbear_rect(screen_w, screen_h)
            elif name == "pseudodragon":
                draw_pseudodragon(surface, screen_w, screen_h, period, c.is_present, anim_time)
                rect = pseudodragon_rect(screen_w, screen_h)
            elif name == "flumph":
                draw_flumph(surface, screen_w, screen_h, period,
                            c.is_present, anim_time)
                rect = flumph_rect(screen_w, screen_h)
            elif name == "moss_wisp":
                draw_moss_wisp(surface, screen_w, screen_h, period,
                               c.is_present, anim_time)
                rect = moss_wisp_rect(screen_w, screen_h)
            elif name == "pixie":
                draw_pixie(surface, screen_w, screen_h, period,
                           c.is_present, anim_time)
                rect = pixie_rect(screen_w, screen_h)
            elif name == "displacer_beast":
                draw_displacer_beast(surface, screen_w, screen_h, period,
                                     c.is_present, anim_time)
                rect = displacer_beast_rect(screen_w, screen_h)

            gap = _BOND_BAR_GAP_OVERRIDE.get(name, _BOND_BAR_GAP)
            draw_bond_bar(surface, rect.centerx, rect.bottom + gap,
                          c.bond_level, flashing=c.bond_flash_ttl > 0)

    draw_period_tint(surface, period, screen_w, screen_h)
    draw_motes(surface, period, time_of_day, screen_w, screen_h)
