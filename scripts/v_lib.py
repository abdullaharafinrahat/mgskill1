# Core drawing library: skia helpers, Bengali text shaping (harfbuzz), easing, camera, bubbles
import math, functools
import skia, uharfbuzz as hb

W, H = 1080, 1920
FONTS = {
    "b": "fonts/HindSiliguri-Bold.ttf",
    "m": "fonts/HindSiliguri-Medium.ttf",
    "r": "fonts/HindSiliguri-Regular.ttf",
}


def col(h, a=1.0):
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return skia.Color(r, g, b, int(max(0, min(1, a)) * 255))


def fill(h, a=1.0):
    return skia.Paint(Color=col(h, a), AntiAlias=True)


def stroke(h, w, a=1.0, cap="round"):
    p = skia.Paint(Color=col(h, a), AntiAlias=True)
    p.setStyle(skia.Paint.kStroke_Style)
    p.setStrokeWidth(w)
    p.setStrokeCap(skia.Paint.kRound_Cap if cap == "round" else skia.Paint.kButt_Cap)
    p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def lerp(a, b, t):
    return a + (b - a) * t


def prog(t, a, b):
    """0..1 progress of t between a and b"""
    return clamp((t - a) / (b - a)) if b != a else (1.0 if t >= a else 0.0)


def ease(t):  # smoothstep-ish ease in-out
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def back_out(t, s=1.7):
    t = clamp(t) - 1
    return t * t * ((s + 1) * t + s) + 1


def pop(t, a, d=0.35):
    """overshoot pop-in scale from time a"""
    return back_out(prog(t, a, a + d))


# ---------------------------------------------------------------- text
class _F:
    cache = {}


def _font(key):
    if key not in _F.cache:
        fp = FONTS[key]
        blob = hb.Blob.from_file_path(fp)
        face = hb.Face(blob)
        hf = hb.Font(face)
        tf = skia.Typeface.MakeFromFile(fp)
        sf = skia.Font(tf, 100)
        _F.cache[key] = (hf, face.upem, sf)
    return _F.cache[key]


@functools.lru_cache(maxsize=4096)
def text_path(s, key="b"):
    """returns (path at size 100 with baseline y=0, advance width)"""
    hf, upem, sf = _font(key)
    buf = hb.Buffer()
    buf.add_str(s)
    buf.guess_segment_properties()
    hb.shape(hf, buf, {"kern": True, "liga": True})
    sc = 100.0 / upem
    path = skia.Path()
    x = 0.0
    for gi, gp in zip(buf.glyph_infos, buf.glyph_positions):
        gpath = sf.getPath(gi.codepoint)
        if gpath is not None:
            gpath.offset(x + gp.x_offset * sc, -gp.y_offset * sc)
            path.addPath(gpath)
        x += gp.x_advance * sc
    return path, x


def text_w(s, size, key="b"):
    return text_path(s, key)[1] * size / 100.0


def draw_text(c, s, x, y, size, color="#000000", key="b", align="c", a=1.0, outline=None, ow=0, paint=None):
    path, w = text_path(s, key)
    k = size / 100.0
    if align == "c":
        x0 = x - w * k / 2
    elif align == "r":
        x0 = x - w * k
    else:
        x0 = x
    c.save()
    c.translate(x0, y)
    c.scale(k, k)
    if outline:
        c.drawPath(path, stroke(outline, ow / k * 1.0, a))
    c.drawPath(path, paint or fill(color, a))
    c.restore()


def wrap_words(words, size, maxw, key="b"):
    lines, cur = [], []
    for w in words:
        t = " ".join(cur + [w])
        if cur and text_w(t, size, key) > maxw:
            lines.append(cur)
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- shapes
def rrect(c, x, y, w, h, r, paint):
    c.drawRoundRect(skia.Rect.MakeXYWH(x, y, w, h), r, r, paint)


def rect(c, x, y, w, h, paint):
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), paint)


def circle(c, x, y, r, paint):
    c.drawCircle(x, y, r, paint)


def oval(c, x, y, rx, ry, paint):
    c.drawOval(skia.Rect.MakeXYWH(x - rx, y - ry, rx * 2, ry * 2), paint)


def line(c, x0, y0, x1, y1, h, w, a=1.0):
    c.drawLine(x0, y0, x1, y1, stroke(h, w, a))


def poly(c, pts, paint):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.close()
    c.drawPath(p, paint)


def lin_grad(x0, y0, x1, y1, cols):
    n = len(cols)
    return skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
        [(x0, y0), (x1, y1)], [col(h, a) for h, a in cols], [i / (n - 1) for i in range(n)]))


def rad_grad(x, y, r, cols):
    n = len(cols)
    return skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        (x, y), r, [col(h, a) for h, a in cols], [i / (n - 1) for i in range(n)]))


def shadow_ellipse(c, x, y, rx, ry, a=0.25):
    oval(c, x, y, rx, ry, fill("#000000", a))


# ---------------------------------------------------------------- camera
def camera(c, t, keys):
    """keys: list of (time, cx, cy, zoom). smooth interpolation between keys; world centre -> screen centre"""
    if t <= keys[0][0]:
        k = keys[0]
        cx, cy, z = k[1], k[2], k[3]
    elif t >= keys[-1][0]:
        k = keys[-1]
        cx, cy, z = k[1], k[2], k[3]
    else:
        for i in range(len(keys) - 1):
            a, b = keys[i], keys[i + 1]
            if a[0] <= t <= b[0]:
                u = ease(prog(t, a[0], b[0]))
                cx, cy, z = lerp(a[1], b[1], u), lerp(a[2], b[2], u), lerp(a[3], b[3], u)
                break
    # handheld micro-motion for life
    cx += math.sin(t * 1.3) * 3
    cy += math.cos(t * 1.7) * 3
    c.translate(W / 2, H / 2)
    c.scale(z, z)
    c.translate(-cx, -cy)


# ---------------------------------------------------------------- speech bubbles
def bubble(c, x, y, text, t0, t, size=64, tail=(0, 1), maxw=620, bg="#FFF8E7", fg="#2B1D14", key="b", words=None, border="#2B1D14", tail_off=0):
    """speech bubble centred at x,y (tail points down if tail[1]>0, up if <0, sideways via tail[0])"""
    s = pop(t, t0)
    if t < t0:
        return
    lines = wrap_words(text.split(" "), size, maxw, key)
    lh = size * 1.28
    bw = max(text_w(" ".join(l), size, key) for l in lines) + 90
    bh = len(lines) * lh + 50
    c.save()
    c.translate(x, y)
    c.scale(s, s)
    # tail
    tx = tail[0] * bw * 0.28 + tail_off
    if tail[1] > 0:
        pts = [(tx - 34, bh / 2 - 6), (tx + 34, bh / 2 - 6), (tx + tail[0] * 40 + 10, bh / 2 + 70)]
    elif tail[1] < 0:
        pts = [(tx - 34, -bh / 2 + 6), (tx + 34, -bh / 2 + 6), (tx + tail[0] * 40 + 10, -bh / 2 - 70)]
    else:
        sx = tail[0] * (bw / 2 - 6)
        pts = [(sx, -22), (sx, 26), (sx + tail[0] * 70, 56)]
    rrect(c, -bw / 2 + 8, -bh / 2 + 10, bw, bh, 44, fill("#000000", 0.18))
    rrect(c, -bw / 2, -bh / 2, bw, bh, 44, fill(bg))
    rrect(c, -bw / 2, -bh / 2, bw, bh, 44, stroke(border, 6))
    poly(c, pts, fill(bg))
    pp = skia.Path()
    pp.moveTo(*pts[0]); pp.lineTo(*pts[2]); pp.lineTo(*pts[1])
    c.drawPath(pp, stroke(border, 6))
    # cover the border where the tail joins
    if tail[1] != 0:
        yy = (bh / 2 - 3) if tail[1] > 0 else (-bh / 2 + 3)
        line(c, pts[0][0] + 5, yy, pts[1][0] - 5, yy, bg, 10)
    # text
    y0 = -bh / 2 + 25 + size * 0.98
    for i, l in enumerate(lines):
        draw_text(c, " ".join(l), 0, y0 + i * lh, size, fg, key)
    c.restore()


def sparkle(c, x, y, r, color="#FFE08A", rot=0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    p = skia.Path()
    p.moveTo(0, -r)
    p.quadTo(0, 0, r, 0)
    p.quadTo(0, 0, 0, r)
    p.quadTo(0, 0, -r, 0)
    p.quadTo(0, 0, 0, -r)
    c.drawPath(p, fill(color))
    c.restore()


def question_mark(c, x, y, size, color="#C0392B", rot=0, a=1.0):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    draw_text(c, "?", 0, 0, size, color, "b", "c", a)
    c.restore()
