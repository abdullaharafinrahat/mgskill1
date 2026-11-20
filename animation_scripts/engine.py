# -*- coding: utf-8 -*-
"""Tiny 2D animation engine on top of pycairo + Pillow(raqm) for Bengali text."""
import math, os, functools, random
import cairo
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
FD = "/usr/share/fonts/truetype/noto/"
FONTS = {
    ("bn", "sans", True): FD + "NotoSansBengali-Bold.ttf",
    ("bn", "sans", False): FD + "NotoSansBengali-Regular.ttf",
    ("bn", "serif", True): FD + "NotoSerifBengali-Bold.ttf",
    ("bn", "serif", False): FD + "NotoSerifBengali-Regular.ttf",
    ("la", "sans", True): FD + "NotoSans-Bold.ttf",
    ("la", "sans", False): FD + "NotoSans-Regular.ttf",
    ("la", "serif", True): FD + "NotoSerif-Bold.ttf",
    ("la", "serif", False): FD + "NotoSerif-Regular.ttf",
}
SS = 2  # text supersampling


# ------------------------------------------------------------------ maths
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def eo3(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ei3(t):
    t = clamp(t)
    return t ** 3


def eio(t):
    t = clamp(t)
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def back(t, s=1.70158):
    t = clamp(t)
    return max(1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2, 0.004)


def prog(t, t0, d):
    return clamp((t - t0) / d)


def pop(t, t0, d=0.4):
    """0 before t0, overshoot scale in, settles at 1"""
    if t < t0:
        return 1e-4
    return max(back(prog(t, t0, d)), 1e-4)


def kf(t, keys):
    """keyframes [(time, v1, v2, ...)] smooth interpolation -> tuple"""
    if t <= keys[0][0]:
        return keys[0][1:]
    for a, b in zip(keys[:-1], keys[1:]):
        if t <= b[0]:
            p = smooth((t - a[0]) / max(b[0] - a[0], 1e-6))
            return tuple(lerp(x, y, p) for x, y in zip(a[1:], b[1:]))
    return keys[-1][1:]


def mix(c1, c2, p):
    a, b = rgb(c1), rgb(c2)
    return tuple(lerp(x, y, p) for x, y in zip(a, b))


# ------------------------------------------------------------------ colours / primitives
@functools.lru_cache(maxsize=None)
def _hex(c):
    c = c.lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    return tuple(int(c[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def rgb(c):
    return _hex(c) if isinstance(c, str) else c


def setc(ctx, c, a=1.0):
    r, g, b = rgb(c)
    ctx.set_source_rgba(r, g, b, a)


def rr_path(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def _paint(ctx, c, a, sc, lw):
    if c is not None:
        setc(ctx, c, a)
        if sc is not None and lw:
            ctx.fill_preserve()
        else:
            ctx.fill()
    if sc is not None and lw:
        setc(ctx, sc, a)
        ctx.set_line_width(lw)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke()


def rect(ctx, x, y, w, h, c, r=0, a=1.0, sc=None, lw=0):
    if r:
        rr_path(ctx, x, y, w, h, r)
    else:
        ctx.rectangle(x, y, w, h)
    _paint(ctx, c, a, sc, lw)


def circ(ctx, x, y, r, c, a=1.0, sc=None, lw=0):
    ctx.new_sub_path()
    ctx.arc(x, y, max(r, 0.01), 0, math.tau)
    _paint(ctx, c, a, sc, lw)


def ell(ctx, x, y, rx, ry, c, a=1.0, rot=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(max(rx, 0.01), max(ry, 0.01))
    ctx.new_sub_path()
    ctx.arc(0, 0, 1, 0, math.tau)
    ctx.restore()
    setc(ctx, c, a)
    ctx.fill()


def poly(ctx, pts, c, a=1.0, sc=None, lw=0, close=True):
    ctx.new_path()
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    if close:
        ctx.close_path()
    _paint(ctx, c, a, sc, lw)


def line(ctx, x1, y1, x2, y2, c, lw=6, a=1.0, cap=cairo.LINE_CAP_ROUND):
    ctx.new_path()
    ctx.move_to(x1, y1)
    ctx.line_to(x2, y2)
    setc(ctx, c, a)
    ctx.set_line_width(lw)
    ctx.set_line_cap(cap)
    ctx.stroke()


def pline(ctx, pts, c, lw=6, a=1.0):
    ctx.new_path()
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    setc(ctx, c, a)
    ctx.set_line_width(lw)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke()


def arc_stroke(ctx, x, y, r, a0, a1, c, lw=6, a=1.0):
    ctx.new_path()
    ctx.arc(x, y, r, a0, a1)
    setc(ctx, c, a)
    ctx.set_line_width(lw)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()


def vgrad(ctx, c0, c1, y0=0, y1=H, x=0, w=W, h=None):
    g = cairo.LinearGradient(0, y0, 0, y1)
    g.add_color_stop_rgb(0, *rgb(c0))
    g.add_color_stop_rgb(1, *rgb(c1))
    ctx.rectangle(x, y0, w, (y1 - y0) if h is None else h)
    ctx.set_source(g)
    ctx.fill()


def rgrad(ctx, x, y, r, c, a0=0.9, a1=0.0, r0=0):
    g = cairo.RadialGradient(x, y, r0, x, y, r)
    cc = rgb(c)
    g.add_color_stop_rgba(0, *cc, a0)
    g.add_color_stop_rgba(1, *cc, a1)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, math.tau)
    ctx.fill()


def bg(ctx, c, x=-3000, y=-3000, w=7000, h=7000):
    rect(ctx, x, y, w, h, c)


def camera(ctx, cx, cy, zoom=1.0, rot=0.0):
    ctx.translate(W / 2, H / 2)
    ctx.rotate(rot)
    ctx.scale(zoom, zoom)
    ctx.translate(-cx, -cy)


def shake(t, amp=6, f=17):
    return (math.sin(t * f) * amp, math.cos(t * f * 1.3) * amp)


# ------------------------------------------------------------------ text
@functools.lru_cache(maxsize=None)
def _font(kind, fam, bold, px):
    return ImageFont.truetype(FONTS[(kind, fam, bold)], px, layout_engine=ImageFont.Layout.RAQM)


def _runs(text):
    out, cur, kind = [], "", None
    for ch in text:
        if ch.isascii() and ch.isalpha():
            k = "la"
        elif ch.isascii():
            k = kind or "bn"
        else:
            k = "bn"
        if kind is None:
            kind = k
        if k != kind:
            out.append((kind, cur))
            cur, kind = "", k
        cur += ch
    if cur:
        out.append((kind, cur))
    return out


_tcache = {}


def text_sprite(text, size, color="#ffffff", fam="sans", bold=True, maxw=None, stroke=0, stroke_color="#000000",
                lh=1.42, align="center"):
    key = (text, size, color if isinstance(color, str) else tuple(color), fam, bold, maxw, stroke,
           stroke_color if isinstance(stroke_color, str) else tuple(stroke_color), lh, align)
    if key in _tcache:
        return _tcache[key]
    px = int(size * SS)

    def meas(s):
        return sum(_font(k, fam, bold, px).getlength(r) for k, r in _runs(s))

    lines = []
    if maxw:
        for para in text.split("\n"):
            cur = ""
            for w in para.split(" "):
                trial = (cur + " " + w) if cur else w
                if meas(trial) <= maxw * SS or not cur:
                    cur = trial
                else:
                    lines.append(cur)
                    cur = w
            lines.append(cur)
    else:
        lines = text.split("\n")
    widths = [meas(l) for l in lines]
    pad = int(size * 0.3 * SS) + stroke * SS * 2
    lhpx = int(px * lh)
    cw = int(max(widths)) + pad * 2
    ch_ = lhpx * len(lines) + pad * 2
    img = Image.new("RGBA", (cw, ch_), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    asc = _font("bn", fam, bold, px).getmetrics()[0]
    fill = tuple(int(v * 255) for v in rgb(color)) + (255,)
    sfill = tuple(int(v * 255) for v in rgb(stroke_color)) + (255,)
    for li, l in enumerate(lines):
        x = pad + ((cw - 2 * pad - widths[li]) / 2 if align == "center" else 0 if align == "left" else (cw - 2 * pad - widths[li]))
        base = pad + li * lhpx + (lhpx - px) / 2 + asc
        for k, r in _runs(l):
            f = _font(k, fam, bold, px)
            d.text((x, base), r, font=f, fill=fill, anchor="ls", stroke_width=stroke * SS, stroke_fill=sfill)
            x += f.getlength(r)
    arr = np.array(img).astype(np.float32)
    a = arr[..., 3:4] / 255.0
    pm = np.concatenate([arr[..., 2:3] * a, arr[..., 1:2] * a, arr[..., 0:1] * a, arr[..., 3:4]], axis=2)
    data = np.ascontiguousarray(pm.astype(np.uint8))
    surf = cairo.ImageSurface.create_for_data(data, cairo.FORMAT_ARGB32, cw, ch_, cw * 4)
    res = (surf, data, cw / SS, ch_ / SS, widths, len(lines))
    _tcache[key] = res
    return res


def text(ctx, s, x, y, size=60, color="#ffffff", a=1.0, sc=1.0, rot=0.0, anchor="c", **kw):
    if a <= 0.001 or sc <= 0.001:
        return (0, 0)
    m = ctx.get_matrix()
    if abs(m.xx * m.yy - m.xy * m.yx) * sc * sc < 1e-4:
        return (0, 0)
    surf, _, w, h, _, _ = text_sprite(s, size, color, **kw)
    ctx.save()
    ctx.translate(x, y)
    if rot:
        ctx.rotate(rot)
    ctx.scale(sc / SS, sc / SS)
    ox = -w * SS / 2 if anchor == "c" else 0 if anchor == "l" else -w * SS
    ctx.set_source_surface(surf, ox, -h * SS / 2)
    ctx.get_source().set_filter(cairo.FILTER_BEST)
    ctx.paint_with_alpha(a)
    ctx.restore()
    return (w, h)


def text_w(s, size, **kw):
    r = text_sprite(s, size, "#fff", **kw)
    return r[2], r[3]


def typewriter(s, p):
    n = int(len(s) * clamp(p))
    return s[:n]


# ------------------------------------------------------------------ decor helpers
def sunburst(ctx, cx, cy, c1, c2, t=0, n=18, R=2600, speed=0.15):
    bg(ctx, c1)
    for i in range(n):
        a0 = (i / n) * math.tau + t * speed
        a1 = a0 + math.tau / n / 2
        ctx.new_path()
        ctx.move_to(cx, cy)
        ctx.line_to(cx + R * math.cos(a0), cy + R * math.sin(a0))
        ctx.line_to(cx + R * math.cos(a1), cy + R * math.sin(a1))
        ctx.close_path()
        setc(ctx, c2)
        ctx.fill()


def sparkle(ctx, x, y, r, c="#FFF3C4", a=1.0, rot=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r * 0.25
        ang = i * math.pi / 4 - math.pi / 2
        pts.append((rr * math.cos(ang), rr * math.sin(ang)))
    poly(ctx, pts, c, a)
    ctx.restore()


def confetti(ctx, t, cols, n=60, seed=1, x0=0, x1=W, y0=0, y1=H, speed=140, size=16):
    rnd = random.Random(seed)
    for i in range(n):
        bx = rnd.uniform(x0, x1)
        by = rnd.uniform(0, y1 - y0)
        sp = rnd.uniform(0.6, 1.4) * speed
        ph = rnd.uniform(0, 6.28)
        y = y0 + (by + t * sp) % (y1 - y0)
        x = bx + math.sin(t * 1.5 + ph) * 25
        c = cols[i % len(cols)]
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(t * rnd.uniform(-3, 3) + ph)
        rect(ctx, -size / 2, -size / 4, size, size / 2, c)
        ctx.restore()


def rain(ctx, t, c="#CFC3B4", n=90, seed=3, a=0.55, x0=-200, x1=W + 200):
    rnd = random.Random(seed)
    for i in range(n):
        x = rnd.uniform(x0, x1)
        sp = rnd.uniform(1400, 2000)
        y = (rnd.uniform(0, H) + t * sp) % (H + 200) - 100
        line(ctx, x, y, x - 14, y + 55, c, 3, a)


def noise_dots(ctx, seed, n, c, a, x0, x1, y0, y1, rmin=2, rmax=6):
    rnd = random.Random(seed)
    for _ in range(n):
        circ(ctx, rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(rmin, rmax), c, a)


def cloud(ctx, x, y, s, c="#ffffff", a=1.0):
    for dx, dy, r in ((-60, 8, 40), (-20, -14, 52), (30, -6, 46), (70, 12, 34), (0, 22, 44)):
        circ(ctx, x + dx * s, y + dy * s, r * s, c, a)
    rect(ctx, x - 80 * s, y + 10 * s, 170 * s, 36 * s, c, 18 * s, a)


class ShotCtx:
    """Per-shot helper handed to every shot function."""

    def __init__(self, tl, ci0, ci1, gstart, gend, env):
        self.tl = tl
        self.ci0, self.ci1 = ci0, ci1
        self.g0, self.g1 = gstart, gend
        self.dur = gend - gstart
        self.env = env
        self.t = 0.0
        self.gt = gstart

    def at(self, t):
        self.t = t
        self.gt = self.g0 + t
        return self

    def c(self, i):
        """local time when chunk i begins being spoken"""
        return self.tl["chunks"][i]["s0"] - self.g0

    def ce(self, i):
        return self.tl["chunks"][i]["s1"] - self.g0

    def active(self):
        """index of chunk being spoken right now (or None)"""
        for ch in self.tl["chunks"]:
            if ch["s0"] - 0.05 <= self.gt <= ch["s1"] + 0.05:
                return ch["i"]
        return None

    def speaking(self, who):
        a = self.active()
        if a is None:
            return 0.0
        if self.tl["chunks"][a]["speaker"] != who:
            return 0.0
        k = int(self.gt * 60)
        k = min(k, len(self.env) - 3)
        v = float(np.mean(self.env[max(k - 1, 0):k + 2]))
        return clamp(v * 1.15)

    def talk(self, who):  # returns mouth openness
        return self.speaking(who)
