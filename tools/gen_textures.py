"""Generate every PNG the Starforge mod ships.

Run with:  python3 tools/gen_textures.py
Writes into src/main/resources/assets/starforge/textures/ plus the mod icon.
"""
import math
import os
import random
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from palette import (  # noqa: E402
    CLEAR, WHITE,
    VOID_0, VOID_1, VOID_2, VOID_3,
    STEEL_0, STEEL_1, STEEL_2, STEEL_3,
    EMBER_0, EMBER_1, EMBER_2, EMBER_3, EMBER_4,
    STAR_0, STAR_1, STAR_2,
    ARC_0, ARC_1, ARC_2,
)

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
TEX = os.path.join(ROOT, "src/main/resources/assets/starforge/textures")


# --------------------------------------------------------------------------
# tiny canvas helpers
# --------------------------------------------------------------------------
class Canvas:
    def __init__(self, w=16, h=16):
        self.img = Image.new("RGBA", (w, h), CLEAR)
        self.px = self.img.load()
        self.w, self.h = w, h

    def set(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h and col[3]:
            self.px[int(x), int(y)] = col

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.px[int(x), int(y)]
        return CLEAR

    def rect(self, x0, y0, x1, y1, col):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, col)

    def save(self, *parts):
        path = os.path.join(TEX, *parts)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.img.save(path)
        return path


def shade(col, f):
    """Scale a colour's brightness by f, keeping alpha."""
    return (
        max(0, min(255, int(col[0] * f))),
        max(0, min(255, int(col[1] * f))),
        max(0, min(255, int(col[2] * f))),
        col[3],
    )


def mix(a, b, t):
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
        int(a[3] + (b[3] - a[3]) * t),
    )


# --------------------------------------------------------------------------
# weapons / tools

def _bezier(p0, p1, p2, steps=64):
    """Quadratic bezier sampled to integer pixel coordinates (deduped)."""
    out, seen = [], set()
    for i in range(steps + 1):
        t = i / float(steps)
        u = 1 - t
        x = round(u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0])
        y = round(u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1])
        if (x, y) not in seen:
            seen.add((x, y))
            out.append((x, y))
    return out


def _line(a, b):
    """Integer line points from a to b."""
    (x0, y0), (x1, y1) = a, b
    n = max(abs(x1 - x0), abs(y1 - y0))
    if n == 0:
        return [(x0, y0)]
    return [(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n))
            for i in range(n + 1)]


def starfall_blade():
    """Straight blade running up-right, ember crossguard, void grip."""
    c = Canvas()
    for i in range(9):                          # three parallel diagonals
        c.set(12 - i, 1 + i, STEEL_1)           # back of the blade
        c.set(13 - i, 2 + i, STEEL_3)           # bright centre ridge
        c.set(14 - i, 3 + i, STEEL_0)           # shadowed cutting edge
    c.set(13, 1, STEEL_2)                       # tip
    c.set(14, 1, STEEL_3)
    c.set(15, 0, STEEL_3)
    c.set(14, 2, STEEL_1)
    c.set(6, 9, STAR_2)                         # star set into the forte
    c.set(5, 10, STAR_1)
    for k in (-2, -1, 1, 2):                    # crossguard, perpendicular
        c.set(4 + k, 11 + k, EMBER_2 if abs(k) == 1 else EMBER_1)
    c.set(4, 11, EMBER_4)
    c.set(3, 10, EMBER_3)
    for k in range(1, 4):                       # grip runs down-left
        c.set(4 - k, 11 + k, VOID_3 if k % 2 else VOID_2)
        c.set(5 - k, 11 + k, VOID_1)
    c.set(0, 15, EMBER_1)                       # pommel
    c.set(1, 14, EMBER_3)
    c.set(2, 14, EMBER_1)
    return c


def worldbreaker():
    """Heavy mace: blocky head top-right, long haft to a bottom-left pommel."""
    c = Canvas()
    for x, y in _line((8, 7), (1, 14)):         # haft
        c.set(x, y, VOID_3)
        c.set(x + 1, y, VOID_2)
        c.set(x, y + 1, VOID_1)
    for y in range(1, 7):                       # head block
        for x in range(9, 16):
            edge = x in (9, 15) or y in (1, 6)
            c.set(x, y, STEEL_0 if edge else mix(STEEL_2, STEEL_1, (y - 1) / 5.0))
    c.set(9, 1, CLEAR)
    c.set(15, 1, CLEAR)
    c.set(9, 6, CLEAR)
    c.set(15, 6, CLEAR)
    for y in range(2, 6):                       # molten core down the head
        c.set(12, y, EMBER_3 if y in (3, 4) else EMBER_1)
    c.set(12, 3, EMBER_4)
    c.set(11, 3, EMBER_2)
    c.set(13, 4, EMBER_2)
    for x, y in ((8, 3), (8, 4), (11, 0), (13, 0), (11, 7), (13, 7)):
        c.set(x, y, STEEL_1)                    # studs
    c.set(10, 2, STEEL_3)
    c.set(1, 14, EMBER_3)                       # pommel
    c.set(0, 15, EMBER_1)
    c.set(2, 14, EMBER_1)
    return c


def starforge_pickaxe():
    """Curved head arcing over the top, haft down to the bottom-left."""
    c = Canvas()
    for x, y in _line((2, 14), (10, 5)):        # haft
        c.set(x, y, VOID_3)
        c.set(x + 1, y, VOID_2)
        c.set(x, y + 1, VOID_1)
    head = _bezier((3, 8), (9, -2), (15, 6))
    for x, y in head:                           # head, two pixels thick
        c.set(x, y, STEEL_2)
        c.set(x, y + 1, STEEL_0)
    c.set(3, 8, STEEL_1)
    c.set(15, 6, STEEL_1)
    c.set(2, 9, STEEL_0)
    for x, y in head[len(head) // 2 - 1:len(head) // 2 + 2]:
        c.set(x, y, STEEL_3)                    # crown highlight
    c.set(9, 3, EMBER_3)                        # ember eye where head meets haft
    c.set(10, 4, EMBER_2)
    c.set(1, 14, EMBER_2)                       # pommel
    c.set(0, 15, EMBER_1)
    return c


def voidpiercer(pull=-1):
    """Bow drawn as a ) limb with a straight string. pull -1 idle, 0..2 draw."""
    c = Canvas()
    bulge = 5 + [0, 0, 1, 1][pull + 1]
    limb = []
    for y in range(1, 16):
        x = 8 + int(round(bulge * math.sin(math.pi * (y - 1) / 14.0)))
        limb.append((x, y))
    for x, y in limb:                           # limb body
        c.set(x, y, VOID_3)
        c.set(x - 1, y, VOID_2)
    for x, y in limb[5:10]:                     # grip wrap
        c.set(x, y, EMBER_1)
        c.set(x - 1, y, EMBER_2)
    c.set(limb[7][0], 8, EMBER_4)
    for x, y in (limb[0], limb[-1]):            # nocks
        c.set(x, y, STEEL_2)
        c.set(x - 1, y, STEEL_1)
    anchor = 8 - [0, 2, 4, 6][pull + 1]
    for seg in (_line(limb[0], (anchor, 8)), _line((anchor, 8), limb[-1])):
        for x, y in seg:
            c.set(x, y, STEEL_3)
    if pull >= 0:                               # nocked arrow
        for x in range(anchor, 16):
            c.set(x, 8, EMBER_2 if x % 2 else EMBER_1)
        c.set(anchor, 8, STEEL_3)
        c.set(anchor + 1, 7, STEEL_2)
        c.set(anchor + 1, 9, STEEL_2)
        c.set(15, 8, STAR_2)
    return c


def voidshard():
    """Faceted crystal shard, bright facet on the light side."""
    c = Canvas()
    widths = {1: 0, 2: 1, 3: 2, 12: 2, 13: 1, 14: 0}
    for y in range(1, 15):
        hw = widths.get(y, 3)
        for x in range(8 - hw, 8 + hw + 1):
            if x < 8:                           # lit facet
                col = mix(ARC_2, ARC_1, (8 - x) / 4.0)
            elif x == 8:
                col = ARC_1
            else:                               # shadowed facet
                col = mix(ARC_0, VOID_1, (x - 8) / 4.0)
            c.set(x, y, col)
    for y in range(3, 13, 3):                   # facet breaks
        for x in range(8 - widths.get(y, 3), 9 + widths.get(y, 3)):
            c.set(x, y, shade(c.get(x, y), 0.72))
    c.set(7, 3, WHITE)                          # glint
    c.set(7, 4, ARC_2)
    c.set(8, 2, ARC_2)
    c.set(10, 11, VOID_0)
    c.set(8, 14, VOID_0)
    return c

# --------------------------------------------------------------------------
def blade_band(c, steps, start, dark, mid, light, core=None):
    """Draw a 3px wide diagonal blade running up-right from `start`."""
    sx, sy = start
    for i in range(steps):
        x, y = sx - i, sy + i
        c.set(x - 1, y + 1, dark)
        c.set(x, y, light)
        c.set(x + 1, y - 1, mid)
        if core and i % 3 == 1:
            c.set(x, y, core)


def hilt(c, cross, grip_dark, grip_light, pommel, cx=4, cy=11):
    """Crossguard perpendicular to an up-right blade, plus grip and pommel."""
    for k in (-2, -1, 0, 1, 2):
        c.set(cx + k, cy + k, cross if k else shade(cross, 1.25))
    for k in range(1, 4):                      # grip runs down-left
        c.set(cx - k, cy + k, grip_dark if k % 2 else grip_light)
    c.set(cx - 4, cy + 4, pommel)
    c.set(cx - 3, cy + 4, shade(pommel, 0.7))







def emberbrand():
    """Early-game iron blade with a heat-glowing edge."""
    c = Canvas()
    for i in range(9):
        c.set(12 - i, 1 + i, STEEL_1)
        c.set(13 - i, 2 + i, STEEL_2)
        c.set(14 - i, 3 + i, EMBER_2)          # the edge runs hot
    c.set(13, 1, STEEL_2)
    c.set(14, 1, STEEL_3)
    c.set(15, 0, EMBER_4)
    c.set(14, 2, EMBER_3)
    for k in (-2, -1, 1, 2):
        c.set(4 + k, 11 + k, EMBER_1 if abs(k) == 1 else EMBER_0)
    c.set(4, 11, EMBER_3)
    for k in range(1, 4):
        c.set(4 - k, 11 + k, VOID_2 if k % 2 else VOID_3)
        c.set(5 - k, 11 + k, VOID_1)
    c.set(1, 14, EMBER_2)
    c.set(0, 15, EMBER_0)
    return c


def starsteel_shard():
    """Small early-game crystal: steel blue with an ember heart."""
    c = Canvas()
    widths = {3: 0, 4: 1, 5: 2, 11: 2, 12: 1, 13: 0}
    for y in range(3, 14):
        hw = widths.get(y, 3)
        for x in range(8 - hw, 8 + hw + 1):
            col = mix(STEEL_3, STEEL_1, (8 - x + hw) / (2.0 * hw + 1)) if x < 8 \
                else mix(STEEL_1, STEEL_0, (x - 8) / 4.0)
            c.set(x, y, col)
    for y in range(6, 11):                     # ember heart
        c.set(8, y, EMBER_2 if y % 2 else EMBER_3)
    c.set(7, 5, WHITE)
    c.set(7, 6, STEEL_3)
    c.set(9, 12, VOID_1)
    c.set(8, 13, VOID_0)
    return c


def starforge_codex():
    """A bound book with a star sigil on the cover."""
    c = Canvas()
    c.rect(2, 2, 13, 13, VOID_2)               # cover
    c.rect(2, 2, 13, 2, VOID_3)
    c.rect(2, 13, 13, 13, VOID_0)
    c.rect(2, 2, 2, 13, VOID_1)
    c.rect(3, 3, 4, 12, EMBER_1)               # spine
    c.set(3, 3, EMBER_3)
    c.set(4, 12, EMBER_0)
    c.rect(13, 3, 13, 12, STEEL_1)             # page edges
    c.rect(12, 3, 12, 12, STEEL_3)
    for dx, dy in ((0, -3), (0, 3), (-3, 0), (3, 0)):   # star sigil
        c.set(8 + dx, 8 + dy, EMBER_3)
    for dx, dy in ((0, -2), (0, 2), (-2, 0), (2, 0)):
        c.set(8 + dx, 8 + dy, EMBER_4)
    for dx, dy in ((-1, -1), (1, 1), (-1, 1), (1, -1)):
        c.set(8 + dx, 8 + dy, EMBER_2)
    c.set(8, 8, WHITE)
    c.set(7, 8, STAR_2)
    return c


# --------------------------------------------------------------------------
# materials and trinkets
# --------------------------------------------------------------------------
def starsteel_ingot():
    c = Canvas()
    for y in range(6, 12):                     # ingot body, slight taper
        inset = 0 if 7 <= y <= 10 else 1
        for x in range(3 + inset, 14 - inset):
            t = (y - 6) / 5.0
            c.set(x, y, mix(STEEL_2, STEEL_0, t))
    for x in range(4, 13):                     # top highlight
        c.set(x, 6, STEEL_3)
    for x in range(4, 13, 3):                  # starlight veins
        c.set(x, 8, STAR_1)
        c.set(x + 1, 9, STAR_0)
    c.set(6, 7, WHITE)
    c.set(11, 10, STEEL_0)
    return c



def astral_core():
    c = Canvas()
    for y in range(16):                        # radiant orb
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if d <= 5.4:
                t = d / 5.4
                c.set(x, y, mix(WHITE, EMBER_2, t ** 1.4))
            elif d <= 6.4:
                c.set(x, y, mix(EMBER_1, VOID_1, (d - 5.4)))
    for ang in range(0, 360, 45):              # eight-point star flare
        a = math.radians(ang)
        for r in range(4, 8):
            col = EMBER_4 if r < 6 else EMBER_2
            c.set(round(7.5 + math.cos(a) * r), round(7.5 + math.sin(a) * r), col)
    c.set(7, 7, WHITE)
    c.set(8, 7, WHITE)
    return c


def astral_elixir():
    c = Canvas()
    c.rect(6, 1, 9, 2, STEEL_1)                # stopper
    c.set(6, 1, STEEL_2)
    c.rect(7, 3, 8, 4, STEEL_0)                # neck
    for y in range(5, 15):                     # flask
        halfw = {5: 2, 6: 3, 14: 3}.get(y, 4)
        if y >= 13:
            halfw = 4 if y == 13 else 3
        for x in range(7 - halfw + 1, 8 + halfw):
            c.set(x, y, mix(ARC_0, VOID_1, 0.3))
    for y in range(7, 14):                     # liquid
        halfw = 3 if y > 7 else 2
        for x in range(7 - halfw + 1, 8 + halfw):
            t = (y - 7) / 6.0
            c.set(x, y, mix(STAR_2, ARC_1, t))
    c.set(5, 9, ARC_2)
    c.set(6, 8, WHITE)
    c.set(10, 12, VOID_0)
    return c


def heart_of_the_star():
    c = Canvas()
    for y in range(16):                        # totem plate
        for x in range(16):
            if 3 <= x <= 12 and 1 <= y <= 14:
                edge = x in (3, 12) or y in (1, 14)
                c.set(x, y, EMBER_0 if edge else mix(EMBER_2, EMBER_1, y / 14.0))
    for y in range(3, 13):                     # inset
        for x in range(5, 11):
            c.set(x, y, mix(VOID_2, VOID_0, (y - 3) / 9.0))
    for y in range(16):                        # beating core
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.0)
            if d <= 2.6:
                c.set(x, y, mix(WHITE, STAR_1, d / 2.6))
    for dx, dy in ((0, -4), (0, 4), (-3, 0), (3, 0)):
        c.set(7 + dx, 7 + dy, STAR_2)
        c.set(8 + dx, 7 + dy, STAR_2)
    c.set(4, 2, EMBER_4)
    c.set(11, 13, EMBER_0)
    return c


# --------------------------------------------------------------------------
# armour icons
# --------------------------------------------------------------------------
def _plate(c, x0, y0, x1, y1):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            t = (y - y0) / max(1.0, float(y1 - y0))
            c.set(x, y, mix(STEEL_2, STEEL_0, t))


def starforge_helmet():
    c = Canvas()
    _plate(c, 3, 3, 12, 10)
    c.rect(3, 3, 12, 3, STEEL_3)
    c.rect(4, 7, 11, 8, VOID_0)                # visor slit
    c.rect(5, 7, 10, 7, STAR_1)
    c.rect(3, 11, 4, 12, STEEL_1)              # cheek guards
    c.rect(11, 11, 12, 12, STEEL_1)
    for x in (5, 7, 9):                        # crest
        c.set(x, 2, EMBER_3)
    c.set(7, 1, EMBER_4)
    c.set(3, 4, STEEL_0)
    c.set(12, 10, STEEL_0)
    return c


def starforge_chestplate():
    c = Canvas()
    _plate(c, 4, 3, 11, 12)
    c.rect(1, 3, 3, 9, STEEL_1)                # pauldrons
    c.rect(12, 3, 14, 9, STEEL_1)
    c.rect(1, 3, 3, 3, STEEL_3)
    c.rect(12, 3, 14, 3, STEEL_3)
    c.rect(4, 3, 11, 3, STEEL_3)               # collar
    c.rect(7, 4, 8, 12, EMBER_1)               # central seam
    c.set(7, 6, EMBER_3)
    c.set(8, 6, EMBER_4)
    c.set(7, 7, STAR_2)
    c.set(8, 7, STAR_1)
    for y in (9, 11):                          # rivet rows
        for x in (5, 10):
            c.set(x, y, STEEL_3)
    return c


def starforge_leggings():
    c = Canvas()
    _plate(c, 3, 2, 12, 6)                     # belt
    c.rect(3, 2, 12, 2, STEEL_3)
    c.rect(7, 3, 8, 5, EMBER_2)
    c.set(7, 4, STAR_2)
    _plate(c, 3, 7, 6, 14)                     # left leg
    _plate(c, 9, 7, 12, 14)                    # right leg
    for y in (9, 12):
        c.rect(3, y, 6, y, STEEL_1)
        c.rect(9, y, 12, y, STEEL_1)
    c.set(4, 8, STEEL_3)
    c.set(10, 8, STEEL_3)
    return c


def starforge_boots():
    """A pair of greaves seen from the front: cuff, ankle, forward-pointing foot."""
    c = Canvas()
    for ox in (1, 9):                           # two identical boots
        _plate(c, ox, 3, ox + 5, 9)             # shin cuff
        c.rect(ox, 3, ox + 5, 3, STEEL_3)
        c.rect(ox, 4, ox + 5, 4, STEEL_1)
        c.set(ox + 2, 6, EMBER_3)               # ember vent
        c.set(ox + 3, 6, EMBER_2)
        c.set(ox + 2, 7, EMBER_1)
        c.rect(ox, 10, ox + 5, 11, STEEL_1)     # ankle
        c.rect(ox, 10, ox + 5, 10, STEEL_2)
        c.rect(ox, 12, ox + 6, 13, STEEL_1)     # foot, toe juts outward
        c.rect(ox, 12, ox + 6, 12, STEEL_2)
        c.rect(ox, 14, ox + 6, 14, VOID_1)      # sole
        c.set(ox + 6, 13, STEEL_0)
        c.set(ox, 13, STEEL_0)
        c.set(ox + 1, 11, STAR_1)               # starlight rivet
    c.set(0, 14, VOID_0)
    c.set(8, 14, VOID_0)
    return c

# --------------------------------------------------------------------------
# worn-armour layers (64x32, standard humanoid UV layout)
# --------------------------------------------------------------------------
def _armour_plate(img, x0, y0, x1, y1, seam=True, rng=None):
    px = img.load()
    rng = rng or random.Random(7)
    h = max(1, y1 - y0)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            t = (y - y0) / float(h)
            col = mix(STEEL_2, STEEL_0, t * 0.85)
            if (y - y0) % 4 == 0:                       # banding between plates
                col = shade(col, 0.72)
            elif (y - y0) % 4 == 1:
                col = shade(col, 1.12)
            if rng.random() < 0.07:                     # forge speckle
                col = shade(col, 0.85)
            px[x, y] = col
    mid = (x0 + x1) // 2
    if seam and x1 - x0 >= 3:                           # glowing centre seam
        for y in range(y0, y1 + 1):
            t = (y - y0) / float(h)
            px[mid, y] = mix(EMBER_3, EMBER_1, t)
    for y in range(y0 + 2, y1, 5):                      # rivets
        px[x0, y] = STEEL_3
        px[x1, y] = STEEL_3


def armour_layer(which):
    """which: 'humanoid' (helmet/chest/boots) or 'humanoid_leggings'."""
    img = Image.new("RGBA", (64, 32), CLEAR)
    rng = random.Random(41 if which == "humanoid" else 97)
    if which == "humanoid":
        _armour_plate(img, 0, 0, 31, 15, rng=rng)       # head -> helmet
        _armour_plate(img, 16, 16, 39, 31, rng=rng)     # body -> chestplate
        _armour_plate(img, 40, 16, 55, 31, rng=rng)     # arms -> chestplate
        _armour_plate(img, 0, 16, 15, 31, rng=rng)      # legs -> boots
        px = img.load()
        for x in range(8, 16):                          # helmet visor slit
            px[x, 11] = VOID_0
            px[x, 12] = STAR_1 if x % 2 else STAR_0
        for x in range(0, 16):                          # boot soles
            px[x, 31] = VOID_1
            px[x, 30] = VOID_2
    else:
        _armour_plate(img, 16, 16, 39, 31, rng=rng)     # waist
        _armour_plate(img, 0, 16, 15, 31, rng=rng)      # legs
        px = img.load()
        for x in range(16, 40):                         # belt line
            px[x, 17] = EMBER_2
            px[x, 18] = EMBER_0
    return img


# --------------------------------------------------------------------------
# paintings, GUI background, logo
# --------------------------------------------------------------------------
def _starfield(img, x0, y0, x1, y1, rng, top, bottom, density=0.06):
    px = img.load()
    h = max(1, y1 - y0)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            px[x, y] = mix(top, bottom, (y - y0) / float(h))
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if rng.random() < density:
                px[x, y] = rng.choice((WHITE, STAR_2, ARC_2, EMBER_4))


def painting_voidgate():
    img = Image.new("RGBA", (16, 16), CLEAR)
    rng = random.Random(3)
    _starfield(img, 0, 0, 15, 15, rng, VOID_2, VOID_0, density=0.03)
    px = img.load()
    for y in range(3, 13):                              # portal arch
        for x in range(4, 12):
            d = math.hypot((x - 7.5) / 3.6, (y - 8.0) / 4.6)
            if d <= 1.0:
                px[x, y] = mix(ARC_2, ARC_0, d)
            elif d <= 1.2:
                px[x, y] = VOID_3
    for x in range(1, 15):
        px[x, 14] = VOID_1
    return img


def painting_forgeheart():
    img = Image.new("RGBA", (32, 16), CLEAR)
    rng = random.Random(11)
    _starfield(img, 0, 0, 31, 15, rng, VOID_1, VOID_0, density=0.03)
    px = img.load()
    for y in range(9, 14):                              # anvil
        for x in range(9, 23):
            inset = {9: 0, 10: 1, 11: 3, 12: 3, 13: 1}[y]
            if 9 + inset <= x <= 22 - inset:
                px[x, y] = mix(STEEL_1, STEEL_0, (y - 9) / 4.0)
    for x in range(10, 22):
        px[x, 9] = STEEL_2
    for i in range(14):                                 # sparks rising
        px[10 + rng.randrange(12), 3 + rng.randrange(5)] = rng.choice(
            (EMBER_3, EMBER_4, EMBER_2))
    for x in range(13, 19):
        px[x, 8] = EMBER_3
    return img


def painting_starfall():
    img = Image.new("RGBA", (32, 32), CLEAR)
    rng = random.Random(23)
    _starfield(img, 0, 0, 31, 31, rng, VOID_2, VOID_0, density=0.025)
    px = img.load()
    for i in range(22):                                 # falling star with tail
        x, y = 24 - i, 2 + i
        if 0 <= x < 32 and 0 <= y < 32:
            col = EMBER_4 if i < 4 else (EMBER_3 if i < 10 else EMBER_1)
            px[x, y] = col
            if i < 12 and x + 1 < 32:
                px[x + 1, y] = shade(col, 0.6)
    for y in range(26, 32):                             # dark horizon
        for x in range(32):
            px[x, y] = mix(VOID_1, VOID_0, (y - 26) / 5.0)
    for x in range(32):
        px[x, 26] = ARC_0
    return img


def advancement_background():
    """16x16 tile used as the Starforge advancement tab backdrop."""
    img = Image.new("RGBA", (16, 16), CLEAR)
    rng = random.Random(59)
    px = img.load()
    for y in range(16):
        for x in range(16):
            n = rng.random()
            base = mix(VOID_2, VOID_0, (y / 15.0) * 0.6 + n * 0.4)
            px[x, y] = base
    for _ in range(7):
        px[rng.randrange(16), rng.randrange(16)] = rng.choice((STAR_1, ARC_1, EMBER_2))
    return img


def logo(size=256):
    """Square mod icon: a four-point starburst above a forge anvil.

    Drawn at 4x and downsampled so the curves survive at gallery size.
    """
    S = size * 4
    img = Image.new("RGBA", (S, S), CLEAR)
    px = img.load()
    cx = cy = S / 2.0
    R = S * 0.47
    corner = S * 0.17
    half = S / 2.0 - 1

    def inside_plate(x, y):
        dx, dy = abs(x - cx), abs(y - cy)
        if dx > half - corner and dy > half - corner:
            return math.hypot(dx - (half - corner), dy - (half - corner)) <= corner
        return dx <= half and dy <= half

    for y in range(S):                                   # night-sky plate
        for x in range(S):
            if not inside_plate(x, y):
                continue
            d = math.hypot(x - cx, y - cy) / R
            px[x, y] = mix(mix(VOID_3, VOID_1, min(1.0, d * 1.1)), VOID_0,
                           max(0.0, d - 0.5))

    rng = random.Random(1987)                            # starfield
    for _ in range(260):
        x, y = rng.randrange(S), rng.randrange(S)
        if not px[x, y][3]:
            continue
        r = rng.choice((1, 2, 2, 3))
        col = rng.choice((WHITE, STAR_2, ARC_2, EMBER_4))
        for oy in range(-r, r + 1):
            for ox in range(-r, r + 1):
                if math.hypot(ox, oy) <= r and 0 <= x + ox < S and 0 <= y + oy < S:
                    if px[x + ox, y + oy][3]:
                        px[x + ox, y + oy] = col

    sy = cy - R * 0.10                                   # starburst centre
    SR = R * 0.56
    P = 0.42                                             # <1 gives concave spikes
    for y in range(S):
        for x in range(S):
            if not px[x, y][3]:
                continue
            nx, ny = (x - cx) / SR, (y - sy) / SR
            v = abs(nx) ** P + abs(ny) ** P
            if v <= 1.0:
                d = min(1.0, math.hypot(nx, ny) / 0.42)
                col = mix(WHITE, mix(EMBER_4, EMBER_2, min(1.0, v)), d ** 0.7)
                if v > 0.93:                             # crisp rim
                    col = mix(col, EMBER_1, (v - 0.93) / 0.07)
                px[x, y] = col
            elif v <= 1.30:                              # outward glow
                px[x, y] = mix(px[x, y], EMBER_2, (1.30 - v) / 0.37 * 0.55)

    ay0, ay1 = cy + R * 0.44, cy + R * 0.88              # anvil silhouette
    for y in range(int(ay0), int(ay1)):
        t = (y - ay0) / (ay1 - ay0)
        if t < 0.24:
            hw = R * 0.44
        elif t < 0.58:
            hw = R * (0.44 - (t - 0.24) * 0.79)
        else:
            hw = R * (0.17 + (t - 0.58) * 0.60)
        for x in range(int(cx - hw), int(cx + hw) + 1):
            if 0 <= x < S and px[x, y][3]:
                px[x, y] = mix(VOID_0, VOID_2, max(0.0, 0.35 - t))
    glow = int(R * 0.030) or 1                           # hot top face
    for y in range(int(ay0), int(ay0) + glow):
        for x in range(int(cx - R * 0.44), int(cx + R * 0.44) + 1):
            if 0 <= x < S and px[x, y][3]:
                px[x, y] = EMBER_3
    for y in range(int(ay0) + glow, int(ay0) + glow * 2):
        for x in range(int(cx - R * 0.40), int(cx + R * 0.40) + 1):
            if 0 <= x < S and px[x, y][3]:
                px[x, y] = mix(EMBER_1, VOID_0, 0.4)

    for y in range(S):                                   # bevelled border
        for x in range(S):
            if not px[x, y][3]:
                continue
            dx, dy = abs(x - cx), abs(y - cy)
            edge = max(dx, dy)
            if edge > half - S * 0.026:
                px[x, y] = mix(px[x, y], STEEL_1, 0.60)
            elif edge > half - S * 0.042:
                px[x, y] = mix(px[x, y], VOID_0, 0.50)

    return img.resize((size, size), Image.LANCZOS)

# --------------------------------------------------------------------------
def main():
    items = {
        "starfall_blade": starfall_blade(),
        "worldbreaker": worldbreaker(),
        "starforge_pickaxe": starforge_pickaxe(),
        "voidpiercer": voidpiercer(-1),
        "voidpiercer_pulling_0": voidpiercer(0),
        "voidpiercer_pulling_1": voidpiercer(1),
        "voidpiercer_pulling_2": voidpiercer(2),
        "emberbrand": emberbrand(),
        "starsteel_shard": starsteel_shard(),
        "starforge_codex": starforge_codex(),
        "starsteel_ingot": starsteel_ingot(),
        "voidshard": voidshard(),
        "astral_core": astral_core(),
        "astral_elixir": astral_elixir(),
        "heart_of_the_star": heart_of_the_star(),
        "starforge_helmet": starforge_helmet(),
        "starforge_chestplate": starforge_chestplate(),
        "starforge_leggings": starforge_leggings(),
        "starforge_boots": starforge_boots(),
    }
    written = []
    for name, canvas in items.items():
        written.append(canvas.save("item", name + ".png"))

    def put(img, *parts):
        path = os.path.join(TEX, *parts)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        img.save(path)
        written.append(path)

    put(armour_layer("humanoid"), "entity", "equipment", "humanoid", "starforge.png")
    put(armour_layer("humanoid_leggings"), "entity", "equipment",
        "humanoid_leggings", "starforge.png")
    put(painting_voidgate(), "painting", "voidgate.png")
    put(painting_forgeheart(), "painting", "forgeheart.png")
    put(painting_starfall(), "painting", "starfall.png")
    put(advancement_background(), "gui", "advancements", "backgrounds", "starforge.png")

    icon = logo(256)
    icon_path = os.path.join(ROOT, "src/main/resources/assets/starforge/icon.png")
    os.makedirs(os.path.dirname(icon_path), exist_ok=True)
    icon.save(icon_path)
    written.append(icon_path)

    for p in written:
        print("  wrote", os.path.relpath(p, ROOT))
    print(f"{len(written)} textures generated")


if __name__ == "__main__":
    main()
