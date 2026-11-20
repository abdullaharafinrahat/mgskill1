# -*- coding: utf-8 -*-
"""Shots 1-14 : hook, shop, ad, customers"""
import math, random
from chars import *

BNUM = "০১২৩৪৫৬৭৮৯"


def bn(n):
    return "".join(BNUM[int(c)] for c in str(int(n)))


ZAHID = dict(skin=SKIN[0], hair="#2A1B14", shirt="#C9573F", pants="#4A3A32", acc=("mustache",))
ZAHID_AP = dict(ZAHID, acc=("mustache", "apron"))
CUST1 = dict(skin=SKIN[1], hair="#1E1512", shirt="#6B7F3A", pants="#3A3A3A", acc=("glasses",))
CUST2 = dict(skin=SKIN[3], hair="#D8D2C6", shirt="#F4EDE0", pants="#6E5A48", hs="topi", acc=("beard", "kurta"))
GIRL = dict(skin=SKIN[2], hair="#22140F", shirt="#F2E6CF", pants="#7A3B2E", hs="pigtail", acc=("backpack", "tie"))


def blk(t, off=0.0):
    ph = (t + off) % 3.3
    return max(0.0, 1 - abs(ph - 0.08) / 0.08)


def sway(t, a=3, f=2.0, ph=0):
    return math.sin(t * f + ph) * a


def phone_prop(w=70, h=130, state="on", rot=-0.2):
    return lambda c: phone(c, 0, -h * 0.35, w, h, state, rot)


def interior(ctx, t, wall="#E8C99A", floor="#9C6B45", panel="#D4A870", clock_min=20.0, clock=True, dark=False, glowc=None):
    wall_interior(ctx, wall, floor, 1300, panel)
    shelf(ctx, -120, 640, 560, mix(panel, "#000000", 0.4), seed=4)
    shelf(ctx, -120, 820, 560, mix(panel, "#000000", 0.4), seed=9)
    poster(ctx, 560, 760, 140, 190, "#F6E8C8", tilt=-0.05)
    if clock:
        clock_(ctx, t, clock_min)
    if glowc:
        rgrad(ctx, 830, 520, 600, glowc, 0.35, 0)


def clock_(ctx, t, minutes, x=830, y=520, r=95, sec=True):
    clock(ctx, x, y, r, minutes=minutes, sec=(math.floor(t * 2) / 120.0 if sec else None))


def draw_counter(ctx, x=-120, w=720, y=1190):
    counter(ctx, x, y, w, 330)


# =================================================================== SHOT 1
def shot_hook_phone(ctx, s):
    t = s.t
    sunburst(ctx, 540, 820, "#F2B544", "#F7C766", t, 20)
    cx, cy, z = kf(t, [(0, 540, 960, 1.0), (s.dur, 540, 900, 1.22)])
    ctx.save()
    camera(ctx, cx, cy, z, math.sin(t * 0.8) * 0.01)
    swap = 1.7
    # old phone leaves, new phone enters
    if t < swap:
        shk = shake(t, 3 * smooth(t / swap)) if t > 1.1 else (0, 0)
        phone(ctx, 330 + shk[0], 860 + shk[1], 380, 740, "crack", rot=-0.06)
    else:
        p = back(prog(t, swap, 0.5))
        phone(ctx, 330, 860 + (1 - p) * 700, 380, 740, "on", rot=-0.06)
        if t < swap + 0.9:
            q = prog(t, swap, 0.9)
            for i in range(6):
                a = i * 1.05
                sparkle(ctx, 330 + math.cos(a) * 300 * q, 860 + math.sin(a) * 300 * q, 40 * (1 - q), "#FFF8D8", 1 - q)
        checkmark(ctx, 330, 860, 120, "#3E8E41", prog(t, swap + 0.4, 0.4), 22)
    # stopwatch
    ps = pop(t, 2.0, 0.5)
    if ps > 0:
        ctx.save()
        ctx.translate(790, 720)
        ctx.scale(ps, ps)
        stopwatch(ctx, 0, 0, 190, frac=(t - 2.0) * 0.28 % 1.0)
        ctx.restore()
    p2 = pop(t, 2.3, 0.45)
    if p2 > 0:
        rect(ctx, 150, 1090, 780, 200, "#2B1D14", 40, 1.0)
        text(ctx, "৫০ মিনিট", 540, 1190, 150, "#FFE08A", sc=p2)
    ctx.restore()


# =================================================================== SHOT 2
def shot_shop_glow(ctx, s):
    t = s.t
    vgrad(ctx, "#F6C177", "#F8E6B8")
    circ(ctx, 220, 560, 170, "#F28C38", 0.55)
    circ(ctx, 220, 560, 120, "#F7A94B", 0.8)
    cx, cy, z = kf(t, [(0, 400, 1250, 1.0), (s.dur, 560, 860, 1.3)])
    ctx.save()
    camera(ctx, cx, cy, z)
    rect(ctx, -1000, 1380, 4000, 800, "#B88A5A")
    rect(ctx, -1000, 1380, 4000, 30, "#D4A877")
    building(ctx, -150, 600, 260, 800, "#B9835A", "#F3DDAA", 2, 6)
    building(ctx, 870, 560, 300, 840, "#A97150", "#F3DDAA", 2, 6)
    shop_front(ctx, 190, 650, 700, 730, wall="#D9774E", glow=0.6 + 0.4 * math.sin(t * 3), t=t)
    for i in range(7):
        a = t * 1.5 + i * 0.9
        sparkle(ctx, 540 + math.cos(i * 1.3) * 380, 760 + math.sin(i * 2.1) * 130, 26 + 12 * math.sin(a * 2), "#FFF3C4",
                0.5 + 0.5 * math.sin(a * 2), a * 0.4)
    # coins pop out
    for i in range(6):
        t0 = s.c(1) + 1.2 + i * 0.35
        if t > t0:
            q = (t - t0)
            y = 1150 - q * 260
            a = clamp(1 - q / 1.8)
            circ(ctx, 330 + i * 70, y, 34, "#F2B53A", a, "#B58A2D", 5)
            text(ctx, "৳", 330 + i * 70, y, 38, "#7A5518", a)
    # rising arrow
    pa = prog(t, s.c(1) + 2.0, 1.0)
    if pa > 0:
        yb = 1350 - 520 * eo3(pa)
        poly(ctx, [(930, 1350), (990, 1350), (990, yb + 60), (1030, yb + 60), (960, yb - 40), (890, yb + 60), (930, yb + 60)],
             "#4E9A3F", 0.95)
    ctx.restore()


# =================================================================== SHOT 3
def shot_shutter_sad(ctx, s):
    t = s.t
    vgrad(ctx, "#3B2F2A", "#5B4A41")
    cx, cy, z = kf(t, [(0, 560, 980, 1.0), (s.dur, 420, 1020, 1.45)])
    ctx.save()
    camera(ctx, cx, cy, z)
    rect(ctx, -1000, 1420, 4000, 800, "#2D2420")
    rect(ctx, -1000, 1420, 4000, 20, "#4B3C34")
    building(ctx, -300, 600, 300, 830, "#4A3A33", "#6E5A4C", 2, 6, 0.6)
    sh = clamp(prog(t, s.c(2) + 3.3, 1.4) * 0.92 + 0.1)
    shop_front(ctx, 350, 700, 600, 720, wall="#6E4A3C", sign_bg="#2B2B24", shutter=sh, dark=True, awning="#8D6B3E",
               glow=0)
    # rent notice
    poster(ctx, 780, 1120, 190, 250, "#E8DCC0", "#5B4A3A", 0.06)
    tape(ctx, 780, 1000, 70, 24, 0.2)
    text(ctx, "ভাড়া\nবাকি", 780, 1090, 52, "#A42E24")
    for i in range(3):
        line(ctx, 700, 1160 + i * 28, 860, 1160 + i * 28, "#6B5A4A", 4)
    # zahid sad
    person(ctx, 250, 1430, 1.0, **ZAHID, arms=((8, 4), (8, 4)), emo="sad", head_rot=0.1 + sway(t, 0.03, 1.2), look=-0.5,
           ly=1, blink=blk(t), bob=sway(t, 2, 1.5))
    # thought: coin crossed
    p = pop(t, s.c(2) + 1.2, 0.5)
    if p > 0:
        ctx.save()
        ctx.translate(250, 780)
        ctx.scale(p, p)
        circ(ctx, 0, 0, 80, "#FFFFFF", 0.9, "#2B1D14", 5)
        circ(ctx, 0, 0, 40, "#F2B53A", 1, "#B58A2D", 4)
        text(ctx, "৳", 0, 0, 44, "#7A5518")
        cross(ctx, 0, 0, 50, "#C0392B", prog(t, s.c(2) + 1.8, 0.4), 12)
        ctx.restore()
    ctx.restore()
    rain(ctx, t, "#CFC3B4", 80)
    # label
    p = pop(t, 0.15, 0.5)
    rect(ctx, 540 - 230 * p, 190, 460 * p, 110, "#F3E6C4", 30)
    text(ctx, "এক বছর আগে", 540, 245, 62, "#3B2F2A", sc=p)


# =================================================================== SHOT 4
def shot_mirpur(ctx, s):
    t = s.t
    vgrad(ctx, "#F2A65A", "#F8DDA6", 0, 1500)
    circ(ctx, 800, 480, 130, "#F7C36B", 0.9)
    cx, cy, z = kf(t, [(0, 540, 960, 1.0), (1.3, 540, 960, 1.0), (s.dur, 560, 1260, 2.7)])
    ctx.save()
    camera(ctx, cx, cy, z)
    rnd = random.Random(7)
    for layer, (col, base, hmin, hmax) in enumerate([("#C79A6F", 1380, 400, 800), ("#A86F4A", 1400, 300, 640),
                                                      ("#7C4F34", 1420, 220, 460)]):
        x = -300
        while x < 1400:
            w = rnd.randint(110, 200)
            h = rnd.randint(hmin, hmax)
            if layer == 2 and 400 < x < 720:
                x += w
                continue
            building(ctx, x, base - h, w, h, col, "#F6E4B6" if layer < 2 else "#EBCB86", 2, max(2, h // 90), 0.8)
            x += w + 8
    rect(ctx, -1000, 1400, 4000, 700, "#8C6A4E")
    rect(ctx, -1000, 1400, 4000, 22, "#B08C69")
    # tiny shop
    shop_front(ctx, 440, 1230, 190, 175, wall="#D9774E", size=14, sign_txt="জাহিদ মোবাইল")
    # pin
    pin_a = 1 - clamp((t - 1.0) / 0.6)
    if pin_a > 0:
        yb = 880 + (1 - back(prog(t, 0.2, 0.6))) * -500 + sway(t, 8, 4)
        ctx.save()
        ctx.translate(540, yb)
        ctx.scale(1.2, 1.2)
        poly(ctx, [(-50, -20), (50, -20), (0, 100)], "#C0392B", pin_a)
        circ(ctx, 0, -40, 66, "#C0392B", pin_a)
        circ(ctx, 0, -40, 26, "#FFF3D0", pin_a)
        ctx.restore()
        text(ctx, "মিরপুর", 540, 660, 110, "#2B1D14", a=pin_a, stroke=6, stroke_color="#FFF3D0")
    ctx.restore()


# =================================================================== SHOT 5
def shot_father(ctx, s):
    t = s.t
    bg(ctx, "#A9B58A")
    for i in range(-10, 30):
        line(ctx, i * 90, 0, i * 90 - 300, 1920, "#9AA67B", 6, cap=cairo.LINE_CAP_BUTT)
    cx, cy, z = kf(t, [(0, 540, 940, 1.0), (s.dur, 540, 860, 1.28)])
    ctx.save()
    camera(ctx, cx, cy, z, math.sin(t * 0.7) * 0.012)
    rgrad(ctx, 540, 760, 640, "#FFF3C9", 0.5, 0)
    # frame
    rect(ctx, 250 + 12, 430 + 16, 560, 700, "#000000", 14, 0.2)
    rect(ctx, 250, 430, 560, 700, "#6B4226", 14)
    rect(ctx, 276, 456, 508, 648, "#F3E6C4", 6)
    ctx.save()
    rect(ctx, 306, 486, 448, 588, "#D8C79E")
    ctx.rectangle(306, 486, 448, 588)
    ctx.clip()
    person(ctx, 530, 1300, 1.55, **CUST2, arms=((10, 6), (10, 6)), emo="n", look=0, blink=blk(t))
    ctx.restore()
    # black ribbon
    poly(ctx, [(250, 430), (360, 430), (250, 540)], "#1F1A18")
    # key on nail
    circ(ctx, 880, 1180, 10, "#444")
    kx, ky = 880, 1180
    ctx.save()
    ctx.translate(kx, ky)
    ctx.rotate(sway(t, 0.12, 2.2))
    line(ctx, 0, 0, 0, 90, "#6B5A4A", 4)
    rect(ctx, -34, 90, 68, 40, "#D6A84B", 8)
    circ(ctx, 0, 110, 30, None, 1, "#D6A84B", 14)
    rect(ctx, -9, 130, 18, 130, "#D6A84B", 4)
    rect(ctx, 9, 215, 34, 14, "#D6A84B", 3)
    rect(ctx, 9, 240, 24, 14, "#D6A84B", 3)
    rect(ctx, -52, 110, 104, 54, "#F3E6C4", 8, sc="#6B4226", lw=4) if False else None
    ctx.restore()
    p = pop(t, s.c(4) + 0.9, 0.5)
    for i in range(5):
        a = t * 2 + i * 1.3
        sparkle(ctx, 540 + math.cos(i * 1.8) * 360, 780 + math.sin(i * 1.3) * 380, 22 * p, "#FFF8D8", 0.5 + 0.5 * math.sin(a), a * 0.3)
    ctx.restore()


# =================================================================== SHOT 6
def shot_wallclock(ctx, s):
    t = s.t
    bg(ctx, "#E3D2AE")
    rnd = random.Random(5)
    for i in range(14):
        ell(ctx, rnd.uniform(0, W), rnd.uniform(0, H), rnd.uniform(60, 160), rnd.uniform(30, 90), "#D2BE94", 0.5, rnd.uniform(0, 3))
    cx, cy, z = kf(t, [(0, 540, 980, 0.9), (s.dur, 540, 800, 1.35)])
    ctx.save()
    camera(ctx, cx, cy, z, sway(t, 0.012, 3))
    # nail & dust
    clock(ctx, 540, 800, 330, minutes=40 + t * 4, sec=math.floor(t * 3) / 18.0, shake_=(0.012 if int(t * 3) != int(t * 3 - 0.1) else 0))
    # cobweb
    for k in range(5):
        a = k * math.pi / 8
        line(ctx, -40, -40, -40 + 420 * math.cos(a), -40 + 420 * math.sin(a), "#B9AA8A", 2)
    for r_ in (110, 200, 300):
        arc_stroke(ctx, -40, -40, r_, 0, math.pi / 2, "#B9AA8A", 2)
    for i in range(24):
        x = (i * 173 + t * 14) % W
        y = (i * 311 + math.sin(t + i) * 30 + t * 8) % 1500 + 200
        circ(ctx, x, y, 3 + (i % 3), "#FFF8E0", 0.8)
    ctx.restore()
    text(ctx, "পুরনো ঘড়ি", 540, 1330, 80, "#6B4226", a=prog(t, 0.2, 0.5), serif=None) if False else None
    p = pop(t, 0.3, 0.5)
    if p > 0:
        rect(ctx, 540 - 230 * p, 1230, 460 * p, 110, "#6B4226", 30)
        text(ctx, "পুরনো ঘড়ি", 540, 1285, 64, "#F6EBD3", sc=p)


# =================================================================== SHOT 7
def shot_tried_all(ctx, s):
    t = s.t
    bg(ctx, "#D9694E")
    for i in range(-3, 14):
        for j in range(-1, 20):
            circ(ctx, i * 100 + (j % 2) * 50, j * 100, 6, "#E58A70", 0.7)
    z = lerp(1.0, 1.12, smooth(t / s.dur))
    ctx.save()
    camera(ctx, 540, 960, z, sway(t, 0.015, 1.2))
    c6 = s.c(6)
    # icons around Zahid
    def card(x, y, tt, rot, draw):
        p = pop(t, tt, 0.45)
        if p <= 0:
            return
        ctx.save()
        ctx.translate(x, y + sway(t, 8, 2, x))
        ctx.rotate(rot)
        ctx.scale(p, p)
        draw(ctx)
        ctx.restore()

    def d_tag(c):
        poly(c, [(-130, -50), (60, -50), (140, 0), (60, 50), (-130, 50)], "#F6EBD0", 1, "#2B1D14", 6)
        circ(c, -100, 0, 10, "#D9694E")
        text(c, "২০% ছাড়", -10, 0, 44, "#B8352B")

    def d_fly(c):
        for k in range(3):
            rect(c, -80 + k * 10, -110 + k * 10, 160, 210, "#F6EBD0", 8, sc="#2B1D14", lw=5)
        for k in range(4):
            line(c, -50, -50 + k * 30, 50, -50 + k * 30, "#8A7A62", 6)
        text(c, "লিফলেট", 0, 150, 40, "#FFF3D0")

    def d_mega(c):
        poly(c, [(-70, -30), (60, -90), (60, 90), (-70, 30)], "#F2B53A", 1, "#2B1D14", 6)
        rect(c, -110, -34, 50, 68, "#6B4226", 10)
        for k in range(3):
            arc_stroke(c, 70, 0, 40 + k * 28, -0.8, 0.8, "#FFF3D0", 7)
        text(c, "অফার!", 0, 140, 44, "#FFF3D0")

    def d_sign(c):
        rect(c, -140, -60, 280, 120, "#2F4F2A", 14, sc="#F3E6C4", lw=6)
        text(c, "নতুন সাইন", 0, 0, 46, "#FFF3C9")
        line(c, -90, 60, -90, 120, "#F3E6C4", 6)
        line(c, 90, 60, 90, 120, "#F3E6C4", 6)

    card(250, 560, c6 + 0.4, -0.15, d_tag)
    card(840, 640, c6 + 1.2, 0.12, d_fly)
    card(250, 1010, c6 + 2.0, 0.1, d_mega)
    card(830, 1060, c6 + 2.8, -0.1, d_sign)
    ws = t * 7
    person(ctx, 540, 1400, 1.25, **ZAHID_AP, arms=((70 + math.sin(ws) * 25, 140 + math.sin(ws + 1) * 20), (70 + math.cos(ws) * 25, 140 + math.cos(ws + 1) * 20)),
           emo="sad" if t > s.c(6) + 3.4 else "n", blink=blk(t), bob=abs(math.sin(ws)) * 6)
    sweat(ctx, 620, 880, t)
    ctx.restore()


# =================================================================== SHOT 8
def shot_never_measured(ctx, s):
    t = s.t
    vgrad(ctx, "#8A8F4A", "#6C7238")
    cx, cy, z = kf(t, [(0, 540, 920, 1.0), (s.dur, 540, 820, 1.18)])
    ctx.save()
    camera(ctx, cx, cy, z)
    tc = s.c(7) + 0.9
    sh = shake(t, 10 * clamp(1 - (t - tc) * 3)) if t > tc else (0, 0)
    ctx.translate(*sh)
    rgrad(ctx, 540, 800, 560, "#FFF3C9", 0.35, 0)
    stopwatch(ctx, 540, 680, 250, frac=0.0)
    cross(ctx, 540, 680, 190, "#C0392B", prog(t, tc, 0.4), 40)
    ctx.restore()
    wall = pop(t, 0.2, 0.4)
    person(ctx, 200, 1500, 0.8, **ZAHID, arms=((10, 4), (10, 4)), emo="n", look=-1 + sway(t, 0.3, 1), blink=blk(t), bob=sway(t, 2, 1.5), head_rot=-0.08)
    p = pop(t, tc + 0.3, 0.5)
    if p > 0:
        rect(ctx, 540 - 330 * p, 1010, 660 * p, 120, "#2B1D14", 36)
        text(ctx, "সময় মাপা হয়নি", 540, 1070, 66, "#FFE08A", sc=p)


# =================================================================== SHOT 9
def shot_ad_poster(ctx, s):
    t = s.t
    bg(ctx, "#F4B73F")
    for i in range(0, 14):
        poly(ctx, [(i * 160 - 200, 0), (i * 160 - 100, 0), (i * 160 + 400, 1920), (i * 160 + 300, 1920)], "#F7C763", 0.6)
    cx, cy, z = kf(t, [(0, 540, 1080, 1.0), (s.dur, 540, 800, 1.32)])
    ctx.save()
    camera(ctx, cx, cy, z, sway(t, 0.008, 1))
    dp = back(prog(t, 0.0, 0.7))
    yoff = (1 - dp) * -900
    poster(ctx, 540, 840 + yoff, 780, 960, "#FFF4D6", "#6B4226", 0.0)
    ctx.save()
    ctx.translate(0, yoff)
    for (x, y, r) in ((170, 400, -0.5), (910, 400, 0.5), (170, 1280, 0.5), (910, 1280, -0.5)):
        tape(ctx, x, y, 110, 34, r)
    # lightning
    poly(ctx, [(520, 470), (400, 700), (500, 700), (450, 900), (640, 640), (540, 640), (610, 470)], "#F2B53A", 1, "#B58A2D", 6)
    rect(ctx, 220, 440, 120, 22, "#C0392B", 8)
    msg = "দ্রুত ও নির্ভরযোগ্য\nমোবাইল সার্ভিস"
    full = typewriter(msg, prog(t, s.c(8) + 0.5, 2.3))
    if full:
        text(ctx, full, 540, 1090, 84, "#7A1F17", maxw=700, fam="serif", lh=1.3)
    ctx.restore()
    ctx.restore()


# =================================================================== SHOT 10
def shot_how_fast(ctx, s):
    t = s.t
    bg(ctx, "#3A2E29")
    for i in range(12):
        x = (i * 211 - t * (900 + i * 30)) % (W + 600) - 300
        line(ctx, x, 200 + i * 130, x + 260, 200 + i * 130, "#5A4A41", 8)
    z = lerp(1.0, 1.22, smooth(t / s.dur))
    ctx.save()
    camera(ctx, 540, 900, z, sway(t, 0.02, 2))
    for (x, y, sz, r) in ((180, 420, 260, -0.3), (900, 560, 220, 0.25), (260, 1260, 200, 0.2), (860, 1200, 280, -0.2)):
        p = pop(t, 0.3 + (x % 5) * 0.12, 0.5)
        text(ctx, "?", x, y + sway(t, 14, 2, x), sz, "#F6EBD3", a=0.9, sc=p, rot=r + sway(t, 0.08, 3, y))
    sc_ = 1 + 0.04 * math.sin(t * 6)
    text(ctx, "দ্রুত", 540, 700, 300, "#F2B53A", sc=sc_ * pop(t, 0.0, 0.5), rot=sway(t, 0.04, 3), stroke=8, stroke_color="#8A5A12")
    p = pop(t, s.c(9) + 0.9, 0.5)
    text(ctx, "কত দ্রুত?", 540, 1010, 150, "#FFF3D0", sc=p)
    stopwatch(ctx, 540, 1340, 100, frac=(t * 0.7) % 1.0)
    ctx.restore()


# =================================================================== customers
def _interior_cust(ctx, t, wall, floor, panel, cmin):
    interior(ctx, t, wall, floor, panel, cmin)


def shot_cust_ask(ctx, s):
    t = s.t
    _interior_cust(ctx, t, "#E8C99A", "#9C6B45", "#D4A870", 20)
    cx, cy, z = kf(t, [(0, 540, 960, 1.0), (s.c(11) - 0.2, 600, 960, 1.05), (s.dur, 700, 900, 1.28)])
    ctx.save()
    camera(ctx, cx, cy, z)
    person(ctx, 300, 1270, 1.0, **ZAHID_AP, arms=((12, 8), (12, 8)), blink=blk(t), bob=sway(t, 2, 1.6))
    draw_counter(ctx)
    wx = lerp(1350, 800, eo3(prog(t, 0.0, 1.8)))
    walking = prog(t, 0.0, 1.8) < 1
    person(ctx, wx, 1440, 1.0, **CUST1, walk=(t * 9 if walking else None), arms=((20, 110), (14, 10)),
           mouth=s.talk("cust"), blink=blk(t, 1), propR=phone_prop(80, 150, "crack", -0.15), flip=-1 if walking else 1)
    ctx.restore()
    ctx.save()
    camera(ctx, cx, cy, z)
    bubble(ctx, 720, 730, "ভাই, কতক্ষণ\nলাগবে?", 58, 790, 1000, p=pop(t, s.c(11), 0.35), maxw=420)
    ctx.restore()


def shot_zahid_hoye(ctx, s):
    t = s.t
    _interior_cust(ctx, t, "#E7B65A", "#8E5E3C", "#C99A55", 20)
    cx, cy, z = kf(t, [(0, 480, 1000, 1.1), (s.dur, 330, 960, 1.55)])
    ctx.save()
    camera(ctx, cx, cy, z)
    g = s.talk("zahid")
    sh = 1 if t > s.c(13) else 0
    person(ctx, 300, 1270, 1.0, **ZAHID_AP, arms=((70 + sh * 10, 150 - sh * 10), (70 + sh * 10, 150 - sh * 10)), mouth=g,
           emo="n", blink=blk(t), look=0.6)
    draw_counter(ctx)
    person(ctx, 850, 1440, 1.0, **CUST1, arms=((14, 10), (14, 10)), blink=blk(t, 2), look=-0.6, propR=phone_prop(80, 150, "crack", -0.15))
    bubble(ctx, 480, 720, "হয়ে যাবে।", 70, 340, 920, p=pop(t, s.c(13), 0.35), maxw=520, fill="#FFF3D0")
    sweat(ctx, 390, 900, t) if t > s.c(13) + 0.3 else None
    ctx.restore()


def shot_kokhon(ctx, s):
    t = s.t
    vgrad(ctx, "#D79B8C", "#B97B6E")
    for i in range(10):
        circ(ctx, (i * 211) % W, (i * 331) % H, 160 + i * 6, "#C98B7D", 0.5)
    cx, cy, z = kf(t, [(0, 540, 1000, 1.0), (s.dur, 540, 900, 1.2)])
    ctx.save()
    camera(ctx, cx, cy, z)
    up = 1 if t < s.c(15) else 0
    person(ctx, 540, 1500, 1.5, **CUST1, arms=((30, 110) if up else (14, 10), (14, 10)), mouth=s.talk("cust"),
           emo="angry" if t > s.c(15) else "n", blink=blk(t), propR=phone_prop(110, 210, "crack", -0.15),
           bob=sway(t, 3, 2), head_rot=sway(t, 0.03, 2))
    bubble(ctx, 540, 400, "কখন?", 120, 540, 740, p=pop(t, s.c(15), 0.35), maxw=520, fill="#FFF3D0")
    pq = pop(t, s.c(14) + 0.6, 0.4)
    text(ctx, "?", 160, 800, 200, "#FFF3D0", a=0.8, sc=pq, rot=-0.2)
    text(ctx, "?", 920, 700, 160, "#FFF3D0", a=0.8, sc=pq, rot=0.2)
    ctx.restore()


def shot_shrug(ctx, s):
    t = s.t
    bg(ctx, "#CBB38A")
    for i in range(0, 18):
        rect(ctx, i * 120 - 60, 0, 60, 1920, "#C2A97F", 0)
        rect(ctx, i * 120 - 60, 0, 60, 1920, "#C2A97F", 0.0, 0.6)
    z = lerp(1.0, 1.22, smooth(t / s.dur))
    ctx.save()
    camera(ctx, 540, 1000, z, sway(t, 0.012, 2))
    sw = math.sin(t * 3) * 6
    person(ctx, 540, 1480, 1.3, **ZAHID, arms=((72 + sw, 140), (72 - sw, 140)), emo="sad", blink=blk(t), bob=sway(t, 3, 3),
           look=sway(t, 0.8, 1.5))
    for i, (x, y, sz) in enumerate(((300, 560, 220), (780, 480, 260), (540, 330, 170))):
        p = pop(t, 0.2 + i * 0.35, 0.45)
        text(ctx, "?", x, y + sway(t, 12, 2.4, i), sz, "#7A1F17", sc=p, rot=sway(t, 0.12, 2.5, i))
    sweat(ctx, 700, 1000, t)
    ctx.restore()


def shot_street(ctx, s):
    t = s.t
    vgrad(ctx, "#F0D9A8", "#F8EBCC", 0, 1300)
    p = prog(t, 0.2, s.dur - 0.4)
    camx = lerp(540, 1560, smooth(p))
    ctx.save()
    camera(ctx, camx, 960, 1.0)
    rect(ctx, -600, 1330, 3600, 600, "#8F7F6C")
    rect(ctx, -600, 1330, 3600, 36, "#BBA98F")
    for i in range(-5, 30):
        rect(ctx, i * 200, 1650, 110, 16, "#E7D8B8", 6)
    building(ctx, -500, 520, 360, 820, "#B58F68", "#F3DDAA", 2, 6)
    shop_front(ctx, 60, 880, 470, 450, wall="#B96A47", sign_bg="#3B2F1F", size=34, sign_txt="জাহিদ মোবাইল")
    # big shop
    rect(ctx, 1220, 420, 1000, 930, "#E5E1D6")
    rect(ctx, 1240, 480, 960, 180, "#C0272D", 12, sc="#FFD23F", lw=8)
    text(ctx, "মেগা মোবাইল হাব", 1720, 570, 96, "#FFE9A0")
    for i in range(14):
        circ(ctx, 1260 + i * 70, 690 + math.sin(i + t * 4) * 3, 10, "#FFD23F" if (i + int(t * 4)) % 2 else "#FFF3C0")
    rect(ctx, 1260, 740, 920, 600, "#2B2724")
    rect(ctx, 1280, 760, 880, 580, "#FFF3D6")
    for k in range(4):
        rect(ctx, 1320 + k * 210, 800, 170, 220, "#D6C9A8", 10)
        phone(ctx, 1405 + k * 210, 910, 80, 160, "on")
    sk = [SKIN[0], SKIN[2], SKIN[1]]
    for i in range(3):
        person(ctx, 1500 + i * 190, 1360, 0.78, skin=sk[i], hair="#2A1B14", shirt=["#C9573F", "#E9B443", "#6FA35B"][i], pants="#4A3A32",
               arms=((12, 8), (12, 8)), emo="happy", blink=blk(t, i), bob=sway(t, 2, 2, i))
    wx = lerp(560, 1280, smooth(prog(t, 0.0, s.dur - 0.6)))
    person(ctx, wx, 1450, 1.0, **CUST1, walk=t * 9, arms=((24, 100), (24, 14)), propR=phone_prop(70, 130, "crack"),
           emo="n", flip=1)
    ctx.restore()
