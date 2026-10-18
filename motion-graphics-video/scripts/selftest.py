#!/usr/bin/env python3
"""Smoke-test the renderer before you commit to a long render.

    python scripts/selftest.py

Checks that every module imports, that the typefaces are present and can
shape a complex script, that each component renders to a non-empty image,
and that a two-shot storyboard renders end to end into a playable mp4.
Takes about ten seconds.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

fails = []


def check(name, fn):
    try:
        msg = fn()
        print(f"  PASS  {name}" + (f"  ({msg})" if msg else ""))
    except Exception as e:
        print(f"  FAIL  {name}: {e}")
        fails.append(name)


def t_imports():
    from mgv import easing, theme, draw, components, layers, render, storyboard, fonts
    return f"mgv {render.__dict__.get('__name__', '')} ok"


def t_fonts():
    from mgv import fonts as F
    d = os.path.join(os.path.dirname(HERE), "assets", "fonts")
    tbl = F.resolve_fonts(d)
    if "bold" not in tbl:
        raise RuntimeError("no Latin face found - run fetch_fonts.py")
    spec = F.font_for(tbl, "bold")
    f = F.make_font(spec[0], 48, spec[1])
    bb = f.getbbox("Ag")
    if bb[2] <= 0:
        raise RuntimeError("font produced no glyphs")
    return f"{os.path.basename(spec[0])}"


def t_raqm():
    from PIL import features
    ok = features.check("raqm")
    if not ok:
        raise RuntimeError(
            "Pillow has no Raqm - Bengali/Arabic will render as empty boxes. "
            "Install a Pillow build with libraqm.")
    return "raqm on"


def t_bengali():
    from mgv import fonts as F
    d = os.path.join(os.path.dirname(HERE), "assets", "fonts")
    tbl = F.resolve_fonts(d)
    if "bengali" not in tbl:
        raise RuntimeError("no Bengali face - run fetch_fonts.py --all-scripts")
    from PIL import Image, ImageDraw
    spec = tbl["bengali"]
    f = F.make_font(spec[0], 48, spec[1])
    img = Image.new("L", (600, 100), 0)
    d2 = ImageDraw.Draw(img)
    d2.text((10, 10), "ভিডিও এডিটিং ২২", font=f, fill=255)
    if img.getbbox() is None:
        raise RuntimeError("Bengali rendered as nothing")
    return "shaped ok"


def t_components():
    from mgv import theme as T, components as C, fonts as F
    d = os.path.join(os.path.dirname(HERE), "assets", "fonts")
    th = T.theme_from_dict({})
    th["FONTS"] = F.resolve_fonts(d)
    f = F.make_font(F.font_for(th["FONTS"], "bold")[0], 40, 700)
    checks = [
        ("pill", lambda: C.pill(th, (400, 60), text="TEST", font=f)),
        ("bubble", lambda: C.bubble(th, (400, 140), text="Hello there", font=f)),
        ("card", lambda: C.card(th, (300, 200))),
        ("avatar", lambda: C.avatar(th, (120, 120))),
        ("label", lambda: C.label_pill(th, (300, 60), text="LBL", font=f)),
        ("cursor", lambda: C.cursor(th, (80, 80))),
        ("monitor", lambda: C.monitor(th, (400, 280))),
        ("circuit", lambda: C.circuit(th, (400, 300))),
        ("numeral", lambda: C.numeral(th, (400, 280), text="1500+", font=f)),
        ("sparkles", lambda: C.sparkles(th, (300, 300))),
        ("graph", lambda: C.line_graph(th, (300, 160))),
        ("icon", lambda: C.icon_tile(th, (160, 160), glyph="Ae", font=f)),
        ("phone", lambda: C.phone(th, (160, 300))),
    ]
    for name, fn in checks:
        im = fn()
        if im.size[0] < 4 or im.size[1] < 4:
            raise RuntimeError(f"{name} produced a degenerate image")
    return f"{len(checks)} components"


def t_ffmpeg():
    from mgv import render as R
    return os.path.basename(R.find_ffmpeg())


def t_render():
    from mgv import render as R
    sb = {
        "meta": {"title": "selftest", "language": "en"},
        "acts": [{"id": "hook", "name": "Hook", "goal": "x"},
                 {"id": "offer", "name": "Offer", "goal": "x"}],
        "shots": [
            {"id": "s01", "act": "hook", "visual": "graphics", "purpose": "test",
             "duration": 0.6, "cta": False, "voice": "one two three",
             "layers": [
                 {"type": "bg", "style": "bokeh", "base": "#070E1E"},
                 {"type": "text", "text": "SELFTEST", "x": 0.5, "y": 0.45,
                  "size": 0.08, "weight": "black", "color": "#EEF2F4",
                  "in": {"type": "wipe_bars", "dur": 0.2}},
                 {"type": "pill", "text": "OK", "gradient": "azure_blue",
                  "x": 0.5, "y": 0.7, "w": 0.25, "h": 0.08,
                  "in": {"type": "pop", "dur": 0.25, "delay": 0.2}},
             ]},
            {"id": "s02", "act": "offer", "visual": "graphics",
             "purpose": "test", "duration": 0.6, "cta": True,
             "voice": "four five six",
             "layers": [
                 {"type": "bg", "style": "radial", "inner": "#072B6D",
                  "outer": "#070E1E"},
                 {"type": "numeral", "text": "22", "gradient": "green_lime",
                  "x": 0.5, "y": 0.45, "w": 0.4, "h": 0.4,
                  "in": {"type": "pop", "dur": 0.3, "ease": "elastic"}},
             ]},
        ],
    }
    tmp = tempfile.mkdtemp(prefix="mgv_selftest_")
    out = os.path.join(tmp, "out.mp4")
    r = R.Renderer(sb, out, width=640, height=360, fps=12, workdir=tmp)
    r.render()
    if not os.path.exists(out) or os.path.getsize(out) < 1000:
        raise RuntimeError("no output produced")
    return f"{os.path.getsize(out) // 1024} KB"


def t_validator():
    from mgv import storyboard as SB
    sb = SB.normalise({
        "acts": [{"id": "hook"}],
        "shots": [{"id": "s01", "act": "hook", "duration": 1.0,
                   "layers": [], "voice": "x"}]})
    issues = SB.validate(sb)
    if not any(i.code == "ACTS_TOO_FEW" for i in issues):
        raise RuntimeError("the validator did not catch a one-act storyboard")
    if not any(i.code == "NO_CTA" for i in issues):
        raise RuntimeError("the validator did not catch a missing CTA")
    return f"{len(issues)} faults found (as expected)"


def main():
    print("motion-graphics-video selftest")
    print("-" * 60)
    check("modules import", t_imports)
    check("ffmpeg available", t_ffmpeg)
    check("typeface present", t_fonts)
    check("complex-script shaping", t_raqm)
    check("Bengali renders", t_bengali)
    check("component kit", t_components)
    check("validator catches faults", t_validator)
    check("end-to-end render", t_render)
    print("-" * 60)
    if fails:
        print(f"{len(fails)} check(s) failed: {', '.join(fails)}")
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
