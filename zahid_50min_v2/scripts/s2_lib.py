"""Script 2: drawing library (Skia raster) - text shaping (HarfBuzz), shapes, characters, props."""
import math, functools, contextlib
import skia
import uharfbuzz as hb

W, H = 1080, 1920
FD = "/tmp/vid/fonts/"
FB, FR = "NotoSansBengali.ttf", "NotoSansBengali-Regular.ttf"

# ---------------------------------------------------------------- math / easing
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def lerp(a, b, t):
    return a + (b - a) * t

def ease_out(t):
    t = clamp(t); return 1 - (1 - t) ** 3

def ease_in(t):
    t = clamp(t); return t ** 3

def ease_io(t):
    t = clamp(t); return 3 * t * t - 2 * t * t * t

def back_out(t, k=1.9):
    t = clamp(t); t -= 1
    return 1 + t * t * ((k + 1) * t + k)

def prog(t, t0, dur=0.5):
    return clamp((t - t0) / dur)

def pop(t, t0, dur=0.45):
    return back_out(prog(t, t0, dur))

# ---------------------------------------------------------------- colours
def rgb(h):
    h = h.lstrip("#"); return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

def col(h, a=255):
    r, g, b = rgb(h); return skia.ColorSetARGB(int(clamp(a, 0, 255)), r, g, b)

def mix(h1, h2, t):
    a, b = rgb(h1), rgb(h2); t = clamp(t)
    return "#%02x%02x%02x" % tuple(int(lerp(a[i], b[i], t)) for i in range(3))

def paint(color, a=255, stroke=0, blur=0, round_cap=True):
    p = skia.Paint(AntiAlias=True)
    p.setColor(col(color, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        if round_cap:
            p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p

# ---------------------------------------------------------------- shapes
def rect(c, x, y, w, h, color, r=0, a=255, stroke=0, blur=0):
    p = paint(color, a, stroke, blur)
    if r:
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(x, y, w, h), r, r), p)
    else:
        c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), p)

def circ(c, x, y, r, color, a=255, stroke=0, blur=0):
    c.drawCircle(x, y, r, paint(color, a, stroke, blur))

def oval(c, x, y, rx, ry, color, a=255, stroke=0, blur=0):
    c.drawOval(skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y + ry), paint(color, a, stroke, blur))

def line(c, x1, y1, x2, y2, color, w=6, a=255):
    c.drawLine(x1, y1, x2, y2, paint(color, a, w))

def poly(c, pts, color, a=255, stroke=0, close=True, blur=0):
    path = skia.Path(); path.moveTo(*pts[0])
    for q in pts[1:]:
        path.lineTo(*q)
    if close: path.close()
    c.drawPath(path, paint(color, a, stroke, blur))

def curve(c, pts, color, w=6, a=255):
    path = skia.Path(); path.moveTo(*pts[0])
    for i in range(1, len(pts) - 1):
        mx, my = (pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2
        path.quadTo(pts[i][0], pts[i][1], mx, my)
    path.lineTo(*pts[-1])
    c.drawPath(path, paint(color, a, w))

def arc(c, cx, cy, r, a0, a1, color, w=6, a=255):
    c.drawArc(skia.Rect.MakeLTRB(cx - r, cy - r, cx + r, cy + r), a0, a1 - a0, False, paint(color, a, w))

def wedge(c, cx, cy, r, a0, a1, color, a=255):
    c.drawArc(skia.Rect.MakeLTRB(cx - r, cy - r, cx + r, cy + r), a0, a1 - a0, True, paint(color, a))

def grad(c, x, y, w, h, c1, c2, vertical=True, a=255):
    p = skia.Paint(AntiAlias=True)
    pts = [(x, y), (x, y + h)] if vertical else [(x, y), (x + w, y)]
    p.setShader(skia.GradientShader.MakeLinear(pts, [col(c1, a), col(c2, a)]))
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), p)

def radial(c, cx, cy, r, c1, c2, a1=255, a2=0):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial((cx, cy), r, [col(c1, a1), col(c2, a2)]))
    c.drawCircle(cx, cy, r, p)

def shadow(c, x, y, rx, ry, a=70):
    oval(c, x, y, rx, ry, "#000000", a, blur=10)

@contextlib.contextmanager
def alpha_layer(c, a):
    c.saveLayerAlpha(None, int(clamp(a, 0, 1) * 255))
    try:
        yield
    finally:
        c.restore()

@contextlib.contextmanager
def xform(c, x=0, y=0, s=1.0, rot=0.0, sx=None, sy=None):
    c.save(); c.translate(x, y)
    if rot: c.rotate(rot)
    c.scale(s if sx is None else sx, s if sy is None else sy)
    try:
        yield
    finally:
        c.restore()

def sparkle(c, x, y, r, color="#FFF3B0", a=255, rot=45):
    path = skia.Path(); k = 0.22
    path.moveTo(0, -r); path.quadTo(k * r, -k * r, r, 0); path.quadTo(k * r, k * r, 0, r)
    path.quadTo(-k * r, k * r, -r, 0); path.quadTo(-k * r, -k * r, 0, -r)
    c.save(); c.translate(x, y); c.rotate(rot - 45); c.drawPath(path, paint(color, a)); c.restore()

def rays(c, cx, cy, t, color, a=40, n=16, length=2600, speed=6):
    for i in range(n):
        a0 = i * 360 / n + t * speed
        path = skia.Path(); path.moveTo(cx, cy)
        for ang in (a0, a0 + 180 / n):
            path.lineTo(cx + length * math.cos(math.radians(ang)), cy + length * math.sin(math.radians(ang)))
        path.close(); c.drawPath(path, paint(color, a))

def dots(c, x0, y0, x1, y1, step, r, color, a=60, ox=0, oy=0):
    x = x0 + (ox % step) - step
    while x < x1:
        y = y0 + (oy % step) - step
        while y < y1:
            circ(c, x, y, r, color, a); y += step
        x += step

# ---------------------------------------------------------------- text (HarfBuzz shaping + Skia paths)
_faces = {}

def _load(name):
    if name not in _faces:
        blob = hb.Blob.from_file_path(FD + name); face = hb.Face(blob)
        _faces[name] = (hb.Font(face), skia.Typeface.MakeFromFile(FD + name), face.upem)
    return _faces[name]

def _runs(txt):
    runs, cur, kind = [], "", None
    for ch in txt:
        o = ord(ch)
        k = "bn" if (0x0980 <= o <= 0x09FF or o in (0x200C, 0x200D)) else ("lat" if ch.isalpha() else None)
        if k is None: k = kind or "bn"
        if kind is not None and k != kind:
            runs.append(cur); cur = ""
        kind = k; cur += ch
    if cur: runs.append(cur)
    return runs

@functools.lru_cache(maxsize=4000)
def text_path(txt, size, bold=True):
    hbf, tf, upem = _load(FB if bold else FR)
    sf = skia.Font(tf, size); sc = size / upem
    path = skia.Path(); x = 0.0
    for run in _runs(txt):
        buf = hb.Buffer(); buf.add_str(run); buf.guess_segment_properties(); hb.shape(hbf, buf, {})
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            gp = sf.getPath(info.codepoint)
            if gp is not None:
                path.addPath(gp, x + pos.x_offset * sc, -pos.y_offset * sc)
            x += pos.x_advance * sc
    return path, x

def text_w(txt, size, bold=True):
    return text_path(txt, size, bold)[1]

def draw_text(c, txt, x, y, size, color="#FFFFFF", a=255, align="c", bold=True, outline=None, scale=1.0,
              rot=0.0, shadow_c=None):
    path, w = text_path(txt, size, bold)
    ox = {"c": -w / 2, "l": 0, "r": -w}[align]
    c.save(); c.translate(x, y)
    if rot: c.rotate(rot)
    c.scale(scale, scale); c.translate(ox, 0)
    if shadow_c:
        c.save(); c.translate(3, 5); c.drawPath(path, paint(shadow_c, min(a, 120))); c.restore()
    if outline:
        c.drawPath(path, paint(outline[0], a, outline[1]))
    c.drawPath(path, paint(color, a))
    c.restore()

def wrap(txt, size, maxw, bold=True):
    words, lines, cur = txt.split(" "), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_w(t, size, bold) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def draw_lines(c, lines, x, y, size, color, lh=1.35, a=255, align="c", bold=True, **kw):
    for i, ln in enumerate(lines):
        draw_text(c, ln, x, y + i * size * lh, size, color, a, align, bold, **kw)

def bubble(c, cx, cy, text, p=1.0, size=48, maxw=520, fill="#FFFFFF", ink="#2B2118", tail=(0, 100), bold=True):
    """speech bubble centred at (cx,cy); tail=(dx,dy) offset of tail tip from centre."""
    if p <= 0.01: return
    lines = wrap(text, size, maxw, bold)
    w = max(text_w(l, size, bold) for l in lines) + 70; h = len(lines) * size * 1.4 + 44
    s = back_out(p)
    c.save(); c.translate(cx + tail[0], cy + tail[1]); c.scale(s, s); c.translate(-tail[0], -tail[1])
    with alpha_layer(c, clamp(p * 2)):
        rect(c, -w / 2 + 6, -h / 2 + 10, w, h, "#000000", r=36, a=45, blur=6)
        tx, ty = tail
        bx = clamp(tx, -w / 2 + 50, w / 2 - 50)
        if ty > 0:
            poly(c, [(bx - 28, h / 2 - 8), (bx + 28, h / 2 - 8), (tx, ty)], fill)
        else:
            poly(c, [(bx - 28, -h / 2 + 8), (bx + 28, -h / 2 + 8), (tx, ty)], fill)
        rect(c, -w / 2, -h / 2, w, h, fill, r=36)
        draw_lines(c, lines, 0, -h / 2 + 22 + size * 0.95, size, ink, bold=bold)
    c.restore()

def tag(c, cx, cy, text, size=44, fill="#2B2118", ink="#FFFFFF", p=1.0, rot=0, padx=40):
    if p <= 0.01: return
    w = text_w(text, size) + padx * 2; h = size * 1.7
    with xform(c, cx, cy, back_out(p), rot):
        with alpha_layer(c, clamp(p * 2)):
            rect(c, -w / 2 + 4, -h / 2 + 8, w, h, "#000000", r=h / 2, a=60, blur=6)
            rect(c, -w / 2, -h / 2, w, h, fill, r=h / 2)
            draw_text(c, text, 0, size * 0.36, size, ink)

# ---------------------------------------------------------------- characters
def _arm(c, sx, sy, ang, bend, sleeve, skin, w=34):
    a1 = math.radians(ang); a2 = math.radians(ang + bend)
    ex, ey = sx + 82 * math.sin(a1), sy + 82 * math.cos(a1)
    hx, hy = ex + 78 * math.sin(a2), ey + 78 * math.cos(a2)
    line(c, sx, sy, ex, ey, sleeve, w + 4)
    line(c, ex, ey, hx, hy, skin, w - 8)
    circ(c, hx, hy, 19, skin)
    return hx, hy

DK = "#1A120D"

def person(c, x, y, s=1.0, skin="#B97A50", shirt="#6B8E4E", pants="#3B3028", hair="#1E1612", style="short",
           mood="neutral", talk=0.0, facing=1, armF=(10, 5), armB=(-8, 5), walk=None, t=0.0, mustache=False,
           apron=None, look=0.0, bag=False, sweat=False, shoes="#2A1F18", blink=True, skirt=None, legs=True):
    """Flat-style character. (x,y) = feet position, facing=+1 right / -1 left. Returns front-hand world pos."""
    c.save(); c.translate(x, y); c.scale(facing * s, s)
    shadow(c, 0, 4, 90, 16, 55)
    sw = math.sin(walk) * 24 if walk is not None else 0
    hip_y = -175
    if legs:
        for side, ang in ((-1, sw), (1, -sw)):
            a = math.radians(ang)
            fx, fy = side * 30 + math.sin(a) * 170, hip_y + math.cos(a) * 170
            line(c, side * 30, hip_y, fx, fy, pants, 46)
            oval(c, fx + 12, fy - 2, 34, 15, shoes)
    if style == "girl":
        rect(c, -76, -462 - 52, 144, 200, hair, r=60)
    if bag:
        rect(c, -112, -335, 66, 150, "#8C3B2E", r=18); rect(c, -106, -328, 54, 44, "#A84B3A", r=14)
    wk = sw * 1.2 if walk is not None else 0
    _arm(c, -62, -360, armB[0] + wk, armB[1], shirt, skin)
    th = 215
    rect(c, -78, -170 - th, 156, th + 12, shirt, r=44)
    if skirt:
        poly(c, [(-80, -200), (80, -200), (108, -110), (-108, -110)], skirt)
    if apron:
        rect(c, -62, -330, 124, 160, apron, r=22)
        rect(c, -28, -300, 56, 36, mix(apron, "#000000", 0.18), r=10)
    rect(c, -16, -400, 32, 40, mix(skin, "#000000", 0.12), r=10)
    fxh, fyh = _arm(c, 62, -360, armF[0] - wk, armF[1], shirt, skin)
    hy = -462
    circ(c, -50, hy + 6, 13, mix(skin, "#000000", 0.08))
    circ(c, 0, hy, 62, skin)
    if style in ("short", "girl", "grey"):
        hc = "#B8B2A6" if style == "grey" else hair
        c.save(); c.clipRect(skia.Rect.MakeLTRB(-90, hy - 90, 90, hy - 28))
        circ(c, -2, hy - 4, 66, hc); c.restore()
        circ(c, -52, hy - 20, 22, hc)
        if style == "girl":
            rect(c, -50, hy - 62, 100, 18, "#C23B2E", r=9)
            for bxx in (-62, 66):
                sgn = 1 if bxx > 0 else -1
                line(c, bxx, hy + 20, bxx + 6 * sgn, hy + 130, hair, 26)
                circ(c, bxx + 6 * sgn, hy + 140, 11, "#C23B2E")
    elif style == "topi":
        c.save(); c.clipRect(skia.Rect.MakeLTRB(-90, hy - 90, 90, hy - 40)); circ(c, -2, hy, 64, hair); c.restore()
        rect(c, -50, hy - 78, 104, 48, "#F4EFE4", r=16)
        for i in range(5):
            line(c, -40 + i * 20, hy - 70, -40 + i * 20, hy - 38, "#D8CFBC", 4)
        rect(c, -52, hy - 42, 108, 10, "#E1D8C5", r=5)
    fx = 14
    blinking = blink and (t % 3.2) < 0.12
    for ex in (16 + fx, 50 + fx):
        if blinking:
            line(c, ex - 8, hy + 4, ex + 8, hy + 4, DK, 4)
        else:
            circ(c, ex, hy + 2, 12, "#FFFFFF"); circ(c, ex + look * 4, hy + 3, 7, DK)
    for k, ex in enumerate((16 + fx, 50 + fx)):
        yy = hy - 24
        if mood in ("worried", "sad"):
            line(c, ex - 12, yy + (0 if k == 0 else -8), ex + 12, yy + (-8 if k == 0 else 0), DK, 6)
        elif mood == "angry":
            line(c, ex - 12, yy + (-8 if k == 0 else 4), ex + 12, yy + (4 if k == 0 else -8), DK, 6)
        elif mood == "surprised":
            line(c, ex - 12, yy - 10, ex + 12, yy - 10, DK, 6)
        elif mood == "happy":
            arc(c, ex, yy + 8, 14, 200, 340, DK, 5)
        else:
            line(c, ex - 12, yy, ex + 12, yy, DK, 6)
    oval(c, 44 + fx, hy + 22, 7, 9, mix(skin, "#000000", 0.18))
    mx, my = 32 + fx, hy + 42
    if talk > 0.05:
        oval(c, mx, my + 4, 15, 4 + 13 * talk, "#4A1D17"); oval(c, mx, my + 10 + 3 * talk, 9, 4 * talk + 1, "#C0574A")
    elif mood == "happy":
        arc(c, mx, my - 2, 20, 20, 160, "#4A1D17", 6)
    elif mood in ("worried", "sad"):
        arc(c, mx, my + 14, 17, 205, 335, "#4A1D17", 6)
    elif mood == "surprised":
        oval(c, mx, my + 6, 11, 14, "#4A1D17")
    else:
        line(c, mx - 14, my + 4, mx + 14, my + 4, "#4A1D17", 6)
    if mustache:
        arc(c, mx - 8, my - 6, 16, 190, 350, "#1E1612", 9); arc(c, mx + 14, my - 6, 16, 190, 350, "#1E1612", 9)
    if sweat:
        d = (t * 1.5) % 1.0; al = int(230 * (1 - d))
        circ(c, -34, hy - 30 + d * 50, 9, "#FFFFFF", al)
    c.restore()
    return x + facing * fxh * s, y + fyh * s

# ---------------------------------------------------------------- props
def phone(c, cx, cy, w=170, h=330, rot=0.0, screen="cracked", t=0.0, body="#1E1A18", s=1.0, glow=0.0):
    with xform(c, cx, cy, s, rot):
        rect(c, -w / 2 + 6, -h / 2 + 12, w, h, "#000000", r=26, a=60, blur=8)
        rect(c, -w / 2, -h / 2, w, h, body, r=28)
        sx, sy, sw, sh = -w / 2 + 9, -h / 2 + 9, w - 18, h - 18
        if screen == "good":
            grad(c, sx, sy, sw, sh, "#FFE7A8", "#F59E4B")
            for i in range(3):
                for j in range(4):
                    rect(c, sx + 14 + i * (sw - 28) / 3, sy + 40 + j * (sh - 80) / 4, 28, 28,
                         ["#E4572E", "#6BA368", "#F4B942", "#FFFFFF"][(i + j) % 4], r=8)
        elif screen == "notes":
            rect(c, sx, sy, sw, sh, "#FBF6EA", r=20)
            rect(c, sx + 14, sy + 20, sw - 28, 18, "#C0574A", r=6)
            for j in range(6):
                rect(c, sx + 14, sy + 56 + j * 28, (sw - 28) * (0.95 - 0.12 * (j % 3)), 11, "#7A6B58", r=5)
        elif screen == "off":
            rect(c, sx, sy, sw, sh, "#0E0C0B", r=20)
        elif screen == "open":
            rect(c, sx, sy, sw, sh, "#3A332E", r=16)
            rect(c, sx + 12, sy + 20, sw - 24, 60, "#C9A227", r=8)
            circ(c, 0, sy + sh * 0.6, 24, "#9A8F82"); rect(c, sx + 16, sy + sh - 60, sw - 32, 28, "#6B8E4E", r=6)
        else:
            grad(c, sx, sy, sw, sh, "#4B4440", "#1F1B19")
            ox, oy = sx + sw * 0.62, sy + sh * 0.3
            for ang, ln in ((10, 150), (60, 120), (120, 160), (170, 110), (220, 170), (280, 130), (330, 150)):
                a = math.radians(ang); mxp, myp = ox + math.cos(a) * ln * 0.5 + 8, oy + math.sin(a) * ln * 0.5 - 6
                curve(c, [(ox, oy), (mxp, myp), (ox + math.cos(a) * ln, oy + math.sin(a) * ln)], "#E9E1D2", 3, 230)
            for rr in (28, 56):
                arc(c, ox, oy, rr, 20, 300, "#E9E1D2", 2.5, 160)
        if glow > 0:
            radial(c, 0, 0, w * 1.2, "#FFE9A8", "#FFE9A8", int(90 * glow), 0)

def wall_clock(c, cx, cy, r, minute=0.0, hour=None, rim="#4A2F1B", face="#FFF6E0", ticks=True, hands="#2B2118",
               wedge_to=None, wedge_col="#D1452F", shadow_on=True, numerals=True, red_sec=None):
    if hour is None: hour = 10 * 30 + minute * 0.5
    if shadow_on: oval(c, cx + 10, cy + 18, r * 1.02, r * 1.02, "#000000", 60, blur=14)
    circ(c, cx, cy, r, rim); circ(c, cx, cy, r * 0.92, face)
    if wedge_to is not None and wedge_to > 0.5:
        wedge(c, cx, cy, r * 0.86, -90, -90 + wedge_to, wedge_col, 200)
    if ticks:
        for i in range(60):
            a = math.radians(i * 6 - 90); ln = r * (0.1 if i % 5 == 0 else 0.045)
            line(c, cx + math.cos(a) * r * 0.86, cy + math.sin(a) * r * 0.86,
                 cx + math.cos(a) * (r * 0.86 - ln), cy + math.sin(a) * (r * 0.86 - ln), "#3A2B1F",
                 r * (0.022 if i % 5 == 0 else 0.01))
    if numerals:
        for n, lab in ((0, "১২"), (3, "৩"), (6, "৬"), (9, "৯")):
            a = math.radians(n * 30 - 90)
            draw_text(c, lab, cx + math.cos(a) * r * 0.64, cy + math.sin(a) * r * 0.64 + r * 0.075, r * 0.2, "#3A2B1F")
    ah = math.radians(hour - 90); am = math.radians(minute - 90)
    line(c, cx, cy, cx + math.cos(ah) * r * 0.45, cy + math.sin(ah) * r * 0.45, hands, r * 0.055)
    line(c, cx, cy, cx + math.cos(am) * r * 0.7, cy + math.sin(am) * r * 0.7, hands, r * 0.04)
    if red_sec is not None:
        asx = math.radians(red_sec - 90)
        line(c, cx - math.cos(asx) * r * 0.12, cy - math.sin(asx) * r * 0.12,
             cx + math.cos(asx) * r * 0.78, cy + math.sin(asx) * r * 0.78, "#D1452F", r * 0.016)
    circ(c, cx, cy, r * 0.05, "#D1452F")

def coin(c, x, y, r, a=255, label="৳"):
    circ(c, x, y, r, "#C99A2E", a); circ(c, x, y, r * 0.82, "#F2C94C", a)
    draw_text(c, label, x, y + r * 0.32, r * 1.0, "#9A6F12", a)

def check(c, x, y, s, color="#3F9B54", w=18, p=1.0):
    pts = [(x - s * 0.5, y), (x - s * 0.12, y + s * 0.38), (x + s * 0.55, y - s * 0.42)]
    if p <= 0: return
    if p < 0.5:
        q = p / 0.5; pts = [pts[0], (lerp(pts[0][0], pts[1][0], q), lerp(pts[0][1], pts[1][1], q))]
    else:
        q = (p - 0.5) / 0.5; pts = [pts[0], pts[1], (lerp(pts[1][0], pts[2][0], q), lerp(pts[1][1], pts[2][1], q))]
    poly(c, pts, color, stroke=w, close=False)

def cross(c, x, y, s, color="#D1452F", w=18, p=1.0):
    if p <= 0: return
    line(c, x - s * p, y - s * p, x + s * p, y + s * p, color, w); line(c, x + s * p, y - s * p, x - s * p, y + s * p, color, w)

def notebook(c, cx, cy, w, h, rot=0.0, rows=None, p=1.0):
    with xform(c, cx, cy, 1, rot):
        rect(c, -w / 2 + 8, -h / 2 + 12, w, h, "#000000", r=14, a=50, blur=8)
        rect(c, -w / 2, -h / 2, w, h, "#7A3E2B", r=14); rect(c, -w / 2 + 14, -h / 2 + 8, w - 22, h - 16, "#FBF3DE", r=8)
        line(c, -w / 2 + 14, -h / 2 + 8, -w / 2 + 14, h / 2 - 8, "#C0574A", 4)
        for i in range(8):
            yy = -h / 2 + 50 + i * (h - 80) / 8
            line(c, -w / 2 + 24, yy, w / 2 - 14, yy, "#D9CDB2", 2)
        if rows:
            for i, (a_, b_) in enumerate(rows):
                yy = -h / 2 + 50 + i * (h - 80) / 8 - 6
                if p * len(rows) > i:
                    draw_text(c, a_ + " → " + b_, -w / 2 + 34, yy, 26, "#3A2B1F", align="l", bold=False)

def megaphone(c, x, y, s=1.0, rot=0):
    with xform(c, x, y, s, rot):
        poly(c, [(-60, -26), (50, -80), (50, 80), (-60, 26)], "#E4572E"); rect(c, -90, -30, 44, 60, "#2B2118", r=10)
        rect(c, 44, -90, 22, 180, "#F4B942", r=10)
        for i in range(3):
            arc(c, 70, 0, 40 + i * 28, -50, 50, "#2B2118", 6, 200 - i * 50)

def broom(c, x, y, s=1.0, rot=0):
    with xform(c, x, y, s, rot):
        line(c, 0, -90, 0, 60, "#8B5A2B", 12); poly(c, [(-34, 60), (34, 60), (46, 120), (-46, 120)], "#E5C158")
        for i in range(-3, 4): line(c, i * 11, 66, i * 14, 118, "#B58E2C", 3)

def price_tag(c, x, y, text, s=1.0, rot=0, fill="#F4B942"):
    with xform(c, x, y, s, rot):
        poly(c, [(-80, -40), (50, -40), (96, 0), (50, 40), (-80, 40)], fill); circ(c, 62, 0, 9, "#2B2118")
        draw_text(c, text, -16, 14, 38, "#2B2118")

def building(c, x, y, w, h, color, windows=True, wcol="#F4D58D", lit=0.5, seed=0):
    rect(c, x, y - h, w, h, color)
    rect(c, x - 8, y - h - 16, w + 16, 22, mix(color, "#000000", 0.25))
    if windows:
        cols = max(1, int(w // 90)); rows_ = max(1, int(h // 120))
        for i in range(cols):
            for j in range(rows_):
                on = ((i * 7 + j * 3 + seed) % 5) / 5 < lit
                rect(c, x + 22 + i * (w - 44) / cols, y - h + 30 + j * 115, (w - 44) / cols - 20, 70,
                     wcol if on else mix(color, "#000000", 0.35), r=6)

def shop_front(c, cx, base, w, sign="জাহিদ মোবাইল সার্ভিসিং", shutter=0.0, wall="#E7C58D", awning=("#C23B2E", "#F7EBD0"),
               sign_col="#2B2118", lit=True, scale_text=1.0):
    """facade, bottom centre (cx, base). returns opening rect."""
    h = w * 1.1; x = cx - w / 2; top = base - h
    shadow(c, cx, base + 6, w * 0.6, 22, 60)
    rect(c, x, top, w, h, wall)
    rect(c, x - 10, top - 14, w + 20, 26, mix(wall, "#000000", 0.25))
    sh = w * 0.2
    rect(c, x + 20, top + 18, w - 40, sh, sign_col, r=14)
    rect(c, x + 28, top + 26, w - 56, sh - 16, "#F4B942", r=10, stroke=4)
    draw_text(c, sign, cx, top + 18 + sh * 0.62, min(w * 0.082, 64) * scale_text, "#F4B942")
    ox, oy, ow, oh = x + 40, top + sh + 120, w - 80, h - sh - 150
    rect(c, ox, oy, ow, oh, "#2A1D16")
    if lit:
        grad(c, ox, oy, ow, oh, "#FFD58A", "#B8743A")
        rect(c, ox + 20, oy + oh * 0.55, ow - 40, oh * 0.45, "#6B3F22")
        for i in range(3):
            rect(c, ox + 30 + i * (ow - 80) / 3, oy + 30, 50, 80, "#2B2118", r=8)
    n = 8; aw = (w + 30) / n; ay = top + sh + 36
    for i in range(n):
        rect(c, x - 15 + i * aw, ay, aw + 1, 74, awning[i % 2])
        circ(c, x - 15 + (i + 0.5) * aw, ay + 74, aw / 2, awning[i % 2])
    if shutter > 0.001:
        sy = oy + 0; sh2 = oh * shutter
        rect(c, ox - 6, sy - 6, ow + 12, sh2 + 6, "#8A8F8C")
        for k in range(int(sh2 // 22) + 1):
            line(c, ox - 6, sy + 12 + k * 22, ox + ow + 6, sy + 12 + k * 22, "#6C716E", 3)
        rect(c, ox - 6, sy + sh2 - 8, ow + 12, 14, "#5C615E", r=4)
    return (ox, oy, ow, oh)

def rickshaw(c, x, y, s=1.0, t=0.0, color="#E4572E", facing=1):
    with xform(c, x, y, 1, 0, sx=s * facing, sy=s):
        for wx in (-90, 90):
            circ(c, wx, -60, 60, "#2B2118", stroke=12); circ(c, wx, -60, 8, "#2B2118")
            for k in range(6):
                a = math.radians(k * 30 + t * 200); line(c, wx, -60, wx + math.cos(a) * 54, -60 + math.sin(a) * 54, "#8A8F8C", 2)
        rect(c, -120, -190, 200, 80, color, r=16)
        poly(c, [(-130, -190), (-30, -300), (90, -300), (100, -190)], "#F4B942")
        for k in range(5): line(c, -90 + k * 40, -190, -70 + k * 40 + 10, -296, mix("#F4B942", "#000000", 0.2), 3)
        line(c, 90, -60, 130, -190, "#2B2118", 8); line(c, 130, -190, 150, -210, "#2B2118", 8)

def follow_button(c, cx, cy, p=1.0, t=0.0, label="Follow"):
    s = 1 + 0.05 * math.sin(t * 5)
    with xform(c, cx, cy, back_out(p) * s):
        rect(c, -230 + 4, -70 + 10, 460, 140, "#000000", r=70, a=70, blur=8)
        rect(c, -230, -70, 460, 140, "#E4572E", r=70)
        draw_text(c, label, 10, 24, 70, "#FFFFFF")
        circ(c, -150, 0, 34, "#FFFFFF"); line(c, -150, -16, -150, 16, "#E4572E", 8); line(c, -166, 0, -134, 0, "#E4572E", 8)

def question(c, x, y, size, color="#D1452F", a=255, rot=0):
    if size < 2: return
    draw_text(c, "?", x, y, size, color, a, rot=rot)
