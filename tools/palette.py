"""Shared colour palette and pixel-art helpers for the Starforge asset pipeline.

Everything the mod ships as art is generated from this module so the whole
asset set stays on one palette: void indigo for the body of an object, starsteel
blue for metal, ember gold for heat and starlight cyan for the magic.
"""

# --- core palette -----------------------------------------------------------
VOID_0 = (14, 8, 28, 255)
VOID_1 = (27, 16, 51, 255)
VOID_2 = (46, 27, 91, 255)
VOID_3 = (67, 42, 127, 255)

STEEL_0 = (58, 68, 104, 255)
STEEL_1 = (110, 127, 184, 255)
STEEL_2 = (159, 180, 232, 255)
STEEL_3 = (214, 228, 255, 255)

EMBER_0 = (94, 43, 12, 255)
EMBER_1 = (138, 75, 18, 255)
EMBER_2 = (217, 131, 36, 255)
EMBER_3 = (255, 184, 77, 255)
EMBER_4 = (255, 233, 168, 255)

STAR_0 = (31, 122, 140, 255)
STAR_1 = (63, 208, 216, 255)
STAR_2 = (168, 255, 245, 255)

ARC_0 = (120, 47, 168, 255)
ARC_1 = (179, 63, 208, 255)
ARC_2 = (232, 140, 255, 255)

WHITE = (255, 255, 255, 255)
CLEAR = (0, 0, 0, 0)

# Legend shared by every ASCII sprite below.
LEGEND = {
    ".": CLEAR,
    "0": VOID_0, "1": VOID_1, "2": VOID_2, "3": VOID_3,
    "a": STEEL_0, "b": STEEL_1, "c": STEEL_2, "d": STEEL_3,
    "e": EMBER_0, "f": EMBER_1, "g": EMBER_2, "h": EMBER_3, "i": EMBER_4,
    "p": STAR_0, "q": STAR_1, "r": STAR_2,
    "u": ARC_0, "v": ARC_1, "w": ARC_2,
    "W": WHITE,
}


def sprite(rows, legend=None):
    """Turn a list of equal-length strings into a list of RGBA rows."""
    legend = legend or LEGEND
    out = []
    for y, row in enumerate(rows):
        line = []
        for x, ch in enumerate(row):
            if ch not in legend:
                raise KeyError(f"unknown glyph {ch!r} at ({x},{y})")
            line.append(legend[ch])
        out.append(line)
    return out


def write_sprite(img, rows, ox=0, oy=0, legend=None):
    """Blit an ASCII sprite onto a PIL image, skipping transparent glyphs."""
    px = img.load()
    for y, line in enumerate(sprite(rows, legend)):
        for x, col in enumerate(line):
            if col[3]:
                px[ox + x, oy + y] = col
