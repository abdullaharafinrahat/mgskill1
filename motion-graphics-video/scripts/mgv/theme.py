"""The design system: palette, gradients, type scale, and the reusable asset
kit definitions.

Everything here is measured from a real high-end motion-graphics promo
(reference: "push.mp4", 2560x1440, 78 detected segments). The numbers are
not arbitrary - they are the values that survived analysis of 3,526 decoded
frames.

The core insight the palette encodes: the piece is *bottom-heavy in value*.
Over half the frame area sits below 0.25 luma, and the only saturated
colours are the accents. That is what makes flat vector graphics read as
expensive on a phone screen.
"""

# --------------------------------------------------------------------------
# Core palette
# --------------------------------------------------------------------------

VOID = (0x07, 0x0E, 0x1E)          # 29.4% of the reference film - the "void"
NAVY = (0x07, 0x2B, 0x6D)          # royal ultramarine - panels, chrome
CHARCOAL = (0x49, 0x41, 0x42)      # warm charcoal - the presenter / 3D rooms
PAPER = (0xEE, 0xF2, 0xF4)         # paper white - type, clean surfaces
TAUPE = (0x91, 0x83, 0x77)         # warm sand - skin, beige walls
ELECTRIC = (0x0C, 0x4D, 0xC6)      # THE signature accent
SKY = (0x60, 0xA2, 0xF0)           # gradient midpoints, glass edges
STEEL = (0xBE, 0xBE, 0xB5)         # neutral grey-green

# Semantic accents - the film uses colour to mean something, so keep it
# consistent and the meaning is free.
GREEN = (0x1F, 0xBF, 0x5A)         # earnings / proof / success
LIME = (0xC6, 0xF2, 0x3C)          # a service tier / a module
CRIMSON = (0xE0, 0x3A, 0x4E)       # wrong / warning / anti-pattern
PINK = (0xC4, 0x4B, 0xC8)          # a second-tier offering
PERIWINKLE = (0x7C, 0x8C, 0xE8)    # colour grading / a third service
TEAL = (0x2E, 0x6E, 0x63)         # storytelling
VIOLET = (0x7A, 0x3C, 0xFF)        # title-card sheen, icon stack
PURPLE_CURSOR = (0xB9, 0x8C, 0xFF)

# --------------------------------------------------------------------------
# Gradients - all linear, none are mesh, all lit from above
# --------------------------------------------------------------------------

GRADIENTS = {
    "azure_ramp": [(0x00, 0x1F, 0x5F), (0x00, 0x3F, 0xBF)],
    "azure_cyan": [(0x0C, 0x4D, 0xC6), (0x60, 0xA2, 0xF0)],
    "magenta_blue": [(0xC4, 0x4B, 0xC8), (0x3A, 0x6F, 0xD8)],
    "teal_lime": [(0x2E, 0x6E, 0x63), (0xC6, 0xF2, 0x3C)],
    "blue_lime": [(0x4F, 0xA8, 0xE8), (0x9B, 0xE8, 0x4A)],
    "green_lime": [(0x1F, 0xBF, 0x5A), (0xC6, 0xF2, 0x3C)],
    "azure_black": [(0x1A, 0x5F, 0xB4), (0x05, 0x07, 0x0E)],
    "green_black": [(0x1F, 0xBF, 0x5A), (0x03, 0x15, 0x0A)],
    "violet_black": [(0x7A, 0x3C, 0xFF), (0x0A, 0x07, 0x14)],
    "paper_sky": [(0xEE, 0xF2, 0xF4), (0x60, 0xA2, 0xF0)],
}

# --------------------------------------------------------------------------
# Type scale (fractions of frame height, for a 1080p master)
# --------------------------------------------------------------------------

TYPE_SCALE = {
    "hero": 0.235,       # the "22" / "1500+" numerals
    "display": 0.105,    # section headlines
    "headline": 0.072,   # the main on-screen line
    "subhead": 0.052,    # supporting line
    "pill": 0.038,       # label inside a gradient pill
    "body": 0.030,       # chat bubbles, captions
    "micro": 0.022,      # badges, corner labels
    "caption": 0.042,    # burned-in subtitles
}

# --------------------------------------------------------------------------
# Geometry
# --------------------------------------------------------------------------

RADIUS = {
    "pill": 999,        # fully rounded
    "card": 28,
    "bubble": 32,
    "monitor": 18,
    "label": 18,
}

SS = 2  # supersampling factor: render at 2x then downscale for clean edges


def hexc(s):
    """'#0C4DC6' or '0C4DC6' -> (12, 77, 198)."""
    s = s.lstrip("#")
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def parse_color(v, default=(255, 255, 255)):
    """Accept '#RRGGBB', 'RRGGBB', [r,g,b] or (r,g,b) and return a tuple.

    Storyboards are written by a language model, so hex strings are the
    natural thing for it to produce. Accepting them here means the author
    never has to think about it."""
    if v is None:
        return default
    if isinstance(v, (list, tuple)):
        if len(v) >= 3:
            try:
                return (int(v[0]), int(v[1]), int(v[2]))
            except (TypeError, ValueError):
                return default
        return default
    if isinstance(v, str):
        s = v.strip().lstrip("#")
        if len(s) in (6, 8):
            try:
                return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))
            except ValueError:
                return default
    return default


def parse_stops(v, default=None):
    """Parse a list of colour stops into RGB tuples."""
    if not v:
        return default
    out = []
    for item in v:
        if isinstance(item, (list, tuple)) and len(item) >= 3:
            out.append(parse_color(item))
        else:
            out.append(parse_color(item))
    return out


# short alias used everywhere in the renderer
C = parse_color


def mix(a, b, t):
    """Linear blend between two RGB tuples."""
    t = max(0.0, min(1.0, t))
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def theme_from_dict(d):
    """Allow a storyboard to override any palette entry by name, e.g.
    {"theme": {"ELECTRIC": "#FF0055", "GRADIENTS": {"azure_ramp": ["#04080F", "#0A1A3C"]}}}
    """
    out = dict(globals())
    for key, val in (d or {}).items():
        if key == "GRADIENTS" and isinstance(val, dict):
            g = dict(GRADIENTS)
            for gk, gv in val.items():
                g[gk] = [hexc(gv[0])] + [hexc(x) for x in gv[1:]] if isinstance(gv, (list, tuple)) else gv
            out["GRADIENTS"] = g
        elif isinstance(val, str) and key.isupper():
            out[key] = hexc(val)
    return out
