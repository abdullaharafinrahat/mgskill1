"""Font resolution.

The renderer needs three things from a typeface: a geometric sans for
display type, a script-appropriate face for non-Latin text, and the ability
to hit a specific weight. Modern Google Fonts ships variable fonts, so one
file covers Regular through Black - we set the weight axis instead of
shipping nine files.

Script coverage matters more than it sounds. A Bengali promo rendered in a
Latin face gets tofu boxes, and a 1080p deliverable full of squares is
unusable. `resolve_fonts` therefore prefers a script face whenever the
storyboard declares one.
"""
import os

from PIL import ImageFont

# role -> (filename, weight)
CORE_ROLES = {
    "regular": ("Inter-Variable.ttf", 400),
    "medium": ("Inter-Variable.ttf", 500),
    "semibold": ("Inter-Variable.ttf", 600),
    "bold": ("Inter-Variable.ttf", 700),
    "black": ("Inter-Variable.ttf", 900),
    "display": ("Inter-Variable.ttf", 900),
    "caption": ("Inter-Variable.ttf", 500),
}

SCRIPT_ROLES = {
    "bengali": ("NotoSansBengali.ttf", 400),
    "bengali_bold": ("NotoSansBengali.ttf", 700),
    "devanagari": ("NotoSansDevanagari.ttf", 400),
    "devanagari_bold": ("NotoSansDevanagari.ttf", 700),
    "arabic": ("NotoSansArabic.ttf", 400),
    "arabic_bold": ("NotoSansArabic.ttf", 700),
    "cjk": ("NotoSansCJK.ttc", 400),
}

SYSTEM_FALLBACK = {
    "regular": ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
    "medium": ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
    "semibold": ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    "bold": ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    "black": ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    "display": ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    "caption": ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
}

_CACHE = {}


def make_font(path, px, weight=400):
    """Open a typeface at `px` and, if it is variable, set the weight axis.

    Axis names arrive as bytes ('b'Weight'') for the Google Fonts variable
    faces and as plain strings for the OpenType-standard ones ('wght'), so
    both spellings are matched. Noto Sans Bengali for instance exposes
    'Weight' and 'Width'; Inter exposes 'wght' and 'opsz'."""
    key = (path, int(px), int(weight))
    if key in _CACHE:
        return _CACHE[key]
    f = ImageFont.truetype(path, int(px))
    try:
        axes = f.get_variation_axes()
        names = []
        for a in axes:
            nm = a.get("name")
            if isinstance(nm, bytes):
                nm = nm.decode("utf-8", "ignore")
            names.append((nm or "").lower())
        if any(n in ("wght", "weight") for n in names):
            vals = []
            for a, nm in zip(axes, names):
                if nm in ("wght", "weight"):
                    vals.append(float(weight))
                elif nm in ("opsz", "opticalsize"):
                    vals.append(float(weight))
                else:
                    vals.append(float(a.get("default", 0)))
            f.set_variation_by_axes(vals)
    except Exception:
        pass
    _CACHE[key] = f
    return f


def resolve_fonts(fonts_dir, overrides=None):
    """Build the theme's FONTS table: role -> (path, weight)."""
    table = {}
    for role, (fname, weight) in CORE_ROLES.items():
        p = os.path.join(fonts_dir, fname)
        if os.path.exists(p):
            table[role] = (p, weight)
        else:
            for cand in SYSTEM_FALLBACK.get(role, []):
                if os.path.exists(cand):
                    table[role] = (cand, 400)
                    break
    for role, (fname, weight) in SCRIPT_ROLES.items():
        p = os.path.join(fonts_dir, fname)
        if os.path.exists(p):
            table[role] = (p, weight)
    for role, spec in (overrides or {}).items():
        if isinstance(spec, str):
            p = spec
            w = 400
        elif isinstance(spec, (list, tuple)) and spec:
            p, w = spec[0], (spec[1] if len(spec) > 1 else 400)
        else:
            continue
        if p and os.path.exists(p):
            table[role] = (p, w)
    if "bold" not in table and "regular" in table:
        table["bold"] = table["regular"]
    if "regular" not in table and "bold" in table:
        table["regular"] = table["bold"]
    return table


def font_for(table, role):
    """Look up a role, degrading bold -> regular -> anything."""
    if not table:
        return None
    for key in (role, role + "_bold", "bold", "regular", "display"):
        if key in table:
            return table[key]
    return next(iter(table.values()), None)


def script_for_language(lang):
    """Map a language code to a script role, so the storyboard can just say
    "language": "bn" and get a Bengali face."""
    lang = (lang or "").lower()
    if lang.startswith("bn") or lang in ("bengali", "bangla"):
        return "bengali"
    if lang.startswith("hi") or lang in ("hindi", "marathi", "ne"):
        return "devanagari"
    if lang.startswith("ar") or lang in ("arabic", "urdu", "fa", "persian"):
        return "arabic"
    if lang.startswith("zh") or lang.startswith("ja") or lang.startswith("ko"):
        return "cjk"
    return None
