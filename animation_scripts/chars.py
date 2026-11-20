# -*- coding: utf-8 -*-
"""Characters and props (flat 2D style)."""
import math
from engine import *

SKIN = ["#C98E63", "#B87A52", "#E0A982", "#A9693F"]


# ------------------------------------------------------------------ person
def _arm(ctx, sx, side, a1, a2, shirt, skin, prop=None):
    L1, L2 = 88, 80
    ex = sx + L1 * side * math.sin(math.radians(a1))
    ey = -278 + L1 * math.cos(math.radians(a1))
    hx = ex + L2 * side * math.sin(math.radians(a2))
    hy = ey + L2 * math.cos(math.radians(a2))
    line(ctx, sx, -278, ex, ey, shirt, 40)
    line(ctx, ex, ey, hx, hy, skin, 30)
    circ(ctx, hx, hy, 18, skin)
    if prop:
        ctx.save()
        ctx.translate(hx, hy)
        prop(ctx)
        ctx.restore()
    return hx, hy


def person(ctx, x, y, sc=1.0, skin="#C98E63", hair="#2A1B14", shirt="#D9822B", pants="#4A3A32",
           arms=((12, 8), (12, 8)), mouth=0.0, emo="n", look=0.0, blink=0.0, walk=None, flip=1,
           hs="short", acc=(), bob=0.0, tilt=0.0, propR=None, propL=None, behind=None, head_rot=0.0,
           lower=True, shoe="#2A1D17", ly=0.0, front_r=False):
    """Origin at feet. arms = ((upperR, foreR),(upperL, foreL)); angle 0 = down, 90 = sideways, 180 = up."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(sc * flip, sc)
    ctx.translate(0, bob)
    if behind:
        behind(ctx)
    if "backpack" in acc:
        rect(ctx, -52, -300, 104, 150, "#C0503A", 30, sc="#8F3523", lw=4)
        rect(ctx, -56, -250, 112, 30, "#8F3523", 10)
    # legs
    if lower:
        for side in (-1, 1):
            a = 0.0
            lift = 0.0
            if walk is not None:
                a = math.sin(walk + (0 if side > 0 else math.pi)) * 0.5
                lift = max(0, math.sin(walk + (0 if side > 0 else math.pi))) * 18
            hx, hy = side * 28, -150
            fx, fy = hx + 150 * math.sin(a), hy + 150 * math.cos(a) - lift
            line(ctx, hx, hy, fx, fy, pants, 44)
            ell(ctx, fx + 8 + 6 * math.sin(a), fy + 4, 30, 14, shoe)
    # torso
    rect(ctx, -60, -300, 120, 160, shirt, 38)
    if "apron" in acc:
        rect(ctx, -46, -250, 92, 112, "#7B4B2A", 18)
        rect(ctx, -22, -228, 44, 30, "#5E3719", 8)
    if "tie" in acc:
        poly(ctx, [(-12, -300), (12, -300), (18, -230), (0, -205), (-18, -230)], "#9C2F2F")
    if "kurta" in acc:
        line(ctx, 0, -298, 0, -220, mix(shirt, "#000000", 0.18), 4)
        for k in range(3):
            circ(ctx, 0, -280 + k * 24, 4, "#F6EBD0")
    # neck
    rect(ctx, -17, -330, 34, 40, mix(skin, "#000000", 0.12), 6)
    # arms
    (aR, bR), (aL, bL) = arms
    if not front_r:
        _arm(ctx, 58, 1, aR, bR, shirt, skin, propR)
    _arm(ctx, -58, -1, aL, bL, shirt, skin, propL)
    # head
    ctx.save()
    ctx.translate(0, -300)
    ctx.rotate(head_rot)
    ctx.translate(0, 300)
    hy = -362
    if hs == "long":
        rect(ctx, -72, hy - 20, 144, 170, hair, 60)
    if hs == "bun":
        circ(ctx, 0, hy - 78, 28, hair)
    circ(ctx, -62, hy + 6, 14, skin)
    circ(ctx, 62, hy + 6, 14, skin)
    circ(ctx, 0, hy - 14, 69, hair) if hs not in ("bald", "cap", "topi") else None
    circ(ctx, 0, hy, 62, skin)
    if hs in ("short", "long", "bun"):
        # fringe
        ctx.new_path()
        ctx.arc(0, hy - 4, 64, math.pi * 1.04, math.pi * 1.96)
        ctx.curve_to(40, hy - 44, -10, hy - 30, -64, hy - 22)
        ctx.close_path()
        setc(ctx, hair)
        ctx.fill()
    if hs == "pigtail":
        circ(ctx, -76, hy + 30, 22, hair)
        circ(ctx, 76, hy + 30, 22, hair)
        circ(ctx, 0, hy - 14, 69, hair)
        circ(ctx, 0, hy, 62, skin)
        ctx.new_path()
        ctx.arc(0, hy - 4, 64, math.pi * 1.04, math.pi * 1.96)
        ctx.curve_to(40, hy - 44, -10, hy - 30, -64, hy - 22)
        ctx.close_path()
        setc(ctx, hair)
        ctx.fill()
    if hs == "cap":
        ctx.new_path()
        ctx.arc(0, hy - 8, 66, math.pi, math.tau)
        ctx.close_path()
        setc(ctx, "#B8452E")
        ctx.fill()
        rect(ctx, -10, hy - 20, 84, 14, "#8F3523", 7)
    if hs == "topi":
        rect(ctx, -52, hy - 80, 104, 44, "#F4EDE0", 20, sc="#CFC3B0", lw=3)
    # eyes
    eb = 1 - blink
    for sx in (-24, 24):
        ell(ctx, sx, hy + 2, 12, max(13 * eb, 1.5), "#FFFFFF")
        circ(ctx, sx + look * 4, hy + 3 + ly * 4, 6 * (1 if eb > 0.4 else 0.4), "#1B1210")
    by = hy - 26
    if emo == "sad":
        line(ctx, -36, by + 4, -14, by - 4, hair, 6)
        line(ctx, 36, by + 4, 14, by - 4, hair, 6)
    elif emo == "angry":
        line(ctx, -36, by - 6, -14, by + 4, hair, 7)
        line(ctx, 36, by - 6, 14, by + 4, hair, 7)
    elif emo == "surprised":
        arc_stroke(ctx, -24, by + 14, 14, math.pi * 1.1, math.pi * 1.9, hair, 6)
        arc_stroke(ctx, 24, by + 14, 14, math.pi * 1.1, math.pi * 1.9, hair, 6)
    elif emo == "think":
        line(ctx, -36, by, -14, by - 6, hair, 6)
        line(ctx, 36, by - 8, 14, by - 2, hair, 6)
    else:
        line(ctx, -36, by, -14, by - 2, hair, 6)
        line(ctx, 36, by, 14, by - 2, hair, 6)
    circ(ctx, -42, hy + 26, 10, "#E07A6A", 0.35)
    circ(ctx, 42, hy + 26, 10, "#E07A6A", 0.35)
    # nose
    ell(ctx, 0, hy + 16, 6, 8, mix(skin, "#000000", 0.14))
    # mouth
    my = hy + 40
    if mouth > 0.08:
        ell(ctx, 0, my + mouth * 5, 15 + mouth * 3, 4 + mouth * 14, "#6B1E1A")
        ell(ctx, 0, my + mouth * 12, 9, 3 + mouth * 4, "#E0766B")
    else:
        if emo == "sad":
            arc_stroke(ctx, 0, my + 12, 15, math.pi * 1.15, math.pi * 1.85, "#5A2A1E", 5)
        elif emo in ("happy", "proud"):
            ctx.new_path()
            ctx.arc(0, my - 6, 20, 0.15, math.pi - 0.15)
            ctx.close_path()
            setc(ctx, "#6B1E1A")
            ctx.fill()
            ell(ctx, 0, my + 8, 9, 4, "#E0766B")
        elif emo == "surprised":
            ell(ctx, 0, my + 6, 9, 12, "#6B1E1A")
        elif emo == "angry":
            line(ctx, -12, my + 6, 12, my + 6, "#5A2A1E", 5)
        else:
            arc_stroke(ctx, 0, my - 8, 14, math.pi * 0.2, math.pi * 0.8, "#5A2A1E", 5)
    if "mustache" in acc:
        ell(ctx, -13, my - 10, 16, 7, hair, rot=0.25)
        ell(ctx, 13, my - 10, 16, 7, hair, rot=-0.25)
    if "beard" in acc:
        ctx.new_path()
        ctx.arc(0, hy + 20, 62, 0.25, math.pi - 0.25)
        ctx.curve_to(-30, hy + 36, 30, hy + 36, 56, hy + 36)
        ctx.close_path()
        setc(ctx, "#D8D2C6")
        ctx.fill()
    if "glasses" in acc:
        circ(ctx, -24, hy + 2, 18, None, 1, "#3B2A22", 5)
        circ(ctx, 24, hy + 2, 18, None, 1, "#3B2A22", 5)
        line(ctx, -6, hy + 2, 6, hy + 2, "#3B2A22", 5)
    ctx.restore()
    if front_r:
        _arm(ctx, 58, 1, aR, bR, shirt, skin, propR)
    ctx.restore()


# ------------------------------------------------------------------ props
def phone(ctx, x, y, w=120, h=230, state="on", rot=0.0, body="#2B2523", crack=1.0, scr="#F5EFE3", sc=1.0, icons=True):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(sc, sc)
    rect(ctx, -w / 2, -h / 2, w, h, body, w * 0.14)
    m = w * 0.06
    sx, sy, sw, sh = -w / 2 + m, -h / 2 + m * 2.2, w - 2 * m, h - m * 4.4
    if state == "off":
        rect(ctx, sx, sy, sw, sh, "#1A1514", w * 0.08)
    else:
        rect(ctx, sx, sy, sw, sh, scr, w * 0.08)
        if icons:
            cols = ["#E07A3F", "#6FA35B", "#E9B443", "#C9573F", "#8D6A4E", "#D98BA0"]
            for r_ in range(3):
                for c_ in range(3):
                    rect(ctx, sx + sw * 0.1 + c_ * sw * 0.3, sy + sh * 0.1 + r_ * sh * 0.14, sw * 0.22, sw * 0.22,
                         cols[(r_ * 3 + c_) % 6], sw * 0.06)
    if state == "crack" or crack < 1 and state == "on" and False:
        pass
    if state == "crack":
        cc = "#3A2E2A"
        ox, oy = sx + sw * 0.7, sy + sh * 0.25
        segs = [[(ox, oy), (ox - sw * 0.35, oy + sh * 0.2), (ox - sw * 0.6, oy + sh * 0.18)],
                [(ox, oy), (ox - sw * 0.1, oy + sh * 0.35), (ox - sw * 0.5, oy + sh * 0.6)],
                [(ox, oy), (ox + sw * 0.05, oy + sh * 0.5), (ox - sw * 0.05, oy + sh * 0.7)],
                [(ox, oy), (ox - sw * 0.2, oy - sh * 0.15)],
                [(ox - sw * 0.1, oy + sh * 0.35), (ox + sw * 0.15, oy + sh * 0.45)]]
        for sgm in segs:
            pline(ctx, sgm, cc, max(2, w * 0.018))
            pline(ctx, [(a + 3, b + 3) for a, b in sgm], "#FFFFFF", max(1, w * 0.01), 0.4)
    rect(ctx, -w * 0.12, -h / 2 + m * 0.7, w * 0.24, m * 0.7, "#0F0C0B", m * 0.35)
    ctx.restore()


def clock(ctx, x, y, r, minutes=0.0, face="#F6EBD3", rim="#6B4226", hands="#2B1D14", sec=None, shake_=0.0, tick=True):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(shake_)
    circ(ctx, 0, 0, r * 1.08, rim)
    circ(ctx, 0, 0, r * 1.0, mix(rim, "#000000", 0.2))
    circ(ctx, 0, 0, r * 0.93, face)
    for i in range(60):
        a = i / 60 * math.tau - math.pi / 2
        big = i % 5 == 0
        r0 = r * (0.78 if big else 0.86)
        line(ctx, r0 * math.cos(a), r0 * math.sin(a), r * 0.9 * math.cos(a), r * 0.9 * math.sin(a), hands,
             r * (0.035 if big else 0.015), cap=cairo.LINE_CAP_BUTT)
    ma = (minutes % 60) / 60 * math.tau - math.pi / 2
    ha = (minutes / 720.0) * math.tau - math.pi / 2 + math.radians(300)
    line(ctx, 0, 0, r * 0.5 * math.cos(ha), r * 0.5 * math.sin(ha), hands, r * 0.075)
    line(ctx, 0, 0, r * 0.76 * math.cos(ma), r * 0.76 * math.sin(ma), hands, r * 0.05)
    if sec is not None:
        sa = sec * math.tau - math.pi / 2
        line(ctx, 0, 0, r * 0.82 * math.cos(sa), r * 0.82 * math.sin(sa), "#C0392B", r * 0.018)
    circ(ctx, 0, 0, r * 0.07, "#C0392B")
    ctx.restore()


def stopwatch(ctx, x, y, r, frac=0.0, body="#D6A84B", face="#FFF8E6", ring="#B4832D", num=True, hand_c="#C0392B"):
    ctx.save()
    ctx.translate(x, y)
    rect(ctx, -r * 0.16, -r * 1.35, r * 0.32, r * 0.3, ring, r * 0.06)
    rect(ctx, -r * 0.25, -r * 1.45, r * 0.5, r * 0.16, ring, r * 0.06)
    circ(ctx, 0, 0, r * 1.08, ring)
    circ(ctx, 0, 0, r, body)
    circ(ctx, 0, 0, r * 0.85, face)
    for i in range(60):
        a = i / 60 * math.tau - math.pi / 2
        big = i % 5 == 0
        r0 = r * (0.62 if big else 0.72)
        line(ctx, r0 * math.cos(a), r0 * math.sin(a), r * 0.8 * math.cos(a), r * 0.8 * math.sin(a), "#4A3526",
             r * (0.035 if big else 0.015), cap=cairo.LINE_CAP_BUTT)
    if frac > 0:
        arc_stroke(ctx, 0, 0, r * 0.5, -math.pi / 2, -math.pi / 2 + frac * math.tau, hand_c, r * 0.1, 0.35)
    a = frac * math.tau - math.pi / 2
    line(ctx, 0, 0, r * 0.7 * math.cos(a), r * 0.7 * math.sin(a), hand_c, r * 0.05)
    circ(ctx, 0, 0, r * 0.07, "#4A3526")
    ctx.restore()


def bubble(ctx, x, y, s, size=54, tx=None, ty=None, fill="#FFFFFF", col="#2B1D14", p=1.0, maxw=520, edge="#2B1D14",
           fam="sans", tail=1):
    """Speech bubble centered at x,y with tail to (tx,ty). p = pop scale"""
    if p <= 0.01:
        return
    tw, th = text_w(s, size, maxw=maxw, fam=fam)
    w, h = tw + 20, th + 14
    tx = x - w * 0.2 if tx is None else tx
    ty = y + h / 2 + 60 if ty is None else ty
    ctx.save()
    ctx.translate(tx, ty)
    ctx.scale(p, p)
    ctx.translate(-tx, -ty)
    if tail:
        bx = clamp(tx, x - w / 2 + 40, x + w / 2 - 40)
        by = y + h / 2 - 4 if ty > y else y - h / 2 + 4
        poly(ctx, [(bx - 26, by), (bx + 26, by), (tx, ty)], edge)
        poly(ctx, [(bx - 20, by - (3 if ty > y else -3)), (bx + 20, by - (3 if ty > y else -3)), (tx, ty - (6 if ty > y else -6))], fill)
    rect(ctx, x - w / 2, y - h / 2, w, h, fill, 38, sc=edge, lw=6)
    if tail:
        bx = clamp(tx, x - w / 2 + 40, x + w / 2 - 40)
        by = y + h / 2 if ty > y else y - h / 2
        rect(ctx, bx - 19, by - 5, 38, 10, fill)
    text(ctx, s, x, y, size, col, maxw=maxw, fam=fam)
    ctx.restore()


def poster(ctx, x, y, w, h, c="#FFF4D6", edge="#6B4226", tilt=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(tilt)
    rect(ctx, -w / 2 + 10, -h / 2 + 14, w, h, "#000000", 10, 0.18)
    rect(ctx, -w / 2, -h / 2, w, h, c, 10, sc=edge, lw=8)
    ctx.restore()


def tape(ctx, x, y, w=80, h=30, rot=0.2, c="#E8D9A8"):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    rect(ctx, -w / 2, -h / 2, w, h, c, 3, 0.85)
    ctx.restore()


def counter(ctx, x, y, w, h=300, top="#8A5A33", front="#B9794A", items=True):
    rect(ctx, x, y, w, h, front)
    for i in range(0, int(w), 140):
        rect(ctx, x + i + 14, y + 40, 110, h - 70, mix(front, "#000000", 0.1), 8)
    rect(ctx, x - 20, y - 26, w + 40, 40, top, 10)


def shelf(ctx, x, y, w, c="#6B4226", boxes=True, seed=2):
    rect(ctx, x, y, w, 20, c, 4)
    rnd = random.Random(seed)
    if boxes:
        cx = x + 14
        cols = ["#E9B443", "#C9573F", "#6FA35B", "#D98BA0", "#E07A3F", "#F0E0BC"]
        while cx < x + w - 70:
            bw = rnd.randint(46, 84)
            bh = rnd.randint(50, 100)
            if cx + bw > x + w - 6:
                break
            rect(ctx, cx, y - bh, bw, bh, rnd.choice(cols), 6)
            cx += bw + rnd.randint(6, 18)


def wall_interior(ctx, wall="#E8C99A", floor="#9C6B45", fy=1280, panel="#D4A870"):
    bg(ctx, wall)
    rect(ctx, -1500, fy, 4200, 1200, floor)
    for i in range(-1500, 2700, 160):
        line(ctx, i, fy, i - 140, fy + 700, mix(floor, "#000000", 0.18), 4, cap=cairo.LINE_CAP_BUTT)
    rect(ctx, -1500, fy - 30, 4200, 30, mix(wall, "#000000", 0.25))
    rect(ctx, -1500, fy - 330, 4200, 300, panel)
    for i in range(-1500, 2700, 180):
        line(ctx, i, fy - 330, i, fy - 30, mix(panel, "#000000", 0.1), 4, cap=cairo.LINE_CAP_BUTT)


def shop_front(ctx, x, y, w, h, wall="#C96F4A", sign_bg="#2F4F2A", sign_txt="জাহিদ মোবাইল সার্ভিসিং",
               shutter=0.0, glow=0.0, t=0.0, awning="#E9B443", size=46, dark=False):
    """x,y = top-left."""
    rect(ctx, x, y, w, h, wall)
    for i in range(0, int(h), 60):
        line(ctx, x, y + i, x + w, y + i, mix(wall, "#000000", 0.08), 3, cap=cairo.LINE_CAP_BUTT)
    # sign
    rect(ctx, x + w * 0.06, y + 30, w * 0.88, h * 0.18, sign_bg, 14, sc="#F3E6C4", lw=6)
    if glow > 0:
        rgrad(ctx, x + w / 2, y + 30 + h * 0.09, w * 0.7, "#FFE49A", 0.45 * glow, 0)
    text(ctx, sign_txt, x + w / 2, y + 30 + h * 0.09, size, "#FFF3C9", maxw=w * 0.82)
    # awning stripes
    ay = y + h * 0.26
    n = 8
    sw_ = w / n
    for i in range(n):
        poly(ctx, [(x + i * sw_, ay), (x + (i + 1) * sw_, ay), (x + (i + 1) * sw_ - 6, ay + 70), (x + i * sw_ + 6, ay + 70)],
             awning if i % 2 == 0 else "#F6EBD0")
        circ(ctx, x + i * sw_ + sw_ / 2, ay + 70, sw_ / 2 - 4, awning if i % 2 == 0 else "#F6EBD0")
    # opening
    ox, oy, ow, oh = x + w * 0.08, ay + 110, w * 0.84, h - (ay - y) - 110
    rect(ctx, ox, oy, ow, oh, "#3B261A" if not dark else "#1E130D")
    rect(ctx, ox + 14, oy + 14, ow - 28, oh - 14, "#E9C58E" if not dark else "#5B3A22")
    if shutter > 0:
        sh = oh * shutter
        rect(ctx, ox, oy, ow, sh, "#9A9387")
        for i in range(0, int(sh), 24):
            line(ctx, ox, oy + i, ox + ow, oy + i, "#6F695E", 3, cap=cairo.LINE_CAP_BUTT)
        rect(ctx, ox, oy + sh - 14, ow, 14, "#6F695E")
        circ(ctx, ox + ow / 2, oy + sh - 7, 9, "#3F3A32")
    return ox, oy, ow, oh


def building(ctx, x, y, w, h, c, win="#F2E3C0", cols=4, rows=6, wa=1.0):
    rect(ctx, x, y, w, h, c)
    gw = w / (cols * 2 + 1)
    gh = h / (rows * 2 + 1)
    for r_ in range(rows):
        for c_ in range(cols):
            rect(ctx, x + gw * (1 + c_ * 2), y + gh * (1 + r_ * 2), gw, gh, win, 2, wa)


def chair(ctx, x, y, c="#8E4B32"):
    rect(ctx, x - 40, y - 100, 80, 14, c, 6)
    rect(ctx, x - 44, y - 100, 14, 100, c, 5)
    rect(ctx, x - 44, y - 30, 88, 16, c, 6)
    line(ctx, x - 34, y - 14, x - 34, y + 50, c, 10)
    line(ctx, x + 34, y - 14, x + 34, y + 50, c, 10)


def bulb(ctx, x, y, r, on=1.0):
    if on > 0:
        rgrad(ctx, x, y, r * 3.5, "#FFE08A", 0.65 * on, 0)
        for i in range(10):
            a = i / 10 * math.tau
            line(ctx, x + math.cos(a) * r * 1.5, y + math.sin(a) * r * 1.5, x + math.cos(a) * r * 2.1,
                 y + math.sin(a) * r * 2.1, "#F2B53A", r * 0.12, on)
    circ(ctx, x, y, r, "#FFE9A0" if on > 0 else "#D8D0BC", 1.0, "#B58A2D", r * 0.08)
    rect(ctx, x - r * 0.45, y + r * 0.85, r * 0.9, r * 0.55, "#8A7B66", r * 0.1)


def question(ctx, x, y, size, c="#2B1D14", a=1.0, rot=0.0, sc=1.0):
    text(ctx, "?", x, y, size, c, a=a, rot=rot, sc=sc, fam="la" and "sans")


def balloon(ctx, x, y, r, c, label=None, size=50, lc="#ffffff", t=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(math.sin(t * 1.3 + x) * 0.06)
    pts = [(0, r * 1.25), (-12, r * 1.5), (12, r * 1.5)]
    poly(ctx, pts, c)
    pline(ctx, [(0, r * 1.5), (8, r * 1.9), (-8, r * 2.3), (6, r * 2.8)], "#6B5A4A", 3)
    ell(ctx, 0, 0, r * 0.92, r * 1.15, c)
    ell(ctx, -r * 0.35, -r * 0.45, r * 0.18, r * 0.3, "#ffffff", 0.35, rot=0.5)
    if label:
        text(ctx, label, 0, 0, size, lc)
    ctx.restore()


def seal(ctx, x, y, r, c="#B8352B", txt="✓", size=80, rot=0.0, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    pts = []
    n = 24
    for i in range(n * 2):
        rr = r if i % 2 == 0 else r * 0.88
        ang = i * math.pi / n
        pts.append((rr * math.cos(ang), rr * math.sin(ang)))
    poly(ctx, pts, c, a)
    circ(ctx, 0, 0, r * 0.72, None, 1, "#FFF3D0", r * 0.04)
    if txt:
        text(ctx, txt, 0, 0, size, "#FFF3D0", a=a)
    ctx.restore()


def checkmark(ctx, x, y, s, c="#3E8E41", p=1.0, lw=14):
    pts = [(x - s * 0.5, y), (x - s * 0.12, y + s * 0.4), (x + s * 0.55, y - s * 0.45)]
    if p < 0.5:
        q = p / 0.5
        pts = [pts[0], (lerp(pts[0][0], pts[1][0], q), lerp(pts[0][1], pts[1][1], q))]
    elif p < 1:
        q = (p - 0.5) / 0.5
        pts = [pts[0], pts[1], (lerp(pts[1][0], pts[2][0], q), lerp(pts[1][1], pts[2][1], q))]
    if p > 0:
        pline(ctx, pts, c, lw)


def cross(ctx, x, y, s, c="#C0392B", p=1.0, lw=16):
    if p <= 0:
        return
    q1 = clamp(p * 2)
    line(ctx, x - s, y - s, lerp(x - s, x + s, q1), lerp(y - s, y + s, q1), c, lw)
    if p > 0.5:
        q2 = clamp((p - 0.5) * 2)
        line(ctx, x + s, y - s, lerp(x + s, x - s, q2), lerp(y - s, y + s, q2), c, lw)


def sweat(ctx, x, y, t, c="#DDEBEE"):
    for i in range(2):
        yy = y + ((t * 80 + i * 40) % 80)
        a = 1 - ((t * 80 + i * 40) % 80) / 80
        poly(ctx, [(x + i * 30, yy - 18), (x + i * 30 - 9, yy), (x + i * 30 + 9, yy)], c, a)
        circ(ctx, x + i * 30, yy, 9, c, a)


def hand_pointer(ctx, x, y, rot=0.0):
    pass


def heart(ctx, x, y, r, c, a=1.0):
    circ(ctx, x - r * 0.5, y - r * 0.3, r * 0.6, c, a)
    circ(ctx, x + r * 0.5, y - r * 0.3, r * 0.6, c, a)
    poly(ctx, [(x - r * 1.05, y - r * 0.05), (x + r * 1.05, y - r * 0.05), (x, y + r * 1.15)], c, a)
