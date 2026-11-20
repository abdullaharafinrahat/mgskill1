"""Script 3: 2D vector drawing library on pycairo (shapes, camera, Bengali text via PIL/raqm, rigged characters, props)."""
import cairo, math, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FD = "/usr/share/fonts/truetype/noto/"
_dj = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BEN = {"bold": FD + "NotoSansBengali-Bold.ttf", "reg": FD + "NotoSansBengali-Regular.ttf", "serif": FD + "NotoSerifBengali-Bold.ttf"}
LAT = {"bold": FD + "NotoSans-Bold.ttf", "reg": FD + "NotoSans-Regular.ttf", "serif": FD + "NotoSerif-Bold.ttf"}
for d in (BEN, LAT):
    for k, v in d.items():
        if not os.path.exists(v): d[k] = _dj

# ------------------------------------------------------------------ colour / math
def hexc(h, a=1.0):
    h = h.lstrip('#'); h = ''.join(ch*2 for ch in h) if len(h)==3 else h; return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)
def shade(col, f):  # f<1 darker, f>1 lighter
    r, g, b = col[:3]
    if f <= 1: return (r * f, g * f, b * f, col[3] if len(col) > 3 else 1)
    f = f - 1; return (r + (1 - r) * f, g + (1 - g) * f, b + (1 - b) * f, col[3] if len(col) > 3 else 1)
def alpha(col, a): return (col[0], col[1], col[2], a)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def lerp(a, b, t): return a + (b - a) * t
def prog(t, a, b): return 1.0 if b <= a and t >= b else (0.0 if b <= a else clamp((t - a) / (b - a)))
def e_out(x): return 1 - (1 - x) ** 3
def e_in(x): return x ** 3
def e_io(x): return x * x * x * (x * (6 * x - 15) + 10)
def e_back(x):
    c1 = 1.70158; c3 = c1 + 1; return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def e_elastic(x):
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    return 2 ** (-9 * x) * math.sin((x * 10 - 0.75) * (2 * math.pi) / 3) + 1
def bn(n):
    return str(n).translate(str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯"))
def rnd(i, k=0):
    x = math.sin(i * 12.9898 + k * 78.233) * 43758.5453; return x - math.floor(x)

# ------------------------------------------------------------------ basic drawing
def setc(c, col):
    if isinstance(col, cairo.Pattern): c.set_source(col)
    elif len(col) == 3: c.set_source_rgb(*col)
    else: c.set_source_rgba(*col)
def _fs(c, col, stroke=None, sw=0):
    if col is not None:
        setc(c, col)
        if stroke is not None and sw > 0: c.fill_preserve()
        else: c.fill()
    if stroke is not None and sw > 0:
        setc(c, stroke); c.set_line_width(sw); c.stroke()
    elif col is None: c.new_path()
def rrect_path(c, x, y, w, h, r):
    r = max(0, min(r, abs(w) / 2, abs(h) / 2)); c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0); c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi); c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi); c.close_path()
def rect(c, x, y, w, h, col, r=0, stroke=None, sw=0):
    c.new_path()
    if r > 0: rrect_path(c, x, y, w, h, r)
    else: c.rectangle(x, y, w, h)
    _fs(c, col, stroke, sw)
def circ(c, x, y, r, col, stroke=None, sw=0):
    c.new_path(); c.arc(x, y, max(r, 0.01), 0, 2 * math.pi); _fs(c, col, stroke, sw)
def ell(c, x, y, rx, ry, col, rot=0, stroke=None, sw=0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(max(rx, 0.01), max(ry, 0.01)); c.new_path(); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()
    _fs(c, col, stroke, sw)
def poly(c, pts, col, stroke=None, sw=0, close=True):
    c.new_path(); c.move_to(*pts[0])
    for p in pts[1:]: c.line_to(*p)
    if close: c.close_path()
    _fs(c, col, stroke, sw)
def line(c, x1, y1, x2, y2, w, col, cap=cairo.LINE_CAP_ROUND):
    c.new_path(); c.move_to(x1, y1); c.line_to(x2, y2); c.set_line_cap(cap); c.set_line_width(w); setc(c, col); c.stroke()
def arc_stroke(c, x, y, r, a1, a2, w, col):
    c.new_path(); c.arc(x, y, r, a1, a2); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_width(w); setc(c, col); c.stroke()
def vgrad(top, bot, y0=0, y1=H):
    p = cairo.LinearGradient(0, y0, 0, y1); p.add_color_stop_rgba(0, *top); p.add_color_stop_rgba(1, *bot); return p
def lgrad(x0, y0, x1, y1, stops):
    p = cairo.LinearGradient(x0, y0, x1, y1)
    for o, col in stops: p.add_color_stop_rgba(o, *(col if len(col) == 4 else col + (1,)))
    return p
def glow(c, x, y, r, col, a=0.6):
    p = cairo.RadialGradient(x, y, 0, x, y, r); p.add_color_stop_rgba(0, col[0], col[1], col[2], a); p.add_color_stop_rgba(1, col[0], col[1], col[2], 0)
    c.new_path(); c.arc(x, y, r, 0, 2 * math.pi); c.set_source(p); c.fill()
def world(c, col): rect(c, -2500, -2500, 6100, 7000, col)
def star(c, x, y, r, col, rot=0):
    c.save(); c.translate(x, y); c.rotate(rot)
    poly(c, [(0, -r), (r * .22, -r * .22), (r, 0), (r * .22, r * .22), (0, r), (-r * .22, r * .22), (-r, 0), (-r * .22, -r * .22)], col); c.restore()
def rays(c, cx, cy, n, col, rot, r0=0, r1=2400):
    for i in range(n):
        a = rot + i * 2 * math.pi / n; w = math.pi / n * 0.55
        poly(c, [(cx + r0 * math.cos(a), cy + r0 * math.sin(a)), (cx + r1 * math.cos(a - w), cy + r1 * math.sin(a - w)), (cx + r1 * math.cos(a + w), cy + r1 * math.sin(a + w))], col)
def dust(c, g, n=26, col=(1, 1, 1, .35), speed=14, size=5):
    for i in range(n):
        x = (rnd(i) * W + 30 * math.sin(g * .4 + i)) % W; y = (rnd(i, 3) * H - g * speed * (.5 + rnd(i, 5))) % H
        circ(c, x, y, size * (.4 + rnd(i, 7)), col)
def vignette(c, a=0.45, col=(0.08, 0.04, 0.02)):
    p = cairo.RadialGradient(W / 2, H / 2, 560, W / 2, H / 2, 1250); p.add_color_stop_rgba(0, *col, 0); p.add_color_stop_rgba(1, *col, a)
    c.set_source(p); c.rectangle(0, 0, W, H); c.fill()

# ------------------------------------------------------------------ camera
def cam(c, t, keys, g=0.0, shake=2.5):
    if t <= keys[0][0]: k = keys[0][1:]
    elif t >= keys[-1][0]: k = keys[-1][1:]
    else:
        for i in range(len(keys) - 1):
            if keys[i][0] <= t <= keys[i + 1][0]:
                u = e_io(prog(t, keys[i][0], keys[i + 1][0])); k = [lerp(a, b, u) for a, b in zip(keys[i][1:], keys[i + 1][1:])]; break
    cx, cy, z, r = k
    cx += shake * (math.sin(g * 1.3) + .5 * math.sin(g * 2.9 + 1)); cy += shake * (math.cos(g * 1.1) + .5 * math.sin(g * 3.3))
    c.translate(W / 2, H / 2); c.rotate(math.radians(r)); c.scale(z, z); c.translate(-cx, -cy)

# ------------------------------------------------------------------ text (PIL + raqm -> cairo surfaces)
_fc = {}; _tc = {}
def _font(path, size):
    k = (path, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)
    return _fc[k]
def _runs(s):
    runs = []
    for ch in s:
        lat = (ch.isascii() or ch in "“”‘’—–…") and not ch.isspace()
        if runs and (ch.isspace() or runs[-1][0] == lat): runs[-1][1] += ch
        else: runs.append([lat, ch])
    return runs
def _tsurf(s, px, col, kind, stroke, spx):
    key = (s, px, col, kind, stroke, spx)
    if key in _tc: return _tc[key]
    runs = _runs(s); fonts = []; wsum = 0; asc = 0; desc = 0
    for lat, r in runs:
        f = _font((LAT if lat else BEN)[kind], px); fonts.append(f); wsum += f.getlength(r)
        a, d = f.getmetrics(); asc = max(asc, a); desc = max(desc, d)
    pad = int(spx) + 4; w = int(wsum) + pad * 2 + 2; h = asc + desc + pad * 2
    base = (stroke or col)
    img = Image.new("RGBA", (w, h), tuple(int(v * 255) for v in base[:3]) + (0,)); d = ImageDraw.Draw(img)
    x = pad; fill = tuple(int(v * 255) for v in col[:3]) + (255,)
    for (lat, r), f in zip(runs, fonts):
        kw = {}
        if stroke and spx > 0: kw = dict(stroke_width=int(spx), stroke_fill=tuple(int(v * 255) for v in stroke[:3]) + (255,))
        d.text((x, pad + asc), r, font=f, fill=fill, anchor="ls", **kw); x += f.getlength(r)
    arr = np.asarray(img, dtype=np.uint16); out = np.empty((h, w, 4), np.uint8); a = arr[..., 3]
    out[..., 0] = arr[..., 2] * a // 255; out[..., 1] = arr[..., 1] * a // 255; out[..., 2] = arr[..., 0] * a // 255; out[..., 3] = a
    buf = bytearray(out.tobytes()); sf = cairo.ImageSurface.create_for_data(buf, cairo.FORMAT_ARGB32, w, h, w * 4)
    if len(_tc) > 900: _tc.clear()
    _tc[key] = (sf, buf, w, h, pad); return _tc[key]
def text_size(s, size, kind="bold"):
    runs = _runs(s); w = 0
    for lat, r in runs: w += _font((LAT if lat else BEN)[kind], int(size)).getlength(r)
    return w, size * 1.45
def text(c, s, x, y, size, col=(1, 1, 1, 1), kind="bold", anchor="c", a=1.0, stroke=None, sw=0, rot=0, sx=1.0, sy=None, lh=1.32):
    lines = s.split("\n"); m = c.get_matrix(); k = math.hypot(m.xx, m.yx)
    if k < 0.03 or abs(sx) < 0.02 or (sy is not None and abs(sy) < 0.02): return
    sc = clamp(round(k / 0.25) * 0.25, 0.5, 3.0); sy = sx if sy is None else sy
    n = len(lines)
    for i, ln in enumerate(lines):
        if not ln: continue
        sf, buf, w, h, pad = _tsurf(ln, max(8, int(round(size * sc))), tuple(col[:3]), kind, tuple(stroke[:3]) if stroke else None, sw * sc)
        c.save(); c.translate(x, y + (i - (n - 1) / 2) * size * lh); c.rotate(rot); c.scale(sx, sy); c.scale(1 / sc, 1 / sc)
        ox = -w / 2 if anchor == "c" else (-pad if anchor == "l" else -w + pad)
        c.set_source_surface(sf, ox, -h / 2); c.get_source().set_filter(cairo.FILTER_BILINEAR)
        c.paint_with_alpha(a * (col[3] if len(col) > 3 else 1)); c.restore()

# ------------------------------------------------------------------ people
SKIN = {"a": hexc("#D9A273"), "b": hexc("#C68B5C"), "c": hexc("#E6B68A"), "d": hexc("#B87A4E")}
def _ik(sx, sy, tx, ty, l1, l2, side):
    dx, dy = tx - sx, ty - sy; d0 = math.hypot(dx, dy); d = max(abs(l1 - l2) + 1, min(d0, l1 + l2 - .5)); base = math.atan2(dy, dx)
    A = math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1)); best = None
    for sg in (1, -1):
        a = base + sg * A; ex, ey = sx + l1 * math.cos(a), sy + l1 * math.sin(a); sc = ex * side + ey * .3
        if best is None or sc > best[0]: best = (sc, ex, ey)
    return best[1], best[2], sx + d * math.cos(base), sy + d * math.sin(base)

def person(c, x, y, s=1.0, skin=None, hair="#1b1411", shirt="#C8892B", pants="#3a2e27", style="short", outfit="shirt",
           mouth="flat", talk=0.0, brow="flat", look=0.0, blink=0.0, lean=0.0, tilt=0.0, hl=(-128, -10), hr=(128, -10),
           back=False, legs=False, walk=0.0, bob=0.0, flip=False, sweat=0.0, beard=None, glasses=False, sleeve="short",
           hold_l=None, hold_r=None, blush=0.0, hair2=None):
    skin = skin or SKIN["a"]; hair = hexc(hair) if isinstance(hair, str) else hair; shirtc = hexc(shirt) if isinstance(shirt, str) else shirt
    pantsc = hexc(pants) if isinstance(pants, str) else pants
    c.save(); c.translate(x, y); c.scale(-s if flip else s, s)
    skin_d = shade(skin, .86)
    # shadow-less legs
    if legs:
        for sd, ph in ((-1, 0), (1, math.pi)):
            sw_ = math.sin(walk + ph) * .45 if walk else 0
            c.save(); c.translate(sd * 46, -5); c.rotate(sw_)
            if outfit == "uniform":
                rect(c, -26, 60, 52, 280, skin, 22); rect(c, -26, 250, 52, 90, hexc("#f4f0e6"), 8); ell(c, sd * 6, 345, 46, 24, hexc("#1c1a18"))
            elif outfit == "kurta":
                rect(c, -34, 100, 68, 245, hexc("#EFE9DA"), 28); ell(c, sd * 8, 350, 46, 22, hexc("#2d241d"))
            else:
                rect(c, -36, 0, 72, 345, pantsc, 30); ell(c, sd * 8, 350, 50, 24, hexc("#241b16"))
            c.restore()
    c.translate(0, bob); c.rotate(lean)
    # back arm layer for hands handled after torso
    if outfit == "kurta":
        rect(c, -105, -245, 210, 440, shirtc, 60); rect(c, -105, 40, 210, 155, shade(shirtc, .93), 26)
    else:
        rect(c, -102, -245, 204, 262, shirtc, 62)
    if outfit == "uniform":
        poly(c, [(-102, -40), (102, -40), (125, 110), (-125, 110)], hexc("#3F6B3A")); rect(c, -102, -245, 204, 205, hexc("#F5F1E6"), 62)
        rect(c, -102, -80, 204, 60, hexc("#F5F1E6")); poly(c, [(-52, -245), (0, -170), (52, -245)], skin_d)
        poly(c, [(-18, -215), (0, -175), (18, -215)], hexc("#C2432F"))
        rect(c, -102, -50, 204, 20, hexc("#3F6B3A"))
    elif outfit == "kurta":
        poly(c, [(-34, -245), (0, -180), (34, -245)], skin_d); line(c, 0, -190, 0, 20, 4, shade(shirtc, .8))
        for i in range(4): circ(c, 0, -165 + i * 45, 6, hexc("#fff8e8"))
    else:
        poly(c, [(-36, -245), (0, -185), (36, -245)], skin_d)
        poly(c, [(-44, -246), (-6, -196), (-4, -250)], shade(shirtc, 1.25)); poly(c, [(44, -246), (6, -196), (4, -250)], shade(shirtc, 1.25))
        rect(c, 40, -120, 44, 52, shade(shirtc, .88), 6)
    # neck + head
    rect(c, -26, -300, 52, 70, skin_d, 14)
    c.save(); c.translate(0, -345); c.rotate(tilt)
    hx = look * 8
    if hair2 or style == "braid":  # back hair
        ell(c, 0, -4, 82, 88, hair)
    ell(c, -75, 2, 14, 20, skin_d); ell(c, 75, 2, 14, 20, skin_d)
    ell(c, 0, 0, 73, 80, skin)
    if back:
        ell(c, 0, -2, 79, 84, hair)
    else:
        if beard == "stubble":
            c.save(); c.new_path(); c.arc(0, 0, 1, 0, 0); c.restore()
            c.new_path(); c.save(); c.translate(0, 0); c.scale(73, 80); c.arc(0, 0, 1, math.radians(18), math.radians(162)); c.restore()
            c.curve_to(-50, 28, 50, 28, 66, 24); c.close_path(); setc(c, alpha(hair, .30)); c.fill()
        elif beard == "full":
            c.new_path(); c.save(); c.scale(76, 84); c.arc(0, 0, 1, math.radians(12), math.radians(168)); c.restore()
            c.curve_to(-42, 14, 42, 14, 70, 20); c.close_path(); setc(c, hair); c.fill()
        # eyes
        ey = -8 + (-4 if mouth == "shock" else 0)
        for sd in (-1, 1):
            ex = sd * 29 + hx
            ell(c, ex, ey, 15, max(1.5, 17 * (1 - blink)), hexc("#fdfaf3"))
            if blink < .8: circ(c, ex + look * 5, ey + 1, 8.5, hexc("#1d1410")); circ(c, ex + look * 5 + 3, ey - 3, 2.6, (1, 1, 1, .9))
            else: line(c, ex - 14, ey, ex + 14, ey, 4, hair)
            if blush: ell(c, sd * 46, 22, 15, 9, (0.9, 0.35, 0.3, .35 * blush))
        for sd in (-1, 1):
            if brow == "flat": p1, p2 = (-12, -34), (-46, -36)
            elif brow == "worry": p1, p2 = (-10, -48), (-46, -30)
            elif brow == "angry": p1, p2 = (-8, -30), (-46, -48)
            elif brow == "up": p1, p2 = (-14, -52), (-46, -48)
            else: p1, p2 = (-12, -40), (-46, -36)
            line(c, sd * -p1[0] + hx if False else sd * 12 + hx, p1[1], sd * 46 + hx, p2[1], 8, hair)
        # nose
        arc_stroke(c, hx * 1.2 + 2, 14, 9, math.radians(20), math.radians(160), 4, skin_d)
        if glasses:
            for sd in (-1, 1): circ(c, sd * 30 + hx, ey, 25, None, hexc("#2a2018"), 5)
            line(c, -5 + hx, ey, 5 + hx, ey, 5, hexc("#2a2018"))
        # mouth
        my = 44; mc = hexc("#5a1f1a")
        if talk > 0.02:
            ell(c, hx * .5, my, 13 + 8 * talk, 4 + 18 * talk, mc); ell(c, hx * .5, my - 3 - 6 * talk, 9, 3, hexc("#fffaf0")) if talk > .35 else None
        elif mouth == "smile": arc_stroke(c, hx * .5, my - 14, 26, math.radians(25), math.radians(155), 7, mc)
        elif mouth == "big":
            c.new_path(); c.arc(hx * .5, my - 10, 30, 0, math.pi); c.close_path(); setc(c, mc); c.fill(); ell(c, hx * .5, my - 8, 24, 7, hexc("#fffaf0"))
        elif mouth == "frown": arc_stroke(c, hx * .5, my + 20, 24, math.radians(205), math.radians(335), 7, mc)
        elif mouth in ("o", "shock"): ell(c, hx * .5, my + 2, 15, 20, mc)
        elif mouth == "grit": rect(c, -26 + hx * .5, my - 8, 52, 16, hexc("#fffaf0"), 6, mc, 4)
        else: line(c, -16 + hx * .5, my, 16 + hx * .5, my, 7, mc)
        if beard == "mustache": ell(c, hx * .5, my - 14, 26, 8, hair)
        # hair
        if style in ("short", "braid"):
            c.new_path(); c.save(); c.scale(76, 83); c.arc(0, 0, 1, math.pi, 2 * math.pi); c.restore()
            c.curve_to(72, -42, 30, -66, -4, -52); c.curve_to(-30, -48, -60, -40, -76, -20); c.close_path(); setc(c, hair); c.fill()
            if style == "braid": line(c, -6, -80, -6, -50, 5, shade(hair, 1.4))
        elif style == "topi":
            c.new_path(); c.save(); c.scale(78, 70); c.arc(0, 0, 1, math.pi, 2 * math.pi); c.restore(); c.line_to(78, -44); c.line_to(-78, -44); c.close_path()
            setc(c, hexc("#F3EEDD")); c.fill()
            for i in range(-3, 4): line(c, i * 20, -62 + abs(i) * 4, i * 20, -50, 3, hexc("#d6cdb2"))
            rect(c, -78, -52, 156, 14, hexc("#E4DCC4"), 5)
            c.new_path(); c.arc(0, 0, 80, math.radians(150), math.radians(190)); setc(c, hair); c.set_line_width(12); c.stroke()
        elif style == "bald":
            for sd in (-1, 1): ell(c, sd * 68, -4, 12, 26, hair)
        elif style == "cap":
            c.new_path(); c.save(); c.scale(79, 72); c.arc(0, 0, 1, math.pi, 2 * math.pi); c.restore(); c.line_to(79, -40); c.line_to(-79, -40); c.close_path(); setc(c, hexc("#B6452E")); c.fill()
            rect(c, -40 + (30 if flip else 0), -48, 120, 14, hexc("#8f3322"), 6)
        if sweat > 0:
            sy_ = -20 + sweat * 50; poly(c, [(78, sy_ - 20), (66, sy_ + 4), (90, sy_ + 4)], (0.95, 0.9, 0.8, .95)); circ(c, 78, sy_ + 6, 12, (0.95, 0.9, 0.8, .95))
    c.restore()
    # braid
    if style == "braid" and not back:
        for i in range(5):
            ell(c, 78 + i * 3, -300 + i * 52, 20 - i * 1.5, 30, hair)
        ell(c, 91, -60, 12, 12, hexc("#C2432F"))
    elif style == "braid" and back:
        for i in range(6): ell(c, 0, -280 + i * 44, 24 - i * 2, 28, hair)
    # arms
    for sd, tgt, hold in ((-1, hl, hold_l), (1, hr, hold_r)):
        sx_, sy_ = sd * 96, -208
        ex, ey, hx2, hy2 = _ik(sx_, sy_, tgt[0], tgt[1], 118, 108, sd)
        sl = shirtc if sleeve == "long" else shirtc
        line(c, sx_, sy_, ex, ey, 48, sl); circ(c, ex, ey, 24, sl)
        line(c, ex, ey, hx2, hy2, 38, sl if sleeve == "long" else skin); circ(c, hx2, hy2, 25, skin)
        if hold:
            c.save(); c.translate(hx2, hy2); hold(c); c.restore()
    c.restore()

def head_pos(x, y, s=1.0): return x, y - 345 * s

# ------------------------------------------------------------------ props
def phone(c, x, y, w=150, h=300, rot=0, state="off", g=0.0, scr=None, glowing=False):
    c.save(); c.translate(x, y); c.rotate(rot)
    if glowing: glow(c, 0, 0, w * 1.5, hexc("#FFD58A"), .35)
    rect(c, -w / 2 + 6, -h / 2 + 10, w, h, (0, 0, 0, .18), w * .14)
    rect(c, -w / 2, -h / 2, w, h, hexc("#23201e"), w * .14)
    sx, sy, sw_, sh = -w / 2 + w * .06, -h / 2 + h * .04, w * .88, h * .92
    if state == "off": rect(c, sx, sy, sw_, sh, hexc("#0f0e0d"), w * .1)
    else:
        col = scr or hexc("#FFE9B8"); rect(c, sx, sy, sw_, sh, col, w * .1)
    if state == "on":
        text(c, "10:45", 0, -h * .18, w * .25, hexc("#5a3b17"), "bold"); rect(c, -w * .3, h * .05, w * .6, h * .05, hexc("#d9b36a"), 6); rect(c, -w * .3, h * .15, w * .42, h * .05, hexc("#e6c98f"), 6)
    elif state == "notes":
        for i in range(7):
            rect(c, -w * .36, -h * .38 + i * h * .095, w * (.72 if i % 3 else .5), h * .035, hexc("#8a7a5a") if i % 3 else hexc("#C2432F"), 4)
    elif state == "cracked":
        c.save(); rrect_path(c, sx, sy, sw_, sh, w * .1); c.clip()
        ox, oy = w * .12, -h * .1
        for i in range(11):
            a = i * 2 * math.pi / 11 + .3; L = (w * .9 if i % 2 else w * .55) * (.7 + rnd(i) * .6)
            mx, my = ox + L * .5 * math.cos(a) + 8 * rnd(i, 2), oy + L * .5 * math.sin(a)
            c.new_path(); c.move_to(ox, oy); c.line_to(mx, my); c.line_to(ox + L * math.cos(a), oy + L * math.sin(a)); c.set_line_width(2.6); setc(c, (.12, .1, .1, .85)); c.stroke()
        for r_ in (w * .12, w * .26):
            c.new_path(); 
            for i in range(11):
                a = i * 2 * math.pi / 11 + .3; px_, py_ = ox + r_ * math.cos(a), oy + r_ * math.sin(a)
                c.line_to(px_, py_) if i else c.move_to(px_, py_)
            c.close_path(); c.set_line_width(2); setc(c, (.12, .1, .1, .7)); c.stroke()
        c.restore()
    if state == "open":
        rect(c, sx, sy, sw_, sh, hexc("#4b4540"), w * .1)
        rect(c, -w * .3, -h * .3, w * .6, h * .22, hexc("#2d6a4f") if False else hexc("#6d8a4f"), 6); rect(c, -w * .3, 0, w * .25, h * .2, hexc("#b8a27a"), 5); circ(c, w * .15, h * .12, w * .12, hexc("#7a6a52"))
    rect(c, -w * .14, -h / 2 + h * .018, w * .28, h * .02, hexc("#0c0b0a"), 5)
    c.restore()

def wall_clock(c, x, y, r, tmin=0.0, g=0.0, old=False, tick=True, hand_speed=0, hands=True):
    face = hexc("#E9DDBF") if old else hexc("#FBF6E8"); rim = hexc("#4A2F1B")
    circ(c, x + 6, y + 8, r + 12, (0, 0, 0, .2)); circ(c, x, y, r + 14, rim); circ(c, x, y, r, face)
    if old:
        glow(c, x, y, r, hexc("#b79a5a"), .35)
        for i in range(5): line(c, x + r * .5, y - r * .95 + i * 3, x + r * .95, y - r * .5 + i * 3 * 0, 1.6, (1, 1, 1, .5))
    for i in range(60):
        a = i * math.pi / 30 - math.pi / 2; big = i % 5 == 0
        line(c, x + (r * .86 if big else r * .92) * math.cos(a), y + (r * .86 if big else r * .92) * math.sin(a), x + r * .97 * math.cos(a), y + r * .97 * math.sin(a), 5 if big else 2, hexc("#3a2a1c"))
    for n, hr_ in ((12, 0), (3, 3), (6, 6), (9, 9)):
        a = hr_ * math.pi / 6 - math.pi / 2
        text(c, bn(n), x + r * .68 * math.cos(a), y + r * .68 * math.sin(a), r * .2, hexc("#3a2a1c"), "bold")
    if hands:
        am = tmin / 60 * 2 * math.pi - math.pi / 2; ah = tmin / 720 * 2 * math.pi - math.pi / 2
        line(c, x, y, x + r * .5 * math.cos(ah), y + r * .5 * math.sin(ah), r * .075, hexc("#2b1d12"))
        line(c, x, y, x + r * .76 * math.cos(am), y + r * .76 * math.sin(am), r * .055, hexc("#2b1d12"))
        if tick:
            sec = g * hand_speed if hand_speed else math.floor(g) + e_elastic(g % 1) * .9
            asec = sec * 2 * math.pi / 60 - math.pi / 2
            line(c, x - r * .15 * math.cos(asec), y - r * .15 * math.sin(asec), x + r * .85 * math.cos(asec), y + r * .85 * math.sin(asec), 3.5, hexc("#C2432F"))
    circ(c, x, y, r * .07, hexc("#C2432F"))

def stopwatch(c, x, y, r, val, g=0.0, col="#C2432F"):
    rect(c, x - r * .12, y - r * 1.25, r * .24, r * .25, hexc("#444"), 5); circ(c, x, y, r + 10, hexc("#3a3a3a")); circ(c, x, y, r, hexc("#FBF6E8"))
    for i in range(12):
        a = i * math.pi / 6 - math.pi / 2; line(c, x + r * .82 * math.cos(a), y + r * .82 * math.sin(a), x + r * .95 * math.cos(a), y + r * .95 * math.sin(a), 4, hexc("#3a2a1c"))
    a = val / 60 * 2 * math.pi - math.pi / 2; line(c, x, y, x + r * .8 * math.cos(a), y + r * .8 * math.sin(a), 6, hexc(col)); circ(c, x, y, r * .08, hexc(col))

def bubble(c, g, t0, x, y, s, tail=None, size=54, bg="#FFF9EC", fg="#2b2118", t1=None, kind="bold", border="#2b2118"):
    p = e_back(prog(g, t0, t0 + .28))
    if p <= 0.01 or (t1 is not None and g > t1): return
    tw, th = text_size(s.split("\n")[0] if "\n" not in s else max(s.split("\n"), key=len), size, kind); n = s.count("\n") + 1
    w = tw + 80; h = n * size * 1.32 + 56
    c.save(); ox, oy = tail if tail else (x, y); c.translate(ox, oy); c.scale(p, p); c.translate(-ox, -oy)
    if tail:
        bx = clamp(tail[0], x - w / 2 + 50, x + w / 2 - 50); by = y + h / 2 - 4 if tail[1] > y else y - h / 2 + 4
        poly(c, [(bx - 26, by), (bx + 26, by), tail], hexc(bg), hexc(border), 5)
    rect(c, x - w / 2, y - h / 2, w, h, hexc(bg), 36, hexc(border), 5)
    if tail: poly(c, [(bx - 22, by + (-3 if tail[1] > y else 3)), (bx + 22, by + (-3 if tail[1] > y else 3)), (bx, by + (6 if tail[1] > y else -6))], hexc(bg)) if False else None
    text(c, s, x, y, size, hexc(fg), kind); c.restore()

def talkamt(g, a, b, f=13.0):
    if g < a or g > b: return 0.0
    return .25 + .75 * abs(math.sin(g * f)) * (0.6 + .4 * math.sin(g * 5.3) ** 2)

def blinkamt(g, off=0.0):
    ph = (g + off) % 3.4
    return clamp(1 - abs(ph - 3.25) / .09) if 3.16 < ph < 3.34 else 0.0

def coin(c, x, y, r, rot=0):
    c.save(); c.translate(x, y); c.scale(abs(math.cos(rot)) * .8 + .2, 1)
    circ(c, 0, 0, r, hexc("#E0A526"), hexc("#A6720F"), r * .12); circ(c, 0, 0, r * .66, None, hexc("#F6CF62"), r * .09); text(c, "৳", 0, 0, r * 1.0, hexc("#A6720F"), "bold"); c.restore()
