"""
One-time asset prep: key the chroma-magenta sky gap out of background.png.

The generated background leaves the sky as a magenta (#FF00FF) notch so the
game can draw its own time-of-day sky behind it. This turns that magenta into
real transparency and strips the pink spill from the leaf edges around it.

Art-prep tool only (uses Pillow) — not imported by the game.

Usage:  python tools/key_sky.py [input.png] [output.png]
        (defaults to assets/background/background.png in place)
"""

import os
import sys

from PIL import Image

ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT = os.path.join(ROOT, "assets", "background", "background.png")

# Only the sky notch is processed — the Feywild Boundary's purple flowers are
# magenta-ish too and must not be keyed. Box in background pixels (x0, y0, x1, y1).
SKY_BOX = (620, 0, 940, 200)

# "Magenta excess" = min(r, b) - g. Pure magenta scores ~255, foliage ~0 or
# below. At or above KEY_HI a pixel is fully sky; at or below KEY_LO it's
# fully foliage; in between it's an edge pixel blended with the sky.
KEY_LO = 40
KEY_HI = 200

MAGENTA = (255, 0, 255)

# Edge recolour pass: tinted pixels within EDGE_BAND px of the sky are
# repainted from clean neighbours within SAMPLE_R px.
EDGE_BAND    = 10
SAMPLE_R     = 4
TINT_B_SLACK = 8


def key_pixel(r, g, b):
    excess = min(r, b) - g
    if excess <= KEY_LO:
        sky = 0.0   # opaque, but may still carry faint pink spill — despilled below
    elif excess >= KEY_HI:
        return (0, 0, 0, 0)
    else:
        sky = (excess - KEY_LO) / (KEY_HI - KEY_LO)

    alpha = 1.0 - sky
    # Un-mix: remove the magenta share from the observed colour.
    fr, fg, fb = ((c - sky * m) / alpha for c, m in zip((r, g, b), MAGENTA))
    fr, fg, fb = (max(0.0, min(255.0, c)) for c in (fr, fg, fb))

    # Despill: foliage shouldn't have red AND blue both above green.
    spill = min(fr, fb) - fg
    if spill > 0:
        fr -= spill
        fb -= spill

    return (round(fr), round(fg), round(fb), round(alpha * 255))


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    dst = sys.argv[2] if len(sys.argv) > 2 else src

    img  = Image.open(src).convert("RGBA")
    orig = img.copy().load()
    px   = img.load()
    x0, y0, x1, y1 = SKY_BOX
    keyed = edged = 0
    for y in range(y0, min(y1, img.height)):
        for x in range(x0, min(x1, img.width)):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            out = key_pixel(r, g, b)
            if out[3] == 0:
                keyed += 1
            elif out[3] < 255 or out[:3] != (r, g, b):
                edged += 1
            px[x, y] = out

    recoloured = recolour_edge_tint(img, orig)
    img.save(dst)
    print(f"{dst}: {keyed} px keyed to transparent, {edged} edge px un-mixed, "
          f"{recoloured} tinted edge px recoloured")


def _is_tinted(r, g, b):
    """Pink/salmon cast left by magenta bleeding into foliage. Branch browns
    have blue well below green, so they don't match."""
    return r > g and b >= g - TINT_B_SLACK


def recolour_edge_tint(img, orig):
    """
    Pixels near the keyed sky whose ORIGINAL colour was tinted get repainted
    with the average of nearby clean opaque pixels — the generator muddied
    these edges, so un-mixing alone can't recover a true foliage colour.
    """
    px = img.load()
    x0, y0, x1, y1 = SKY_BOX
    x1, y1 = min(x1, img.width), min(y1, img.height)

    def near_sky(x, y):
        for dy in range(-EDGE_BAND, EDGE_BAND + 1):
            for dx in range(-EDGE_BAND, EDGE_BAND + 1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < img.width and 0 <= ny < img.height and px[nx, ny][3] < 255:
                    return True
        return False

    targets = [(x, y) for y in range(y0, y1) for x in range(x0, x1)
               if px[x, y][3] > 0 and _is_tinted(*orig[x, y][:3]) and near_sky(x, y)]
    target_set = set(targets)

    fixes = {}
    for x, y in targets:
        acc, n = [0, 0, 0], 0
        for dy in range(-SAMPLE_R, SAMPLE_R + 1):
            for dx in range(-SAMPLE_R, SAMPLE_R + 1):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < img.width and 0 <= ny < img.height):
                    continue
                if (nx, ny) in target_set or px[nx, ny][3] < 255 or _is_tinted(*orig[nx, ny][:3]):
                    continue
                r, g, b, _ = px[nx, ny]
                acc[0] += r; acc[1] += g; acc[2] += b; n += 1
        if n:
            fixes[(x, y)] = tuple(round(c / n) for c in acc) + (px[x, y][3],)

    for (x, y), colour in fixes.items():
        px[x, y] = colour
    return len(fixes)


if __name__ == "__main__":
    main()
