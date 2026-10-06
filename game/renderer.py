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

# Sprite placement, from the Session 18 composite mockup (docs/phase5_art_spec.csv),
# in background-image pixels (the full 1536x1024 background.png, before any
# scaling/cropping to the window) so values can be checked against the spec
# directly. Mapped to screen space via _bg_transform().
# name -> (centre_x, bottom_y, height)
_SPRITE_LAYOUT = {
    "statue":          (780,  626, 440),
    "druid":           (560,  646, 317),
    "stirge":          (1172, 580, 115),
    "blink_dog":       (890,  770, 181),
    "owlbear":         (190, 1050, 391),   # deliberately runs off the bottom edge
    "pseudodragon":    (1088, 238, 110),
    "flumph":          (1400, 380, 120),
    "moss_wisp":       (315,  180,  88),
    "pixie":           (1420, 180,  63),
    "displacer_beast": (200,  520, 304),
}

# Pixels below this alpha don't count as sprite content when cropping. Several
# generated sprites carry a faint near-invisible haze out to the canvas edge;
# counting it would undersize and mis-anchor the visible art. Low enough to
# keep the moss wisp's intentionally soft edge (the spec measured it at >20).
_SPRITE_ALPHA_CUTOFF = 20

_bg_raw               = None
_bg_cache             = {}
_sprite_raw_cache     = {}
_sprite_scaled_cache  = {}


# ------------------------------------------------------------------
# Sprite / background loading

def _load_sprite_raw(name):
    """Loads a sprite and crops it to its visible bounding box."""
    surf = _sprite_raw_cache.get(name)
    if surf is None:
        raw = pygame.image.load(os.path.join(_SPRITE_DIR, f"{name}.png")).convert_alpha()
        surf = raw.subsurface(raw.get_bounding_rect(_SPRITE_ALPHA_CUTOFF)).copy()
        _sprite_raw_cache[name] = surf
    return surf


def _get_sprite_scaled(name, target_h):
    key = (name, target_h)
    surf = _sprite_scaled_cache.get(key)
    if surf is None:
        raw = _load_sprite_raw(name)
        target_w = max(1, round(raw.get_width() * (target_h / raw.get_height())))
        surf = pygame.transform.smoothscale(raw, (target_w, target_h))
        _sprite_scaled_cache[key] = surf
    return surf


def _load_bg_raw():
    global _bg_raw
    if _bg_raw is None:
        _bg_raw = pygame.image.load(_BG_PATH).convert_alpha()   # sky notch is transparent
    return _bg_raw


def _bg_transform(screen_w, screen_h):
    """(scale, crop_x, crop_y) mapping background-image pixels to the screen:
    the background is scaled uniformly to cover the window, then centre-cropped."""
    raw   = _load_bg_raw()
    scale = max(screen_w / raw.get_width(), screen_h / raw.get_height())
    sw, sh = round(raw.get_width() * scale), round(raw.get_height() * scale)
    return scale, (sw - screen_w) // 2, (sh - screen_h) // 2


def _scaled_background(screen_w, screen_h):
    key = (screen_w, screen_h)
    surf = _bg_cache.get(key)
    if surf is None:
        raw   = _load_bg_raw()
        scale, cx, cy = _bg_transform(screen_w, screen_h)
        sw, sh = round(raw.get_width() * scale), round(raw.get_height() * scale)
        scaled = pygame.transform.smoothscale(raw, (sw, sh))
        surf = scaled.subsurface((cx, cy, screen_w, screen_h)).copy()
        _bg_cache[key] = surf
    return surf


def _sprite_geom(name, screen_w, screen_h):
    """Screen-space (centre_x, centre_y, width, height) for a sprite's layout."""
    bx, b_bottom, b_h = _SPRITE_LAYOUT[name]
    scale, crop_x, crop_y = _bg_transform(screen_w, screen_h)
    target_h = max(1, round(b_h * scale))
    raw      = _load_sprite_raw(name)
    target_w = max(1, round(raw.get_width() * (target_h / raw.get_height())))
    cx     = round(bx * scale) - crop_x
    bottom = round(b_bottom * scale) - crop_y
    return cx, bottom - target_h // 2, target_w, target_h


def sprite_pos(name, screen_w, screen_h):
    cx, cy, _, _ = _sprite_geom(name, screen_w, screen_h)
    return (cx, cy)


def sprite_rect(name, screen_w, screen_h):
    cx, cy, w, h = _sprite_geom(name, screen_w, screen_h)
    return pygame.Rect(cx - w // 2, cy - h // 2, w, h)


def _blit_sprite(surface, name, screen_w, screen_h, offset=(0, 0), alpha=255):
    cx, cy, _, target_h = _sprite_geom(name, screen_w, screen_h)
    cx, cy = cx + offset[0], cy + offset[1]
    img    = _get_sprite_scaled(name, target_h)
    if alpha < 255:
        img = img.copy()
        img.set_alpha(alpha)
    surface.blit(img, (cx - img.get_width() // 2, cy - img.get_height() // 2))


# ------------------------------------------------------------------
# Background — locked-area desaturation
#
# Zone outlines traced against background.png, in background-image pixels
# (same space as _SPRITE_LAYOUT). Neighbouring zones share edge points so
# they meet without gaps. Heartstone (the clearing) is whatever's left and is
# never greyed; the sky notch is transparent in the background, so the sky
# drawn behind it stays coloured regardless.

_ZONE_POLYS = {
    # Gnarled tree plus every other tree on the left, including the left half
    # of the far-forest view; split from canopy below the sky notch.
    "oldwood": [
        (0, 0), (770, 0), (770, 380), (707, 388), (698, 368), (666, 358),
        (611, 358), (540, 354), (470, 385), (450, 420), (380, 440), (330, 470), (250, 460),
        (180, 425), (100, 400), (0, 390),
    ],
    # The whole bramble mass: lower-left corner plus the band along the bottom.
    "thicket": [
        (0, 390), (100, 400), (180, 425), (250, 460), (270, 520), (330, 575),
        (390, 640), (470, 690), (600, 700), (700, 715), (800, 750),
        (950, 765), (1040, 785), (1100, 808), (1140, 830), (1170, 880),
        (1200, 925), (1250, 970), (1320, 1024), (0, 1024),
    ],
    # Upper-right trees.
    "canopy": [
        (770, 0), (1250, 0), (1254, 148), (1215, 170), (1202, 200),
        (1205, 250), (1225, 285), (1244, 307), (1240, 330), (1190, 380),
        (1125, 364), (1105, 354), (1085, 325), (1060, 326), (1035, 330),
        (1015, 362), (980, 358), (940, 355), (913, 358), (859, 368),
        (770, 380),
    ],
    # Purple veil strip, full height, widening to take in the purple flowers;
    # the path in the bottom-right corner stays part of the clearing.
    "feywild_boundary": [
        (1250, 0), (1536, 0), (1536, 1005), (1500, 985), (1430, 916),
        (1350, 853), (1294, 808), (1290, 760), (1295, 685), (1350, 655),
        (1385, 610), (1340, 570), (1290, 530), (1330, 482), (1260, 470),
        (1200, 430), (1190, 380), (1240, 330), (1244, 307), (1225, 285),
        (1205, 250), (1202, 200), (1215, 170), (1254, 148),
    ],
}

_FEATHER_FRAC = 0.010   # feather width as a fraction of screen width

_bg_locked_cache = {}


def _locked_zones_mask(screen_w, screen_h, locked_zones, feather_px):
    """
    One combined mask for every locked zone, feathered via downscale/upscale.
    Combined (not per-zone) so two locked neighbours don't each fade out
    along their shared edge and leave a coloured seam between them.
    """
    scale, crop_x, crop_y = _bg_transform(screen_w, screen_h)
    mask = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    for name in locked_zones:
        poly = _ZONE_POLYS.get(name)
        if poly:
            pts = [(round(x * scale) - crop_x, round(y * scale) - crop_y) for x, y in poly]
            pygame.draw.polygon(mask, (255, 255, 255, 255), pts)
    small_w = max(1, screen_w // max(1, feather_px))
    small_h = max(1, screen_h // max(1, feather_px))
    small   = pygame.transform.smoothscale(mask, (small_w, small_h))
    return pygame.transform.smoothscale(small, (screen_w, screen_h))


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
    feather_px = max(1, round(screen_w * _FEATHER_FRAC))
    mask = _locked_zones_mask(screen_w, screen_h, locked_zones, feather_px)

    grey_rgba = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    grey_rgba.blit(pygame.transform.grayscale(colour), (0, 0))
    grey_rgba.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(grey_rgba, (0, 0))

    _bg_locked_cache[key] = surf
    return surf


def draw_background(surface, blend, screen_w, screen_h, areas=None):
    draw_sky(surface, blend, screen_w, screen_h)
    locked = [name for name in _ZONE_POLYS
              if areas is not None and not areas.is_unlocked(name)]
    surface.blit(_background_with_locked_zones(screen_w, screen_h, locked), (0, 0))


# ------------------------------------------------------------------
# Sky — vertical gradient drawn behind the background, showing through its
# transparent (keyed-out) sky notch. One gradient per period, crossfaded at
# period boundaries. The period tint is still applied over it afterwards.

# period -> (top colour, horizon colour)
_SKY_COLORS = {
    "dawn":  ((120, 150, 205), (250, 190, 150)),
    "day":   ((95, 150, 220),  (170, 205, 235)),
    "dusk":  ((80, 70, 140),   (240, 140, 90)),
    "night": ((10, 14, 40),    (30, 35, 75)),
}
_SKY_GRADIENT_FRAC = 0.16   # gradient spans this fraction of screen height; horizon colour below

_sky_cache = {}


def _get_sky(period, screen_w, screen_h):
    key = (period, screen_w, screen_h)
    surf = _sky_cache.get(key)
    if surf is None:
        top, horizon = _SKY_COLORS[period]
        grad_h = max(1, round(screen_h * _SKY_GRADIENT_FRAC))
        surf = pygame.Surface((screen_w, screen_h))
        surf.fill(horizon)
        for y in range(grad_h):
            pygame.draw.line(surf, _lerp_color(top, horizon, y / grad_h),
                             (0, y), (screen_w, y))
        _sky_cache[key] = surf
    return surf


def draw_sky(surface, blend, screen_w, screen_h):
    p_from, p_to, t = blend
    surface.blit(_get_sky(p_from, screen_w, screen_h), (0, 0))
    if t > 0:
        incoming = _get_sky(p_to, screen_w, screen_h)
        incoming.set_alpha(round(t * 255))
        surface.blit(incoming, (0, 0))
        incoming.set_alpha(None)


def _blended_tint(blend):
    """Interpolated (r, g, b, a) tint; a period with no tint fades as alpha 0."""
    p_from, p_to, t = blend
    a, b = _PERIOD_TINT.get(p_from), _PERIOD_TINT.get(p_to)
    if a is None and b is None:
        return None
    a = a or (*b[:3], 0)
    b = b or (*a[:3], 0)
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


def draw_period_tint(surface, blend, screen_w, screen_h):
    tint = _blended_tint(blend)
    if not tint or tint[3] <= 0:
        return
    overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    overlay.fill(tint)
    surface.blit(overlay, (0, 0))


# ------------------------------------------------------------------
# Silvanus statue — static sprite with a faint ambient glow behind its
# upper body.

_STATUE_GLOW_COLOR    = (140, 110, 200, 28)
_STATUE_GLOW_R_FRAC   = 0.45   # glow radius as a fraction of the statue's width
_STATUE_GLOW_Y_FRAC   = 0.30   # glow centre, down from the statue's top, as a fraction of its height


def draw_statue(surface, period, screen_w, screen_h):
    cx, cy, w, h = _sprite_geom("statue", screen_w, screen_h)
    r = max(1, round(w * _STATUE_GLOW_R_FRAC))
    glow = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    pygame.draw.circle(glow, _STATUE_GLOW_COLOR, (r, r), r)
    glow_cy = cy - h // 2 + round(h * _STATUE_GLOW_Y_FRAC)
    surface.blit(glow, (cx - r, glow_cy - r))
    _blit_sprite(surface, "statue", screen_w, screen_h)


def statue_rect(screen_w, screen_h):
    return sprite_rect("statue", screen_w, screen_h)


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


def _get_halo(name, target_w, color=_HALO_COLOR):
    """Solid blurred glow, drawn before its sprite — the sprite's own redraw
    (at its current animation offset) covers the centre, leaving a ring."""
    key = (name, target_w, color)
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

        surf = blurred
        _halo_cache[key] = surf
    return surf


def halo_pulse(anim_time):
    return 0.5 + 0.5 * math.sin(anim_time * 2 * math.pi / _HALO_PULSE_PERIOD)


def draw_halo(surface, name, screen_w, screen_h, pulse):
    cx, cy, target_w, _ = _sprite_geom(name, screen_w, screen_h)
    halo = _get_halo(name, target_w).copy()
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
# Help / info panel — two tabs: Controls, Feeding

_HP_W       = 460
_HP_TAB_H   = 36
_HP_ROW_H   = 22
_HP_PAD     = 14
_HP_HINT_H  = 24

_HELP_CONTROLS = [
    ("Click", "Interact with a creature, the statue, or the druid"),
    ("Enter", "Advance or dismiss dialogue"),
    ("S",     "Save"),
    ("R",     "Open/close the grove restoration panel"),
    ("H",     "Open/close this help menu"),
    ("Esc",   "Close a menu, or quit"),
]


def draw_help_panel(surface, font, font_sm, active_tab, config, screen_w, screen_h):
    """
    Two-tab reference panel (Controls / Feeding).
    Returns {"controls": rect, "feeding": rect} tab click targets.
    """
    if active_tab == "feeding":
        rows = [(name.replace("_", " ").title(), cfg.get("feeding", {}))
                for name, cfg in config["creatures"].items()]
    else:
        rows = _HELP_CONTROLS

    panel_h = _HP_TAB_H + len(rows) * _HP_ROW_H + _HP_HINT_H + _HP_PAD * 2
    px = (screen_w - _HP_W) // 2
    py = (screen_h - panel_h) // 2

    dim = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 150))
    surface.blit(dim, (0, 0))

    bg = pygame.Surface((_HP_W, panel_h), pygame.SRCALPHA)
    bg.fill((12, 20, 12, 235))
    surface.blit(bg, (px, py))
    pygame.draw.rect(surface, (70, 100, 60), (px, py, _HP_W, panel_h), 1)

    # Tabs
    tab_w  = _HP_W // 2
    tabs   = {}
    labels = [("controls", "Controls"), ("feeding", "Feeding")]
    for i, (key, label) in enumerate(labels):
        rect = pygame.Rect(px + i * tab_w, py, tab_w, _HP_TAB_H)
        tabs[key] = rect
        active = key == active_tab
        if active:
            pygame.draw.rect(surface, (25, 45, 20), rect)
        col = (200, 220, 180) if active else (100, 120, 90)
        t = font.render(label, True, col)
        surface.blit(t, (rect.centerx - t.get_width() // 2, rect.centery - t.get_height() // 2))
    pygame.draw.line(surface, (70, 100, 60), (px, py + _HP_TAB_H), (px + _HP_W, py + _HP_TAB_H))
    pygame.draw.line(surface, (70, 100, 60), (px + tab_w, py), (px + tab_w, py + _HP_TAB_H))

    # Body
    body_y = py + _HP_TAB_H + _HP_PAD
    if active_tab == "feeding":
        col_day, col_cost, col_cd = px + 150, px + 230, px + 320
        for i, (name, feed) in enumerate(rows):
            ry = body_y + i * _HP_ROW_H
            nm = font_sm.render(name, True, (170, 200, 150))
            surface.blit(nm, (px + _HP_PAD, ry))

            per_day = feed.get("feeds_per_day", 0)
            cost    = feed.get("forage_cost", 0)
            cd      = feed.get("cooldown_real_seconds", 0)
            cd_str  = f"{cd / 60:.0f} min cooldown" if cd > 0 else "no cooldown"

            surface.blit(font_sm.render(f"{per_day}/day", True, (130, 155, 115)), (col_day, ry))
            surface.blit(font_sm.render(f"{cost:.0f} forage", True, (130, 155, 115)), (col_cost, ry))
            surface.blit(font_sm.render(cd_str, True, (130, 155, 115)), (col_cd, ry))
    else:
        for i, (key, desc) in enumerate(rows):
            ry = body_y + i * _HP_ROW_H
            kt = font_sm.render(key, True, (200, 220, 180))
            surface.blit(kt, (px + _HP_PAD, ry))
            dt = font_sm.render(desc, True, (150, 170, 135))
            surface.blit(dt, (px + _HP_PAD + 70, ry))

    ch = font_sm.render("[H]  close", True, (62, 82, 55))
    surface.blit(ch, (px + (_HP_W - ch.get_width()) // 2, py + panel_h - _HP_HINT_H))

    return tabs


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

# Rune discs (continue / dismiss) — a small hand-carved stone disc per state,
# same "material" for both, only the etched rune and tint differ. The rune is
# engraved (dark shadow offset up-left, bright highlight offset down-right)
# rather than painted on top of the stone.

_RUNE_CANVAS      = 120   # reference coordinate space the shapes are authored in
_RUNE_STONE_R     = 34
_RUNE_RIM_SCALE   = 0.78
_RUNE_JITTER      = [1, -2, 2, -1, 1, -2, 1, -1, 2, -1]   # per-point radius jitter, irregular outline
_RUNE_RENDER_PX   = 64    # cached surface build resolution
_RUNE_DISPLAY_PX  = 26    # on-screen size in the text box

_RUNE_GREEN_LIT           = (124, 145, 102)
_RUNE_GREEN_MID           = (79, 95, 64)
_RUNE_GREEN_SHADOW        = (41, 51, 33)
_RUNE_GREEN_OUTLINE       = (21, 28, 17)
_RUNE_GREEN_RIM           = (30, 36, 23)
_RUNE_GREEN_GROOVE_SHADOW = (30, 36, 23)
_RUNE_GREEN_GROOVE_HI     = (185, 214, 158)

_RUNE_RED_LIT           = (150, 105, 95)
_RUNE_RED_MID           = (106, 70, 63)
_RUNE_RED_SHADOW        = (51, 31, 27)
_RUNE_RED_OUTLINE       = (28, 18, 15)
_RUNE_RED_RIM           = (37, 24, 19)
_RUNE_RED_GROOVE_SHADOW = (37, 24, 19)
_RUNE_RED_GROOVE_HI     = (227, 166, 150)

_RUNE_ARROW_STROKES = [
    [(46, 42), (63, 54), (71, 60)],
    [(71, 60), (62, 67), (45, 78)],
]
_RUNE_X_STROKES = [
    [(44, 42), (56, 54), (61, 60), (66, 66), (76, 78)],
    [(76, 41), (65, 53), (61, 59), (56, 65), (45, 77)],
]

_TB_GLYPH_BOUNCE_PERIOD = 0.9
_TB_GLYPH_BOUNCE_AMP    = 3

_rune_disc_cache = {}


def _lerp_color(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _quad_bezier_points(p0, p1, p2, n=8):
    pts = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        x = mt * mt * p0[0] + 2 * mt * t * p1[0] + t * t * p2[0]
        y = mt * mt * p0[1] + 2 * mt * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    return pts


def _sample_multi_bezier(points, n_per_seg=8):
    """points: [p0, ctrl0, p2, ctrl1, p4, ...] — chained quadratic segments."""
    result = []
    for i in range(0, len(points) - 2, 2):
        seg = _quad_bezier_points(points[i], points[i + 1], points[i + 2], n_per_seg)
        if result:
            seg = seg[1:]
        result.extend(seg)
    return result


def _build_stone_poly(cx, cy, base_r, jitter):
    """Smooth closed irregular blob — a hand-carved stone outline, not a perfect circle."""
    n = len(jitter)
    pts = []
    for i in range(n):
        angle = 2 * math.pi * i / n
        r = base_r + jitter[i]
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    mids = [((pts[i][0] + pts[(i + 1) % n][0]) / 2,
             (pts[i][1] + pts[(i + 1) % n][1]) / 2) for i in range(n)]
    poly = []
    for i in range(n):
        poly.extend(_quad_bezier_points(mids[i - 1], pts[i], mids[i], n=6))
    return poly


def _draw_thick_polyline(surface, pts, color, width):
    """Approximates a round-capped, round-jointed stroke with plain line/circle draws."""
    r = max(1, width // 2)
    ipts = [(round(x), round(y)) for x, y in pts]
    for i in range(len(ipts) - 1):
        pygame.draw.line(surface, color, ipts[i], ipts[i + 1], width)
    for p in ipts:
        pygame.draw.circle(surface, color, p, r)


def _build_rune_disc(is_continue):
    size  = _RUNE_RENDER_PX
    scale = size / _RUNE_CANVAS
    cx = cy = size / 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)

    if is_continue:
        lit, mid, shadow = _RUNE_GREEN_LIT, _RUNE_GREEN_MID, _RUNE_GREEN_SHADOW
        outline, rim     = _RUNE_GREEN_OUTLINE, _RUNE_GREEN_RIM
        groove_shadow, groove_hi = _RUNE_GREEN_GROOVE_SHADOW, _RUNE_GREEN_GROOVE_HI
        strokes = _RUNE_ARROW_STROKES
    else:
        lit, mid, shadow = _RUNE_RED_LIT, _RUNE_RED_MID, _RUNE_RED_SHADOW
        outline, rim     = _RUNE_RED_OUTLINE, _RUNE_RED_RIM
        groove_shadow, groove_hi = _RUNE_RED_GROOVE_SHADOW, _RUNE_RED_GROOVE_HI
        strokes = _RUNE_X_STROKES

    def to_px(p):
        return (p[0] * scale, p[1] * scale)

    # Stone body — banded gradient (nested scaled-down copies of the blob),
    # shadow at the edge fading to lit toward the centre.
    poly = [to_px(p) for p in _build_stone_poly(60, 60, _RUNE_STONE_R, _RUNE_JITTER)]
    steps = 8
    for i in range(steps, 0, -1):
        t = i / steps
        ring = [(cx + (x - cx) * t, cy + (y - cy) * t) for x, y in poly]
        if t > 0.5:
            col = _lerp_color(mid, shadow, (t - 0.5) / 0.5)
        else:
            col = _lerp_color(mid, lit, (0.5 - t) / 0.5)
        pygame.draw.polygon(surf, col, ring)
    pygame.draw.polygon(surf, outline, poly, max(1, round(2 * scale)))

    rim_poly = [to_px(p) for p in _build_stone_poly(
        60, 60, _RUNE_STONE_R * _RUNE_RIM_SCALE, [j * _RUNE_RIM_SCALE for j in _RUNE_JITTER])]
    pygame.draw.lines(surf, rim, True, rim_poly, max(1, round(1.6 * scale)))

    # Engraved rune — shadow (up-left) / mid-tone base / highlight (down-right)
    off      = max(1.0, 1.0 * scale)
    base_w   = max(1, round(4.6 * scale))
    shadow_w = max(1, round(2.6 * scale))
    hi_w     = max(1, round(2.1 * scale))
    for stroke in strokes:
        pts = _sample_multi_bezier([to_px(p) for p in stroke])
        shadow_pts = [(x - off, y - off) for x, y in pts]
        hi_pts     = [(x + off, y + off) for x, y in pts]
        _draw_thick_polyline(surf, shadow_pts, groove_shadow, shadow_w)
        _draw_thick_polyline(surf, pts, mid, base_w)
        _draw_thick_polyline(surf, hi_pts, groove_hi, hi_w)

    return surf


def _get_rune_disc(is_continue):
    if is_continue not in _rune_disc_cache:
        _rune_disc_cache[is_continue] = _build_rune_disc(is_continue)
    return _rune_disc_cache[is_continue]


def _draw_continue_glyph(surface, cx, cy, anim_time):
    """Green rune disc, bounces sideways — hints there's another box to advance to."""
    disc   = _get_rune_disc(True)
    offset = _breathe(anim_time, _TB_GLYPH_BOUNCE_PERIOD, _TB_GLYPH_BOUNCE_AMP)
    scaled = pygame.transform.smoothscale(disc, (_RUNE_DISPLAY_PX, _RUNE_DISPLAY_PX))
    surface.blit(scaled, scaled.get_rect(center=(cx + offset, cy)))


def _draw_dismiss_glyph(surface, cx, cy, anim_time):
    """Red rune disc, zooms in/out — hints this is the last box, dismissible."""
    disc = _get_rune_disc(False)
    zoom = 1.0 + 0.1 * halo_pulse(anim_time)
    px   = max(1, round(_RUNE_DISPLAY_PX * zoom))
    scaled = pygame.transform.smoothscale(disc, (px, px))
    surface.blit(scaled, scaled.get_rect(center=(cx, cy)))


def draw_text_box(surface, font, font_sm, speaker, text, options,
                  hover_idx, screen_w, screen_h, right_inset=0,
                  has_more=False, anim_time=0.0):
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

        glyph_cx = bx + bw - _TB_PAD - _RUNE_DISPLAY_PX // 2
        glyph_cy = by + _TB_H - _TB_PAD - _RUNE_DISPLAY_PX // 2
        if has_more:
            _draw_continue_glyph(surface, glyph_cx, glyph_cy, anim_time)
        else:
            _draw_dismiss_glyph(surface, glyph_cx, glyph_cy, anim_time)

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
               statue_ready=False, druid_ready=False, anim_time=0.0,
               blend=None):
    # blend: (from_period, to_period, t) from TimeSystem.period_blend — drives
    # the sky and tint crossfade. Omitted -> hold the current period.
    if blend is None:
        blend = (period, period, 0.0)
    draw_background(surface, blend, screen_w, screen_h, areas)

    pulse = halo_pulse(anim_time)

    statue_glow = bool(events and events.grove_pending_event) or statue_ready
    if statue_glow:
        draw_halo(surface, "statue", screen_w, screen_h, pulse)
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

    draw_period_tint(surface, blend, screen_w, screen_h)
    draw_motes(surface, period, time_of_day, screen_w, screen_h)
