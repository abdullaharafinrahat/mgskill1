# -*- coding: utf-8 -*-
"""Shots: first day, rare phone, responsibility, Caples, takeaway, ending"""
import math, random
from shots2 import *

SHIRTS = ["#C9573F", "#E9B443", "#6FA35B", "#8D6A4E", "#D98BA0", "#F0E0BC"]
SKINS = [SKIN[0], SKIN[2], SKIN[1], SKIN[3], SKIN[0], SKIN[2]]


def shot_day1_arrive(ctx, s):
    t = s.t
    vgrad(ctx, "#E7C27D", "#F5E2B0")
    cx, cy, z = kf(t, [(0, 700, 960, 1.0), (s.dur, 560, 960, 1.1)])
    ctx.save()
    camera(ctx, cx, cy, z)
    rect(ctx, -1000, 1430, 4000, 700, "#9C7B58")
    rect(ctx, -1000, 1430, 4000, 24, "#C9A97E")
    building(ctx, 760, 560, 360, 880, "#B58F68", "#F3DDAA", 2, 6)
    shop_front(ctx, -90, 640, 640, 790, wall="#D9774E", glow=0.6, t=t)
    count = 0
    for i in range(6):
        t0 = 0.1 + i * 0.4
        stop = 640 + i * 70
        x = max(stop, 1300 - (t - t0) * 300) if t > t0 else 1400
        walking = x > stop
        if x <= 800 and t > t0:
            count = max(count, i + 1)
        person(ctx, x, 1470, 0.8, skin=SKINS[i], hair="#2A1B14", shirt=SHIRTS[i], pants="#4A3A32", arms=((16, 10), (16, 10)),
               walk=(t * 10 + i if walking else None), emo="happy", blink=blk(t, i), flip=1)
    ctx.restore()
    rect(ctx, 540 - 330, 250, 660, 230, "#2B1D14", 50)
    text(ctx, bn(count), 330, 365, 170, "#FFE08A", sc=1 + 0.15 * (1 if (t * 2.5) % 0.4 < 0.1 else 0))
    text(ctx, "জন কাস্টমার", 650, 365, 70, "#FFF3D0")


def shot_waiting(ctx, s):
    t = s.t
    interior(ctx, t, "#EAD7A8", "#8E6A47", "#D6B97A", 0, clock=False)
    cx, cy, z = kf(t, [(0, 540, 1200, 1.0), (s.c(41) - 0.3, 540, 1100, 1.0), (s.dur, 540, 760, 1.55)])
    ctx.save()
    camera(ctx, cx, cy, z)
    clock(ctx, 540, 520, 175, minutes=t * 3, sec=math.floor(t * 2) / 120.0)
    rect(ctx, 400, 720, 280, 70, "#2B1D14", 20)
    text(ctx, "৫০ মিনিট", 540, 755, 50, "#FFE08A")
    ups = 1.0 if t > s.c(41) else 0.0
    xs = [160, 420, 680, 940]
    for i, x in enumerate(xs):
        person(ctx, x, 1460, 0.85, skin=SKINS[i], hair="#2A1B14", shirt=SHIRTS[i], pants="#4A3A32", arms=((14, 10), (14, 10)),
               emo="n", blink=blk(t, i), look=0.0 if ups else sway(t, 0.8, 1, i), ly=-1.2 * ups, bob=sway(t, 2, 1.5, i),
               head_rot=-0.08 * ups * (1 if i < 2 else -1))
    # price bubble crossed
    if t < s.c(41) - 0.2:
        p = pop(t, s.c(40) + 0.1, 0.4)
        bubble(ctx, 400, 1000, "দাম কত?", 70, 420, 1130, p=p, maxw=360)
        cross(ctx, 400, 1000, 120, "#C0392B", prog(t, s.c(40) + 0.8, 0.4), 18) if p > 0 else None
    ctx.restore()


def shot_calendar_rare(ctx, s):
    t = s.t
    bg(ctx, "#6E7F45")
    for i in range(-2, 20):
        line(ctx, i * 130, 0, i * 130 + 600, 1920, "#788A4E", 36, cap=cairo.LINE_CAP_BUTT)
    c43 = s.c(43)
    cx, cy, z = kf(t, [(0, 540, 960, 1.0), (c43 - 0.1, 540, 900, 1.12), (s.dur, 700, 960, 1.15)])
    ctx.save()
    camera(ctx, cx, cy, z)
    slide = eio(prog(t, c43 - 0.3, 0.6))
    ctx.save()
    ctx.translate(0, -slide * 1500)
    rect(ctx, 250, 420, 580, 700, "#000000", 20, 0.2)
    rect(ctx, 230, 400, 580, 700, "#FFF4D6", 20)
    rect(ctx, 230, 400, 580, 130, "#B8352B", 20)
    rect(ctx, 230, 480, 580, 50, "#B8352B")
    text(ctx, "তৃতীয় সপ্তাহ", 520, 465, 70, "#FFF3D0")
    wk = min(int(t / 0.55), 2)
    for r_ in range(4):
        for c_ in range(7):
            n = r_ * 7 + c_ + 1
            x = 290 + c_ * 80
            y = 590 + r_ * 110
            if r_ <= wk:
                circ(ctx, x, y, 28, "#E9B443" if r_ == wk else "#D9C9A3")
            else:
                circ(ctx, x, y, 28, "#EFE3C3")
            if r_ == 2:
                circ(ctx, x, y, 28, None, 1, "#B8352B", 6) if t > 1.3 else None
    ctx.restore()
    # customer with rare phone
    q = eo3(prog(t, c43, 0.9))
    x = lerp(1400, 700, q)
    if q > 0:
        walking = q < 1
        person(ctx, x, 1440, 1.1, **CUST2, walk=(t * 9 if walking else None), flip=-1 if walking else 1,
               arms=((30, 130), (14, 10)), emo="happy", blink=blk(t), bob=0,
               propR=lambda c: (phone(c, 0, -60, 120, 220, "on", -0.1, body="#C9A24A", scr="#FFF2C0"),
                                sparkle(c, 50, -150, 26 + 8 * math.sin(t * 8), "#FFF8D8", 1, t)))
    if t > c43 + 1.0:
        p = pop(t, c43 + 1.0, 0.45)
        ctx.save()
        ctx.translate(560, 700)
        ctx.rotate(-0.08)
        ctx.scale(p, p)
        poly(ctx, [(-190, -60), (150, -60), (210, 0), (150, 60), (-190, 60)], "#F6EBD0", 1, "#2B1D14", 7)
        circ(ctx, -150, 0, 12, "#6E7F45")
        text(ctx, "বিরল মডেল", 0, 0, 62, "#7A1F17")
        ctx.restore()
    ctx.restore()


def shot_seventy(ctx, s):
    t = s.t
    bg(ctx, "#7A3B2E")
    rgrad(ctx, 540, 760, 800, "#B8583F", 0.8, 0)
    cx, cy, z = kf(t, [(0, 540, 960, 1.0), (s.dur, 540, 880, 1.2)])
    ctx.save()
    camera(ctx, cx, cy, z, sway(t, 0.01, 4) * clamp((t - 1.0) / 0.5))
    p = clamp(t / (s.dur - 0.5))
    mins = 70 * eio(p)
    over = mins > 50
    stopwatch(ctx, 540, 760, 300, frac=(mins / 60.0) % 1.0, body="#D6A84B" if not over else "#C0504A", ring="#B4832D" if not over else "#8F2E28",
              hand_c="#C0392B" if not over else "#FFF3D0")
    # 50 marker
    a = (50 / 60.0) * math.tau - math.pi / 2
    line(ctx, 540 + 230 * math.cos(a), 760 + 230 * math.sin(a), 540 + 330 * math.cos(a), 760 + 330 * math.sin(a), "#FFF3D0", 14)
    text(ctx, "৫০", 540 + 400 * math.cos(a), 760 + 380 * math.sin(a), 58, "#FFF3D0")
    rect(ctx, 540 - 300, 1190, 600, 230, "#2B1D14", 50)
    text(ctx, bn(int(mins)) + " মিনিট", 540, 1305, 130, "#FFE08A" if not over else "#FF8F7A")
    if over:
        sweat(ctx, 330, 560, t)
    ctx.restore()


def shot_give_half(ctx, s):
    t = s.t
    interior(ctx, t, "#E6C99B", "#946A44", "#CFA56E", 40)
    cx, cy, z = kf(t, [(0, 540, 960, 1.0), (s.dur, 540, 900, 1.2)])
    ctx.save()
    camera(ctx, cx, cy, z)
    gave = t > s.c(46) + 0.2
    zarms = ((75, 95), (12, 8)) if not gave else ((14, 10), (14, 10))
    zprop = None if gave else phone_prop(90, 170, "on", -0.1)
    person(ctx, 230, 1270, 1.0, **ZAHID_AP, arms=zarms, mouth=s.talk("zahid"), blink=blk(t), propR=zprop, emo="n" if not gave else "happy",
           look=0.7)
    draw_counter(ctx, w=640)
    cprop = phone_prop(90, 170, "on", -0.1) if gave else None
    person(ctx, 880, 1440, 1.0, **CUST2, arms=((14, 10), (28, 120) if gave else (14, 10)), blink=blk(t, 1), look=-0.6,
           propL=cprop)
    # bubbles
    if t < s.c(47):
        bubble(ctx, 400, 600, "ভাই, আমার কথা\nরাখতে পারিনি।", 54, 260, 900, p=pop(t, s.c(46), 0.35), maxw=520)
    else:
        bubble(ctx, 400, 600, "তাই শ্রমের চার্জ\nঅর্ধেক দিন।", 54, 260, 900, p=pop(t, s.c(47), 0.35), maxw=520)
        # receipt
        p = pop(t, s.c(47) + 0.5, 0.5)
        ctx.save()
        ctx.translate(600, 1010)
        ctx.rotate(0.05)
        ctx.scale(p, p)
        rect(ctx, -170, -130, 340, 260, "#FFF9EA", 8, sc="#8A7A62", lw=4)
        text(ctx, "শ্রমের চার্জ", 0, -85, 40, "#2B1D14")
        text(ctx, "৫০০", -60, -10, 70, "#8A7A62")
        line(ctx, -140, -10, 20, -10, "#C0392B", 8)
        text(ctx, "২৫০", 90, 70, 90, "#2F7A33")
        ctx.restore()
    ctx.restore()


def shot_surprised(ctx, s):
    t = s.t
    vgrad(ctx, "#D88F4B", "#E7B170")
    for i in range(16):
        a = i * math.tau / 16
        line(ctx, 540 + 300 * math.cos(a), 900 + 300 * math.sin(a), 540 + 1500 * math.cos(a), 900 + 1500 * math.sin(a), "#E0A262", 30, cap=cairo.LINE_CAP_BUTT)
    cx, cy, z = kf(t, [(0, 540, 1000, 1.0), (0.4, 540, 960, 1.18), (s.dur, 540, 920, 1.3)])
    ctx.save()
    camera(ctx, cx, cy, z)
    ctx.translate(*shake(t, 5 * clamp(1 - t * 2)))
    person(ctx, 540, 1500, 1.6, **CUST2, arms=((50, 130), (50, 130)), mouth=s.talk("cust"), emo="surprised", blink=blk(t, 1),
           bob=sway(t, 3, 2))
    for i, (x, y, r) in enumerate(((210, 640, -0.3), (860, 600, 0.3), (130, 960, -0.1))):
        text(ctx, "!", x, y, 200, "#7A1F17", sc=pop(t, 0.15 + i * 0.2, 0.4), rot=r)
    bubble(ctx, 540, 360, "আপনি নিজে থেকেই\nকমাচ্ছেন?", 62, 540, 650, p=pop(t, s.c(49), 0.35), maxw=700, fill="#FFF3D0")
    ctx.restore()


def shot_nod(ctx, s):
    t = s.t
    vgrad(ctx, "#C5CFA0", "#E6EAC6")
    z = lerp(1.0, 1.2, smooth(t / s.dur))
    ctx.save()
    camera(ctx, 540, 1000, z)
    nod = math.sin(t * 5) * 0.08 * (1 if t < 1.2 else 0.0)
    person(ctx, 540, 1480, 1.5, **ZAHID, arms=((12, 8), (12, 8)), emo="proud" if False else "happy", blink=blk(t), head_rot=nod,
           bob=sway(t, 2, 1.5), look=0.0)
    for i in range(6):
        a = t * 0.8 + i * 1.1
        sparkle(ctx, 540 + math.cos(i * 1.7) * 380, 760 + math.sin(i * 1.3) * 300, 22 + 8 * math.sin(a * 2), "#FFF3C4", 0.9, a)
    p = pop(t, 1.0, 0.5)
    checkmark(ctx, 880, 520, 130, "#3E8E41", prog(t, 1.0, 0.5), 26)
    ctx.restore()


def shot_brother(ctx, s):
    t = s.t
    vgrad(ctx, "#F0C75E", "#F8E5A8")
    cx, cy, z = kf(t, [(0, 300, 960, 1.0), (s.dur, 560, 960, 1.1)])
    ctx.save()
    camera(ctx, cx, cy, z)
    rect(ctx, -1000, 1430, 4000, 700, "#A88458")
    rect(ctx, -1000, 1430, 4000, 24, "#CFA97A")
    shop_front(ctx, 540, 600, 620, 830, wall="#D9774E", glow=0.5, t=t)
    person(ctx, 880, 1410, 0.95, **ZAHID_AP, arms=((150 + math.sin(t * 6) * 18, 175), (12, 8)), emo="happy", blink=blk(t), mouth=0)
    wx1 = lerp(-250, 380, eo3(prog(t, 0.0, s.dur - 0.5)))
    wx2 = lerp(-520, 150, eo3(prog(t, 0.0, s.dur - 0.5)))
    wk = prog(t, 0.0, s.dur - 0.5) < 1
    person(ctx, wx2, 1470, 0.95, skin=SKIN[3], hair="#1E1512", shirt="#8D6A4E", pants="#3A3A3A", walk=(t * 9 if wk else None),
           arms=((20, 14), (20, 14)), emo="happy", blink=blk(t, 1))
    person(ctx, wx1, 1470, 1.05, **CUST2, walk=(t * 9 + 1 if wk else None), arms=((20, 14), (20, 14)), emo="happy", blink=blk(t))
    ctx.restore()
    p = pop(t, 0.2, 0.5)
    rect(ctx, 540 - 270 * p, 200, 540 * p, 120, "#2B1D14", 36)
    text(ctx, "পরের সপ্তাহে", 540, 260, 66, "#FFE08A", sc=p)


# =================================================================== responsibility
def shot_slowly(ctx, s):
    t = s.t
    bg(ctx, "#EBD9A8")
    for i in range(-2, 22):
        line(ctx, i * 110, 1920, i * 110 + 400, 0, "#E2CE98", 30, cap=cairo.LINE_CAP_BUTT)
    cx, cy, z = kf(t, [(0, 540, 960, 1.0), (s.dur, 600, 900, 1.2)])
    ctx.save()
    camera(ctx, cx, cy, z)
    pts = []
    pg = prog(t, 0.2, 1.4)
    for i in range(0, 11):
        x = 140 + i * 80
        y = 1300 - i * 38 - 14 * math.sin(i * 1.3) - (i ** 2) * 2.4
        pts.append((x, y))
    n = int(len(pts) * pg)
    if n >= 2:
        pline(ctx, pts[:n], "#4E8A3B", 18)
    for i in range(n):
        circ(ctx, pts[i][0], pts[i][1], 14, "#F2B53A", 1, "#B58A2D", 4)
    person(ctx, 540, 1480, 1.3, **ZAHID, arms=((12, 8), (12, 8)), emo="think" if t < s.dur - 1 else "happy", blink=blk(t), look=0.6,
           bob=sway(t, 2, 1.5))
    bp = pop(t, s.dur - 1.3, 0.5)
    ctx.save()
    ctx.translate(540, 560)
    ctx.scale(bp, bp)
    bulb(ctx, 0, 0, 52, 1.0)
    ctx.restore()
    ctx.restore()


def shot_not_only_fast(ctx, s):
    t = s.t
    bg(ctx, "#E0C28A")
    for i in range(14):
        x = (i * 191 + t * (1400 + i * 40)) % (W + 700) - 300
        line(ctx, W - x, 160 + i * 125, W - x + 300, 160 + i * 125, "#C9A66B", 10)
    cx, cy, z = kf(t, [(0, 540, 960, 1.0), (s.dur, 540, 900, 1.15)])
    ctx.save()
    camera(ctx, cx, cy, z)
    text(ctx, "দ্রুত", 540, 720, 340, "#7A1F17", sc=pop(t, 0.0, 0.5), stroke=0, rot=-0.04)
    stopwatch(ctx, 540, 1130, 140, frac=(t * 2.5) % 1.0)
    cp = prog(t, s.c(53) + 1.0, 0.45)
    cross(ctx, 540, 740, 300, "#C0392B", cp, 40)
    p = pop(t, s.c(53) + 1.5, 0.45)
    rect(ctx, 540 - 300 * p, 1290, 600 * p, 110, "#2B1D14", 34)
    text(ctx, "যথেষ্ট নয়", 540, 1345, 70, "#FFE08A", sc=p)
    ctx.restore()


def shot_promise(ctx, s):
    t = s.t
    bg(ctx, "#3F5B34")
    rgrad(ctx, 540, 650, 800, "#6E8E50", 0.8, 0)
    cx, cy, z = kf(t, [(0, 540, 1000, 1.0), (s.dur, 540, 880, 1.25)])
    ctx.save()
    camera(ctx, cx, cy, z)
    p = pop(t, 0.1, 0.6)
    ctx.save()
    ctx.translate(540, 620)
    ctx.scale(p, p)
    poly(ctx, [(-120, 150), (-40, 150), (-70, 420), (-150, 330)][:3] + [(-170, 380)], "#B8352B")
    poly(ctx, [(120, 150), (40, 150), (70, 420), (150, 330)][:3] + [(170, 380)], "#B8352B")
    seal(ctx, 0, 0, 240, "#D9A441", "প্রতিশ্রুতি", 56, rot=sway(t, 0.04, 2))
    ctx.restore()
    person(ctx, 540, 1520, 1.2, **ZAHID, arms=((20, 10), (20, 10)), emo="happy", blink=blk(t), bob=sway(t, 2, 1.5)) if False else None
    person(ctx, 540, 1530, 1.15, **ZAHID, arms=((60, 20), (60, 20)), emo="happy", blink=blk(t), bob=sway(t, 2, 1.5))
    for i in range(8):
        a = t * 0.9 + i
        sparkle(ctx, 540 + math.cos(i * 0.8) * 420, 600 + math.sin(i * 1.7) * 300, 18 + 8 * math.sin(a * 2), "#FFF3C4", 0.9, a)
    ctx.restore()


# =================================================================== Caples
def shot_book(ctx, s):
    t = s.t
    bg(ctx, "#2F2420")
    rgrad(ctx, 540, 700, 1000, "#C28A3E", 0.65, 0)
    rect(ctx, -500, 1330, 3000, 800, "#6B4226")
    for i in range(6):
        line(ctx, -500, 1330 + i * 110, 2000, 1330 + i * 110, "#5A361C", 4)
    cx, cy, z = kf(t, [(0, 540, 1000, 0.95), (s.dur, 540, 840, 1.32)])
    ctx.save()
    camera(ctx, cx, cy, z)
    rot = sway(t, 0.03, 1.4)
    ctx.save()
    ctx.translate(540, 850 + sway(t, 10, 1.6))
    ctx.rotate(rot)
    pp = back(prog(t, 0.0, 0.7))
    ctx.scale(pp, pp)
    rect(ctx, -270 + 18, -380 + 22, 540, 760, "#000000", 14, 0.35)
    rect(ctx, -270, -380, 540, 760, "#8E2A25", 14)
    rect(ctx, -270, -380, 50, 760, "#6E1D19", 14)
    rect(ctx, -230, -340, 480, 680, None if False else "#8E2A25", 6, sc="#E2B04A", lw=6)
    text(ctx, "TESTED\nADVERTISING\nMETHODS", 10, -110, 70, "#F2C45A", fam="serif", lh=1.2)
    line(ctx, -150, 60, 170, 60, "#E2B04A", 5)
    text(ctx, "JOHN CAPLES", 10, 190, 52, "#F6EBD0", fam="serif")
    ctx.restore()
    p = pop(t, s.c(55) + 0.3, 0.5)
    rect(ctx, 540 - 300 * p, 270, 600 * p, 120, "#F6EBD0", 36)
    text(ctx, "জন ক্যাপলস", 540, 330, 76, "#5A1B16", sc=p)
    ctx.restore()


def shot_balloons(ctx, s):
    t = s.t
    vgrad(ctx, "#F2C9A0", "#F8E5C8")
    for i in range(6):
        cloud(ctx, (i * 380 + t * 24) % 1700 - 300, 260 + (i % 4) * 340, 1.5, "#FFF6EA", 0.8)
    c56 = s.c(56)
    cx, cy, z = kf(t, [(0, 540, 960, 1.0), (s.dur, 540, 880, 1.2)])
    ctx.save()
    camera(ctx, cx, cy, z)
    words = [("ভালো", "#C9573F", 250, 880, c56 + 1.6), ("সেরা", "#E9B443", 540, 620, c56 + 2.2), ("দ্রুত", "#4E9A3F", 830, 920, c56 + 2.8)]
    for w, col, x, y, tt in words:
        p = pop(t, tt - 0.2, 0.5)
        if p > 0:
            ctx.save()
            ctx.translate(x, y - (t - tt) * 14 + sway(t, 14, 1.5, x))
            ctx.scale(p, p)
            balloon(ctx, 0, 0, 125, col, w, 80, "#FFF8E8", t)
            ctx.restore()
    if t > c56 + 3.5:
        p = pop(t, c56 + 3.5, 0.5)
        rect(ctx, 540 - 330 * p, 1260, 660 * p, 140, "#2B1D14", 40)
        text(ctx, "শুধু দাবি", 540, 1330, 100, "#FFE08A", sc=p)
    ctx.restore()


def shot_solid(ctx, s):
    t = s.t
    vgrad(ctx, "#F4E3B3", "#FBF1D3")
    rect(ctx, -500, 1250, 3000, 800, "#C9A877")
    rect(ctx, -500, 1250, 3000, 20, "#A88858")
    cx, cy, z = kf(t, [(0, 540, 960, 1.0), (s.dur, 540, 1000, 1.2)])
    ctx.save()
    camera(ctx, cx, cy, z)
    for i in range(3):
        x = [250, 540, 830][i]
        y = 400 - (t * 160 + i * 200) % 1500 * 0 - t * 160 * (1 + i * 0.2)
        balloon(ctx, x, 600 + y, 80, ["#C9573F", "#E9B443", "#4E9A3F"][i], None, 40, "#fff", t)
    d = eo3(prog(t, 0.2, 0.5))
    by = lerp(-300, 1085, d if d < 1 else 1)
    if t > 0.7:
        by += 18 * math.sin(clamp((t - 0.7) * 4, 0, 1) * math.pi) * -1
    ctx.save()
    ctx.translate(620, by)
    rect(ctx, -340 + 14, -160 + 20, 680, 330, "#000000", 30, 0.25)
    rect(ctx, -340, -160, 680, 330, "#D9A441", 30, sc="#8A5A12", lw=10)
    rect(ctx, -310, -130, 620, 270, "#E8BA5B", 20)
    text(ctx, "৫০ মিনিট", 0, 0, 150, "#5A3A0B")
    ctx.restore()
    if t > 0.7:
        q = prog(t, 0.7, 0.8)
        for k in range(6):
            circ(ctx, 540 + (k - 2.5) * 140 * (0.5 + q), 1260 - 14 * q * (k % 2), 16 * (1 - q), "#C9A877", 1 - q)
    # customer
    person(ctx, 110, 1480, 0.9, **CUST1, arms=((12, 8), (12, 8)), emo="happy", blink=blk(t), look=0.8, bob=sway(t, 2, 1.5))
    checkmark(ctx, 880, 1000, 110, "#3E8E41", prog(t, s.c(57) + 1.5, 0.5), 24)
    ctx.restore()


# =================================================================== takeaway
def shot_takeaway(ctx, s):
    t = s.t
    bg(ctx, "#B88A56")
    noise_dots(ctx, 3, 400, "#9A7142", 0.7, 0, W, 0, H, 2, 6)
    noise_dots(ctx, 4, 250, "#D1A672", 0.6, 0, W, 0, H, 2, 5)
    cx, cy, z = kf(t, [(0, 540, 960, 1.0), (s.dur, 540, 880, 1.2)])
    ctx.save()
    camera(ctx, cx, cy, z, sway(t, 0.01, 1.2))
    p = back(prog(t, 0.1, 0.6))
    ctx.save()
    ctx.translate(540, 800)
    ctx.rotate(-0.06 + (1 - p) * 0.5)
    ctx.scale(p * 1.0, p * 1.0)
    rect(ctx, -360 + 16, -360 + 22, 720, 720, "#000000", 6, 0.25)
    rect(ctx, -360, -360, 720, 720, "#FFE680", 6)
    poly(ctx, [(360, 360), (360, 280), (280, 360)], "#E6CB5E")
    circ(ctx, 0, -350, 28, "#B8352B")
    circ(ctx, -8, -358, 8, "#E88F84")
    text(ctx, "Practical", 0, -120, 120, "#2B1D14", fam="serif")
    text(ctx, "Takeaway", 0, 60, 120, "#2B1D14", fam="serif")
    ul = prog(t, 0.9, 0.7)
    line(ctx, -270, 150, -270 + 540 * ul, 150 + math.sin(ul * 6) * 4, "#B8352B", 12)
    for i in range(3):
        sparkle(ctx, 250 + i * 40, 270 - i * 20, 26, "#F2B53A", 1, t + i)
    ctx.restore()
    ctx.restore()


def shot_ask_yourself(ctx, s):
    t = s.t
    bg(ctx, "#8FA67A")
    rgrad(ctx, 540, 800, 900, "#C6D4A8", 0.8, 0)
    cx, cy, z = kf(t, [(0, 540, 1000, 1.0), (s.dur, 540, 880, 1.28)])
    ctx.save()
    camera(ctx, cx, cy, z)
    rect(ctx, -400, 1250, 2000, 700, "#8A5A33")
    rect(ctx, -400, 1250, 2000, 30, "#B07A4A")
    wr = math.sin(t * 7) * 6
    person(ctx, 540, 1330, 1.35, skin=SKIN[2], hair="#22140F", shirt="#E9B443", pants="#4A3A32", hs="bun", arms=((60, 160), (60, 160)),
           emo="think", blink=blk(t), look=0.5, ly=1, bob=sway(t, 2, 1.5), head_rot=0.06 + sway(t, 0.02, 1.2))
    rect(ctx, 330, 1220, 420, 24, "#FFF4D6", 6)
    ctx.save()
    ctx.translate(540, 1300)
    rect(ctx, -520, -90, 1040, 40, "#8A5A33")
    ctx.restore()
    rect(ctx, 220, 1190, 330, 120, "#FFF4D6", 8, sc="#6B4226", lw=4)
    line(ctx, 250, 1230, 500, 1230, "#7A1F17", 5)
    line(ctx, 250, 1262, 440, 1262, "#7A1F17", 5)
    bp = pop(t, 0.5, 0.5)
    ctx.save()
    ctx.translate(540, 420)
    ctx.scale(bp, bp)
    circ(ctx, 0, 0, 170, "#FFFFFF", 1, "#2B1D14", 6)
    text(ctx, "?", 0, 6, 230, "#B8352B")
    ctx.restore()
    circ(ctx, 520, 640, 22 * bp, "#FFFFFF", 1, "#2B1D14", 4)
    circ(ctx, 500, 700, 13 * bp, "#FFFFFF", 1, "#2B1D14", 4)
    ctx.restore()


def shot_check_time(ctx, s):
    t = s.t
    bg(ctx, "#E9A23B")
    sunburst(ctx, 540, 800, "#E9A23B", "#EFB257", t, 20, speed=0.1)
    cx, cy, z = kf(t, [(0, 540, 960, 1.0), (s.dur, 540, 880, 1.1)])
    ctx.save()
    camera(ctx, cx, cy, z)
    stopwatch(ctx, 330, 800, 200, frac=(t * 0.18) % 1.0)
    ctx.save()
    ctx.translate(780, 840)
    ctx.scale(0.92, 0.92)
    ctx.rotate(0.06)
    pp = back(prog(t, 0.2, 0.5))
    ctx.scale(pp, pp)
    rect(ctx, -230 + 12, -330 + 16, 460, 660, "#000000", 10, 0.2)
    rect(ctx, -230, -330, 460, 660, "#FFF4D6", 10, sc="#6B4226", lw=6)
    text(ctx, "সাধারণ মডেলের\nস্ক্রিন বদলান\n৫০ মিনিটে", 0, -60, 52, "#7A1F17", maxw=400, fam="serif")
    line(ctx, -170, 130, 170, 130, "#8A7A62", 5)
    line(ctx, -170, 170, 100, 170, "#8A7A62", 5)
    ctx.restore()
    text(ctx, "?", 540, 420, 200, "#7A1F17", a=1 - prog(t, s.ce(60) - 1.2, 0.3), rot=sway(t, 0.1, 3))
    # arrow between
    pa = prog(t, 1.0, 0.6)
    pline(ctx, [(480, 1130), (540, 1190), (600, 1130)], "#2B1D14", 10, pa)
    checkmark(ctx, 790, 960, 220, "#2F7A33", prog(t, s.ce(60) - 1.2, 0.6), 36)
    ctx.restore()


# =================================================================== ending
def shot_clock_home(ctx, s):
    t = s.t
    interior(ctx, t, "#EBC98E", "#9C6B45", "#D9A867", 0, clock=False)
    rgrad(ctx, 700, 520, 800, "#FFE2A0", 0.55, 0)
    cx, cy, z = kf(t, [(0, 450, 960, 1.0), (s.dur, 660, 820, 1.4)])
    ctx.save()
    camera(ctx, cx, cy, z)
    clock(ctx, 700, 520, 150, minutes=125 + t * 0.5, sec=math.floor(t * 2) / 120.0)
    pw = prog(t, 0.0, 3.0)
    x = lerp(150, 620, eo3(pw))
    walking = pw < 1
    k = prog(t, s.c(62) + 0.6, 0.6)
    person(ctx, x, 1400, 1.1, **ZAHID_AP, walk=(t * 8 if walking else None), arms=((12, 8), (150 * k + 12, 170 * k + 8) if k > 0 else (12, 8)),
           emo="happy", blink=blk(t), look=0.8 * k, ly=-k, bob=abs(math.sin(t * 8)) * 4 if walking else sway(t, 2, 1.5),
           flip=1)
    ctx.restore()


def shot_claim(ctx, s):
    t = s.t
    bg(ctx, "#D9CDB5")
    for i in range(-2, 20):
        line(ctx, i * 120, 0, i * 120 - 300, 1920, "#D0C3A8", 28, cap=cairo.LINE_CAP_BUTT)
    cx, cy, z = kf(t, [(0, 540, 980, 1.0), (s.dur, 540, 880, 1.15)])
    ctx.save()
    camera(ctx, cx, cy, z)
    p = pop(t, 0.0, 0.7)
    ctx.save()
    ctx.translate(540, 700 + sway(t, 16, 1.5))
    ctx.rotate(sway(t, 0.07, 1.6))
    ctx.scale(p, p)
    balloon(ctx, 0, 0, 280, "#C9573F", "দ্রুত", 190, "#FFF8E8", t)
    ctx.restore()
    q = pop(t, s.c(63) + 1.0, 0.5)
    rect(ctx, 540 - 260 * q, 1220, 520 * q, 160, "#2B1D14", 44)
    text(ctx, "= দাবি", 540, 1300, 120, "#FFE08A", sc=q)
    ctx.restore()


def shot_promise_stamp(ctx, s):
    t = s.t
    bg(ctx, "#4F6B3B")
    confetti(ctx, t, ["#F2B53A", "#E9D9A0", "#C9573F"], 50, 8, size=18)
    rgrad(ctx, 540, 760, 800, "#7A9A5A", 0.8, 0)
    cx, cy, z = kf(t, [(0, 540, 980, 1.0), (s.dur, 540, 860, 1.22)])
    ctx.save()
    camera(ctx, cx, cy, z)
    q = prog(t, 0.0, 0.35)
    sc_ = lerp(2.4, 1.0, ei3(q)) if q < 1 else 1 + 0.03 * math.sin(t * 4)
    ox, oy = shake(t, 10 * clamp(1 - (t - 0.35) * 3)) if t > 0.35 else (0, 0)
    ctx.save()
    ctx.translate(540 + ox, 720 + oy)
    ctx.scale(sc_, sc_)
    ctx.rotate(-0.1)
    seal(ctx, 0, 0, 330, "#D9A441", None, 0)
    circ(ctx, 0, 0, 250, "#E8BA5B", 1, "#8A5A12", 8)
    text(ctx, "৫০\nমিনিট", 0, -10, 140, "#5A3A0B", lh=1.15)
    ctx.restore()
    checkmark(ctx, 800, 1050, 150, "#FFF3D0", prog(t, s.c(64) + 0.8, 0.5), 32)
    p = pop(t, s.c(64) + 0.9, 0.5)
    rect(ctx, 540 - 330 * p, 1220, 660 * p, 150, "#2B1D14", 44)
    text(ctx, "প্রতিশ্রুতি", 540, 1295, 110, "#FFE08A", sc=p)
    ctx.restore()


def shot_follow(ctx, s):
    t = s.t
    bg(ctx, "#E86F3C")
    sunburst(ctx, 540, 800, "#E86F3C", "#EE8355", t, 22, speed=0.12)
    confetti(ctx, t, ["#FFE08A", "#FFF3D0", "#7A1F17"], 50, 5, size=18)
    cx, cy, z = kf(t, [(0, 540, 960, 0.95), (s.dur, 540, 900, 1.12)])
    ctx.save()
    camera(ctx, cx, cy, z)
    pp = back(prog(t, 0.0, 0.7))
    ctx.save()
    ctx.translate(540, 780)
    ctx.scale(pp, pp)
    rect(ctx, -270 + 14, -480 + 20, 540, 960, "#000000", 60, 0.25)
    rect(ctx, -270, -480, 540, 960, "#2B2523", 60)
    rect(ctx, -245, -440, 490, 880, "#FFF9EA", 36)
    circ(ctx, 0, -300, 90, "#F2B53A")
    ctx.save()
    ctx.translate(0, -300)
    ctx.scale(0.6, 0.6)
    clock(ctx, 0, 0, 90, minutes=t * 20)
    ctx.restore()
    text(ctx, "practical গল্প", 0, -150, 52, "#2B1D14")
    for i, (a, b) in enumerate((("১০০", "পোস্ট"), ("৫০K", "ফলোয়ার"), ("১২", "ফলোইং"))):
        text(ctx, a, -150 + i * 150, -60, 44, "#2B1D14")
        text(ctx, b, -150 + i * 150, -10, 28, "#8A7A62", bold=False)
    fol = t > s.c(65) + 1.6
    col = "#4E9A3F" if fol else "#E86F3C"
    sb = 1 + 0.06 * math.sin(t * 6) if not fol else 1.0
    ctx.save()
    ctx.translate(0, 120)
    ctx.scale(sb, sb)
    rect(ctx, -190, -50, 380, 100, col, 30)
    text(ctx, "Following" if fol else "Follow", 0, 0, 56, "#FFF3D0")
    ctx.restore()
    for i in range(3):
        for j in range(3):
            rect(ctx, -215 + j * 148, 230 + i * 62, 138, 52, ["#F3D9A8", "#E9B987", "#D9A07A"][(i + j) % 3], 8)
    ctx.restore()
    if t > s.c(65) + 1.6:
        q = prog(t, s.c(65) + 1.6, 1.2)
        circ(ctx, 540, 900, 40 + q * 200, None, 1 - q, "#FFF3D0", 10) if False else None
        for i in range(8):
            qq = (q * 1.3 + i * 0.12) % 1.0
            heart(ctx, 540 + math.sin(i * 2) * 150, 900 - qq * 700, 30, "#C0392B", 1 - qq)
    ctx.restore()
    p = pop(t, 0.8, 0.5)
    text(ctx, "follow করুন", 540, 1330, 110, "#FFF3D0", sc=p, stroke=6, stroke_color="#7A1F17")
