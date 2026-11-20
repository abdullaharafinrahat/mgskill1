# Characters, props and background patterns (flat 2D vector style)
import math
import skia
from v_lib import *

SKIN = {"zahid": "#B9774B", "girl": "#C98A5E", "c1": "#A9683F", "c2": "#D49A6A", "old": "#A8693F"}


# ---------------------------------------------------------------- backgrounds
def bg_solid(c, color, extra=400):
    rect(c, -extra, -extra, W + 2 * extra, H + 2 * extra, fill(color))


def bg_grad(c, c1, c2, extra=400, angle="v"):
    if angle == "v":
        p = lin_grad(0, -extra, 0, H + extra, [(c1, 1), (c2, 1)])
    else:
        p = lin_grad(-extra, 0, W + extra, 0, [(c1, 1), (c2, 1)])
    rect(c, -extra, -extra, W + 2 * extra, H + 2 * extra, p)


def bg_bricks(c, c1, c2, x0=-300, y0=-300, x1=1400, y1=2200, bw=150, bh=60, mortar=None, seed=3):
    rect(c, x0, y0, x1 - x0, y1 - y0, fill(mortar or c2))
    r = 0
    y = y0
    while y < y1:
        off = (bw / 2) if r % 2 else 0
        x = x0 - bw + off
        while x < x1:
            shade = ((int(x * 7 + y * 13 + seed * 31) % 5) - 2) * 0.03
            rrect(c, x + 3, y + 3, bw - 6, bh - 6, 6, fill(c1, 1))
            if shade:
                rrect(c, x + 3, y + 3, bw - 6, bh - 6, 6, fill("#000000" if shade < 0 else "#FFFFFF", abs(shade)))
            x += bw
        y += bh
        r += 1


def bg_planks(c, c1, c2, x0=-300, y0=-300, x1=1400, y1=2200, ph=130, horizontal=True):
    rect(c, x0, y0, x1 - x0, y1 - y0, fill(c1))
    i = 0
    y = y0
    while y < y1:
        if i % 2:
            rect(c, x0, y, x1 - x0, ph, fill(c2, 0.35))
        line(c, x0, y, x1, y, "#000000", 4, 0.18)
        i += 1
        y += ph


def bg_stripes(c, c1, c2, w=90, x0=-300, y0=-300, x1=1400, y1=2200, tilt=0):
    rect(c, x0, y0, x1 - x0, y1 - y0, fill(c1))
    c.save()
    c.rotate(tilt)
    x = x0 - 1500
    i = 0
    while x < x1 + 1500:
        if i % 2:
            rect(c, x, y0 - 1500, w, y1 - y0 + 3000, fill(c2))
        x += w
        i += 1
    c.restore()


def bg_dots(c, c1, c2, step=70, r=9, x0=-300, y0=-300, x1=1400, y1=2200, a=1.0):
    rect(c, x0, y0, x1 - x0, y1 - y0, fill(c1))
    p = fill(c2, a)
    y = y0
    j = 0
    while y < y1:
        x = x0 + (step / 2 if j % 2 else 0)
        while x < x1:
            circle(c, x, y, r, p)
            x += step
        y += step * 0.6
        j += 1


def bg_tiles(c, c1, c2, s=120, x0=-300, y0=-300, x1=1400, y1=2200):
    rect(c, x0, y0, x1 - x0, y1 - y0, fill(c1))
    y = y0
    j = 0
    while y < y1:
        x = x0
        i = 0
        while x < x1:
            if (i + j) % 2:
                rect(c, x, y, s, s, fill(c2))
            x += s
            i += 1
        y += s
        j += 1


def bg_rays(c, cx, cy, c1, c2, t, n=18, speed=8):
    bg_solid(c, c1)
    R = 3000
    for i in range(n):
        a0 = (i * 360 / n + t * speed) * math.pi / 180
        a1 = a0 + (180 / n) * math.pi / 180
        poly(c, [(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)), (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill(c2))


def bg_lines_paper(c, base="#F3EBD2", linec="#9CB28A", x0=-300, y0=-300, x1=1400, y1=2200):
    rect(c, x0, y0, x1 - x0, y1 - y0, fill(base))
    y = y0
    while y < y1:
        line(c, x0, y, x1, y, linec, 4, 0.8)
        y += 80
    line(c, 150, y0, 150, y1, "#D96B5C", 5, 0.8)


def vignette(c, a=0.45, color="#000000"):
    p = rad_grad(W / 2, H / 2, 1250, [(color, 0.0), (color, 0.0), (color, a)])
    c.drawRect(skia.Rect.MakeXYWH(-600, -600, W + 1200, H + 1200), p)


# ---------------------------------------------------------------- person
def _ik(sx, sy, hx, hy, l1=150, l2=140, bend=1):
    dx, dy = hx - sx, hy - sy
    d = math.hypot(dx, dy)
    d = min(d, l1 + l2 - 1)
    d = max(d, 40)
    a = math.atan2(dy, dx)
    cosA = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)
    A = math.acos(clamp(cosA, -1, 1))
    ex = sx + l1 * math.cos(a + bend * A)
    ey = sy + l1 * math.sin(a + bend * A)
    # recompute hand to respect clamped distance
    hx2 = sx + d * math.cos(a)
    hy2 = sy + d * math.sin(a)
    return ex, ey, hx2, hy2


def person(c, x, y, s=1.0, skin="#B9774B", shirt="#6B8E4E", pants="#3D3A35", hair="#1B1410", style="short",
           t=0.0, mouth="smile", hl=None, hr=None, legs=False, walk=0.0, mustache=False, brow=0.0,
           look=(0, 0), sleeve="short", shirt2=None, sweat=False, lean=0.0, mouth_open=0.0, flip=1, tilt=0.0):
    """Upper-body figure. (x,y) = waist centre. torso 300 high, head above."""
    c.save()
    c.translate(x, y)
    c.scale(s * flip, s)
    c.rotate(tilt)
    breath = math.sin(t * 2.2) * 4
    # legs
    if legs:
        for sg in (-1, 1):
            ph = walk + (0 if sg < 0 else math.pi)
            fx = sg * 38 + math.sin(ph) * 70
            fy = 360 - max(0, math.cos(ph)) * 26
            line(c, sg * 38, 10, fx, fy - 20, pants, 62)
            oval(c, fx + 14, fy + 4, 46, 20, fill("#2A211B"))
    # torso
    sh = shirt
    p = skia.Path()
    p.moveTo(-100, -270 + breath * 0.3)
    p.quadTo(-105, -300, -60, -300)
    p.lineTo(60, -300)
    p.quadTo(105, -300, 100, -270 + breath * 0.3)
    p.lineTo(112, 20)
    p.lineTo(-112, 20)
    p.close()
    c.drawPath(p, fill(sh))
    if shirt2:
        rect(c, -112, -20, 224, 40, fill(shirt2))
    # collar / buttons
    poly(c, [(-34, -300), (0, -250), (34, -300)], fill(skin))
    line(c, -34, -300, 0, -250, "#000000", 5, 0.25)
    line(c, 34, -300, 0, -250, "#000000", 5, 0.25)
    for i in range(3):
        circle(c, 0, -215 + i * 60, 6, fill("#000000", 0.25))
    # arms
    for side, tgt in ((-1, hl), (1, hr)):
        sx, sy = side * 98, -262 + breath * 0.3
        if tgt is None:
            tgt = (side * 128, 40)
        ex, ey, hx, hy = _ik(sx, sy, tgt[0], tgt[1], bend=-side)
        slv = sh if sleeve in ("short", "long") else skin
        line(c, sx, sy, ex, ey, sh, 56)
        line(c, ex, ey, hx, hy, sh if sleeve == "long" else skin, 46)
        circle(c, hx, hy, 29, fill(skin))
    # neck + head
    rect(c, -26, -330, 52, 50, fill(skin))
    shadow = fill("#000000", 0.15)
    rect(c, -26, -300, 52, 16, shadow)
    hy0 = -400 + breath * 0.5
    c.save()
    c.translate(look[0] * 4, 0)
    if style == "girl":
        for sg in (-1, 1):
            line(c, sg * 78, hy0 - 10, sg * 98, hy0 + 150, hair, 40)
            line(c, sg * 98, hy0 + 150, sg * 96, hy0 + 215, hair, 32)
            circle(c, sg * 96, hy0 + 150, 10, fill("#C0392B"))
    oval(c, 0, hy0, 80, 92, fill(skin))
    oval(c, -82, hy0 + 10, 14, 24, fill(skin))
    oval(c, 82, hy0 + 10, 14, 24, fill(skin))
    # hair
    if style in ("short", "girl", "old"):
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(-120, hy0 - 140, 240, 118))
        oval(c, 0, hy0 - 8, 86, 96, fill(hair))
        c.restore()
        # hairline carve
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(-120, hy0 - 90, 240, 70))
        oval(c, 0, hy0 + 14, 70, 62, fill(skin))
        c.restore()
        if style == "short":
            for sg in (-1, 1):
                oval(c, sg * 78, hy0 - 22, 10, 26, fill(hair))
    if style == "cap":  # white prayer cap (sits above the brows)
        c.save()
        c.clipRect(skia.Rect.MakeXYWH(-100, hy0 - 140, 200, 100))
        oval(c, 0, hy0 - 8, 84, 92, fill("#F2EDE0"))
        c.restore()
        for i in range(-3, 4):
            line(c, i * 20, hy0 - 88, i * 20, hy0 - 52, "#C9C2AE", 4, 0.8)
    # eyes
    blink = 1.0 if (t % 3.7) > 0.12 else 0.1
    for sg in (-1, 1):
        ex_ = sg * 30
        ey_ = hy0 + 6
        oval(c, ex_, ey_, 16, 16 * blink, fill("#FFFFFF"))
        if blink > 0.5:
            circle(c, ex_ + look[0] * 5, ey_ + look[1] * 4, 8.5, fill("#1B1410"))
            circle(c, ex_ + look[0] * 5 + 3, ey_ + look[1] * 4 - 3, 2.6, fill("#FFFFFF"))
        else:
            line(c, ex_ - 14, ey_, ex_ + 14, ey_, "#1B1410", 4)
    # brows (brow>0 worried, <0 angry)
    bc = hair if style != "cap" else "#9A948A"
    for sg in (-1, 1):
        by = hy0 - 30
        xo, xi = sg * 48, sg * 14
        line(c, xo, by + brow * 9, xi, by - brow * 9, bc, 8)
    # nose
    oval(c, 0, hy0 + 26, 8, 6, fill("#000000", 0.2))
    if mustache:
        mp = skia.Path()
        mp.moveTo(0, hy0 + 32)
        mp.quadTo(-26, hy0 + 26, -50, hy0 + 44)
        mp.quadTo(-26, hy0 + 44, 0, hy0 + 42)
        mp.quadTo(26, hy0 + 44, 50, hy0 + 44)
        mp.quadTo(26, hy0 + 26, 0, hy0 + 32)
        c.drawPath(mp, fill(hair if style != "cap" else "#8E897E"))
    # mouth
    my = hy0 + 62
    if mouth == "smile":
        pm = skia.Path(); pm.moveTo(-26, my - 4); pm.quadTo(0, my + 28, 26, my - 4)
        c.drawPath(pm, stroke("#4A1F14", 6))
    elif mouth == "sad":
        pm = skia.Path(); pm.moveTo(-24, my + 10); pm.quadTo(0, my - 14, 24, my + 10)
        c.drawPath(pm, stroke("#4A1F14", 6))
    elif mouth == "flat":
        line(c, -20, my + 2, 20, my + 2, "#4A1F14", 6)
    elif mouth == "open":
        oval(c, 0, my + 6, 20, 10 + mouth_open * 14, fill("#5A1D14"))
        oval(c, 0, my + 14 + mouth_open * 8, 11, 5, fill("#D9695F"))
    elif mouth == "talk":
        o = (math.sin(t * 14) * 0.5 + 0.5)
        oval(c, 0, my + 4, 18, 5 + o * 13, fill("#5A1D14"))
    if sweat:
        d = (t * 1.6) % 1.0
        sx_ = 95
        sy_ = hy0 - 40 + d * 70
        dp = skia.Path()
        dp.moveTo(sx_, sy_ - 22); dp.quadTo(sx_ + 18, sy_ + 6, sx_, sy_ + 14); dp.quadTo(sx_ - 18, sy_ + 6, sx_, sy_ - 22)
        c.drawPath(dp, fill("#EAF4F8", 1 - d * 0.6))
    c.restore()
    c.restore()


# ---------------------------------------------------------------- props
def phone(c, x, y, w=300, h=600, rot=0, state="on", t=0.0, crack=1.0, accent="#E8B23A", title="", scale=1.0, back="#2B2B2B"):
    c.save()
    c.translate(x, y)
    c.rotate(rot)
    c.scale(scale, scale)
    rrect(c, -w / 2 + 10, -h / 2 + 14, w, h, w * 0.14, fill("#000000", 0.22))
    rrect(c, -w / 2, -h / 2, w, h, w * 0.14, fill(back))
    sw, sh_ = w - 26, h - 26
    sx, sy = -sw / 2, -sh_ / 2
    r = w * 0.11
    if state == "bare":
        rrect(c, sx, sy, sw, sh_, r, fill("#6C645A"))
        rrect(c, sx + 30, sy + 40, sw - 60, sh_ * 0.35, 12, fill("#3C3731"))
        circle(c, sx + sw * 0.3, sy + sh_ * 0.62, 38, fill("#B88A3E"))
        rrect(c, sx + sw * 0.5, sy + sh_ * 0.55, sw * 0.38, 30, 8, fill("#8A7A5E"))
        rrect(c, sx + 30, sy + sh_ * 0.78, sw - 60, 40, 10, fill("#8A7A5E"))
    else:
        c.save()
        c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(sx, sy, sw, sh_), r, r), True)
        if state == "off" or state == "cracked":
            rect(c, sx, sy, sw, sh_, lin_grad(sx, sy, sx + sw, sy + sh_, [("#1E1B19", 1), ("#3A322C", 1)]))
        elif state == "notes":
            rect(c, sx, sy, sw, sh_, fill("#FFF8E8"))
            rect(c, sx, sy, sw, 90, fill("#C96F3B"))
            draw_text(c, title or "পড়া", 0, sy + 62, 52, "#FFF8E8", "b")
            for i in range(7):
                rrect(c, sx + 28, sy + 130 + i * 62, sw - 56 - (i % 3) * 50, 16, 8, fill("#6C5B4A", 0.55))
        else:  # on / new
            rect(c, sx, sy, sw, sh_, lin_grad(sx, sy, sx + sw, sy + sh_, [("#F4C26B", 1), ("#D9703F", 1)]))
            for i in range(3):
                for j in range(4):
                    rrect(c, sx + 28 + i * (sw - 56) / 3, sy + 90 + j * 110, (sw - 56) / 3 - 20, 82, 20,
                          fill(["#FFF3D6", "#7C9A5B", "#B9402E", "#F2D16B"][(i + j) % 4], 0.95))
            draw_text(c, "১২:০০", 0, sy + 58, 46, "#FFFFFF", "b")
        c.restore()
        if state == "cracked":
            cx0, cy0 = sx + sw * 0.62, sy + sh_ * 0.38
            pts = [(-1, -1.2), (1.0, -0.9), (1.2, 0.3), (0.4, 1.4), (-1.2, 0.8), (-0.4, 0.2), (0.9, 1.4), (-1, 1.7)]
            for k, (dx, dy) in enumerate(pts):
                pr = clamp(crack * 1.6 - k * 0.07, 0, 1)
                if pr <= 0:
                    continue
                ex, ey = cx0 + dx * sw * 0.55 * pr, cy0 + dy * sh_ * 0.3 * pr
                mx, my2 = (cx0 + ex) / 2 + 12 * ((k % 2) * 2 - 1), (cy0 + ey) / 2
                pp = skia.Path(); pp.moveTo(cx0, cy0); pp.lineTo(mx, my2); pp.lineTo(ex, ey)
                c.drawPath(pp, stroke("#EDE6D8", 4))
    # notch / speaker
    rrect(c, -34, -h / 2 + 6, 68, 12, 6, fill("#111111"))
    c.restore()


def wall_clock(c, x, y, r, minutes=0.0, t=0.0, tick=True, rim="#7A4A2A", face="#F6EDD8", hour_extra=0.0):
    c.save()
    c.translate(x, y)
    circle(c, 6, 10, r + 14, fill("#000000", 0.22))
    circle(c, 0, 0, r + 14, fill(rim))
    circle(c, 0, 0, r + 14, stroke("#4A2B15", 6))
    circle(c, 0, 0, r, fill(face))
    for i in range(60):
        a = i * math.pi / 30
        L = r * (0.11 if i % 5 == 0 else 0.05)
        w = 7 if i % 5 == 0 else 3
        line(c, math.sin(a) * (r - 8), -math.cos(a) * (r - 8), math.sin(a) * (r - 8 - L), -math.cos(a) * (r - 8 - L), "#3A2A1E", w, 1, )
    for i, lab in ((0, "১২"), (3, "৩"), (6, "৬"), (9, "৯")):
        a = i * math.pi / 6
        draw_text(c, lab, math.sin(a) * r * 0.66, -math.cos(a) * r * 0.66 + r * 0.09, r * 0.24, "#3A2A1E", "b")
    ma = minutes * 6 * math.pi / 180
    ha = (minutes / 60 * 30 + hour_extra) * math.pi / 180
    line(c, 0, 0, math.sin(ha) * r * 0.5, -math.cos(ha) * r * 0.5, "#2A1A10", 12)
    line(c, 0, 0, math.sin(ma) * r * 0.78, -math.cos(ma) * r * 0.78, "#2A1A10", 8)
    sa = (t * 6 if tick else 0) * math.pi / 180
    sa = math.floor(t) * 6 * math.pi / 180 + ease(prog(t % 1, 0, 0.15)) * 6 * math.pi / 180 if tick else 0
    line(c, -math.sin(sa) * r * 0.15, math.cos(sa) * r * 0.15, math.sin(sa) * r * 0.82, -math.cos(sa) * r * 0.82, "#B9402E", 4)
    circle(c, 0, 0, 12, fill("#B9402E"))
    c.restore()


def stopwatch(c, x, y, r, sec=0.0, face="#F6EDD8", body="#B58A3A", label=""):
    c.save()
    c.translate(x, y)
    rrect(c, -r * 0.18, -r - r * 0.36, r * 0.36, r * 0.3, 8, fill("#8A6A2A"))
    circle(c, r * 0.8, -r * 0.8, r * 0.14, fill("#8A6A2A"))
    circle(c, 6, 10, r + 10, fill("#000000", 0.2))
    circle(c, 0, 0, r + 10, fill(body))
    circle(c, 0, 0, r, fill(face))
    for i in range(12):
        a = i * math.pi / 6
        line(c, math.sin(a) * (r - 6), -math.cos(a) * (r - 6), math.sin(a) * (r - 22), -math.cos(a) * (r - 22), "#3A2A1E", 5)
    a = sec * 6 * math.pi / 180
    line(c, 0, 0, math.sin(a) * r * 0.78, -math.cos(a) * r * 0.78, "#B9402E", 7)
    circle(c, 0, 0, 10, fill("#3A2A1E"))
    if label:
        draw_text(c, label, 0, r * 0.55, r * 0.3, "#3A2A1E", "b")
    c.restore()


def signboard(c, x, y, w, h, text, bg="#B9402E", fg="#FFF3D6", size=70, border="#F2D16B", key="b"):
    rrect(c, x - w / 2 + 10, y - h / 2 + 14, w, h, 22, fill("#000000", 0.25))
    rrect(c, x - w / 2, y - h / 2, w, h, 22, fill(bg))
    rrect(c, x - w / 2 + 12, y - h / 2 + 12, w - 24, h - 24, 14, stroke(border, 5))
    lines = text.split("\n")
    lh = size * 1.25
    y0 = y - (len(lines) - 1) * lh / 2 + size * 0.34
    for i, l in enumerate(lines):
        draw_text(c, l, x, y0 + i * lh, size, fg, key)


def counter(c, x, y, w, h=170, top="#8A5A34", front="#6B4226", items=True):
    rrect(c, x - w / 2, y, w, 34, 10, fill(top))
    rect(c, x - w / 2 + 10, y + 34, w - 20, h - 34, fill(front))
    for i in range(int(w // 160)):
        rrect(c, x - w / 2 + 30 + i * 160, y + 56, 120, h - 90, 8, fill("#000000", 0.12))


def calendar(c, x, y, w, h, title="", marks=(), cur=None, hl=None, col1="#B9402E", rows=5):
    rrect(c, x - w / 2 + 10, y - h / 2 + 12, w, h, 20, fill("#000000", 0.22))
    rrect(c, x - w / 2, y - h / 2, w, h, 20, fill("#FFF8E8"))
    rrect(c, x - w / 2, y - h / 2, w, 110, 20, fill(col1))
    rect(c, x - w / 2, y - h / 2 + 70, w, 40, fill(col1))
    draw_text(c, title, x, y - h / 2 + 76, 56, "#FFF3D6", "b")
    cw, ch = (w - 40) / 7, (h - 150) / rows
    for r_ in range(rows):
        for q in range(7):
            n = r_ * 7 + q + 1
            cx_, cy_ = x - w / 2 + 20 + q * cw + cw / 2, y - h / 2 + 130 + r_ * ch + ch / 2
            if hl is not None and hl[0] <= r_ <= hl[1]:
                rrect(c, cx_ - cw / 2 + 3, cy_ - ch / 2 + 3, cw - 6, ch - 6, 10, fill("#F2D16B", 0.6))
            if n <= 30:
                draw_text(c, bn(n), cx_, cy_ + 14, 36, "#4A3A2A", "m")


BN = "০১২৩৪৫৬৭৮৯"


def bn(n):
    return "".join(BN[int(d)] for d in str(n))


def bulb(c, x, y, r, on=1.0):
    if on > 0:
        circle(c, x, y, r * 2.2, rad_grad(x, y, r * 2.2, [("#FFE08A", 0.55 * on), ("#FFE08A", 0.0)]))
    circle(c, x, y, r, fill("#FFD966"))
    rrect(c, x - r * 0.45, y + r * 0.8, r * 0.9, r * 0.6, 6, fill("#8A8A8A"))
    for i in range(8):
        a = i * math.pi / 4 + math.pi / 8
        line(c, x + math.cos(a) * r * 1.5, y + math.sin(a) * r * 1.5, x + math.cos(a) * r * 1.9, y + math.sin(a) * r * 1.9, "#FFD966", 6, on)


def moon(c, x, y, r, col_="#F6E7B4"):
    circle(c, x, y, r * 1.8, rad_grad(x, y, r * 1.8, [(col_, 0.35), (col_, 0.0)]))
    circle(c, x, y, r, fill(col_))
    circle(c, x + r * 0.45, y - r * 0.2, r * 0.9, fill("#2E2420"))


def sun(c, x, y, r, t=0.0, col_="#F6B93B"):
    for i in range(14):
        a = i * math.pi * 2 / 14 + t * 0.4
        line(c, x + math.cos(a) * r * 1.3, y + math.sin(a) * r * 1.3, x + math.cos(a) * r * 1.75, y + math.sin(a) * r * 1.75, col_, 14)
    circle(c, x, y, r, fill(col_))


def tag_price(c, x, y, s=1.0, text="৳", rot=-12):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    poly(c, [(-90, -50), (60, -50), (110, 0), (60, 50), (-90, 50)], fill("#F2D16B"))
    circle(c, 70, 0, 12, fill("#7A5A2A"))
    draw_text(c, text, -10, 22, 70, "#4A3A2A", "b")
    c.restore()


def cross_mark(c, x, y, s, color="#C0392B", p=1.0):
    pr = ease(p)
    line(c, x - s, y - s, x - s + 2 * s * min(1, pr * 2), y - s + 2 * s * min(1, pr * 2), color, s * 0.3)
    if pr > 0.5:
        q = (pr - 0.5) * 2
        line(c, x + s, y - s, x + s - 2 * s * q, y - s + 2 * s * q, color, s * 0.3)
