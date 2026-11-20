# -*- coding: utf-8 -*-
"""Shots: schoolgirl, realisation, night experiment, new ad"""
import math, random
from shots1 import *


# =================================================================== girl arrives
def shot_girl_arrive(ctx, s):
    t = s.t
    vgrad(ctx, "#F2C4B0", "#F8E0CC")
    for i in range(8):
        cloud(ctx, (i * 330 + t * 20) % 1500 - 200, 280 + (i % 3) * 120, 1.2, "#FFF4EA", 0.8)
    cx, cy, z = kf(t, [(0, 380, 980, 1.0), (s.c(19), 540, 980, 1.1), (s.dur, 560, 900, 1.25)])
    ctx.save()
    camera(ctx, cx, cy, z)
    rect(ctx, -1000, 1450, 4000, 600, "#B07A57")
    rect(ctx, -1000, 1450, 4000, 20, "#CFA27C")
    for k in range(-3, 12):
        building(ctx, k * 260 - 100, 1450 - 380 - (k % 3) * 60, 240, 380 + (k % 3) * 60, ["#D9A582", "#C48A68", "#E4B898"][k % 3], "#FFF1D2", 2, 4, 0.8)
    pw = prog(t, 0.0, 2.2)
    gx = lerp(-250, 540, eo3(pw))
    walking = pw < 1
    holding = t > s.c(19) - 0.5
    pr = phone_prop(100, 190, "crack", -0.1) if holding else None
    person(ctx, gx, 1520, 1.3, **GIRL, walk=(t * 10 if walking else None), arms=((20, 10) if not holding else (35, 120), (14, 10)),
           emo="sad" if t > s.c(19) else "happy", blink=blk(t), bob=abs(math.sin(t * 10)) * 5 if walking else sway(t, 2, 1.6),
           propR=pr, look=0.4)
    # books in left hand
    if not holding:
        pass
    ctx.restore()
    # exam card
    p = pop(t, s.c(18) + 1.5, 0.5)
    if p > 0:
        ctx.save()
        ctx.translate(800, 380)
        ctx.rotate(0.08)
        ctx.scale(p, p)
        rect(ctx, -230, -130, 460, 260, "#FFF4D6", 16, sc="#B8352B", lw=8)
        rect(ctx, -230, -130, 460, 70, "#B8352B", 16)
        text(ctx, "পরীক্ষা কাল!", 0, -95, 52, "#FFF3D0")
        for k in range(3):
            line(ctx, -170, -20 + k * 40, 170, -20 + k * 40, "#B9A98A", 6)
        ctx.restore()
    # floating study pages
    if t > s.c(19):
        for i in range(5):
            q = ((t - s.c(19)) * 0.5 + i * 0.2) % 1.0
            x = 540 + math.sin(q * 6 + i) * 130 + (i - 2) * 60
            y = 800 - q * 450
            ctx.save()
            ctx.translate(x, y)
            ctx.rotate(math.sin(q * 5 + i) * 0.5)
            rect(ctx, -34, -44, 68, 88, "#FFF9E8", 6, 1 - q, "#8A7A62", 3)
            line(ctx, -20, -20, 20, -20, "#8A7A62", 4, 1 - q)
            line(ctx, -20, 0, 20, 0, "#8A7A62", 4, 1 - q)
            ctx.restore()
        pp = pop(t, s.c(19) + 0.2, 0.4)
        text(ctx, "সব পড়া ফোনে!", 540, 1260, 70, "#7A1F17", sc=pp, stroke=0) if False else None
        rect(ctx, 540 - 300 * pp, 600, 600 * pp, 100, "#7A1F17", 30)
        text(ctx, "সব পড়া ফোনে", 540, 650, 60, "#FFF3D0", sc=pp)


def shot_girl_ask(ctx, s):
    t = s.t
    interior(ctx, t, "#C98A5B", "#7C4A32", "#B4703F", 120)
    rgrad(ctx, 540, 300, 900, "#FFE2A0", 0.4, 0)
    cx, cy, z = kf(t, [(0, 540, 960, 1.0), (s.dur, 700, 930, 1.32)])
    ctx.save()
    camera(ctx, cx, cy, z)
    person(ctx, 280, 1270, 1.0, **ZAHID_AP, arms=((12, 8), (12, 8)), blink=blk(t), bob=sway(t, 2, 1.6), look=0.7)
    draw_counter(ctx)
    person(ctx, 800, 1440, 1.05, **GIRL, arms=((30, 125), (14, 10)), mouth=s.talk("girl"), emo="sad", blink=blk(t, 1),
           propR=phone_prop(90, 170, "crack", -0.1), look=-0.5)
    bubble(ctx, 740, 640, "ভাইয়া, আজ রাতের\nমধ্যে পাব?", 54, 800, 940, p=pop(t, s.c(21), 0.35), maxw=520)
    ctx.restore()


def shot_zahid_reply(ctx, s):
    t = s.t
    interior(ctx, t, "#C98A5B", "#7C4A32", "#B4703F", 120)
    rgrad(ctx, 540, 300, 900, "#FFE2A0", 0.4, 0)
    cx, cy, z = kf(t, [(0, 700, 940, 1.2), (s.dur, 330, 960, 1.55)])
    ctx.save()
    camera(ctx, cx, cy, z)
    person(ctx, 300, 1270, 1.0, **ZAHID_AP, arms=((60, 140), (60, 140)), mouth=s.talk("zahid"), blink=blk(t), look=0.7)
    draw_counter(ctx)
    person(ctx, 850, 1440, 1.05, **GIRL, arms=((30, 125), (14, 10)), emo="sad", blink=blk(t, 1), propR=phone_prop(90, 170, "crack", -0.1), look=-0.5)
    bubble(ctx, 470, 700, "হয়ে যাবে।", 70, 330, 920, p=pop(t, s.c(23), 0.35), maxw=520, fill="#FFF3D0")
    ctx.restore()


def _choice_card(ctx, x, y, p, label, kind, glow):
    if p <= 0:
        return
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(p * 0.78, p * 0.78)
    rect(ctx, -170, -190, 340, 380, "#FFF4D6", 30, sc="#FFD36B" if glow else "#2B1D14", lw=10 if glow else 6)
    if kind == "wait":
        chair(ctx, 0, 40, "#8E4B32")
        clock(ctx, 0, -80, 50, minutes=30)
    else:
        shop_front(ctx, -100, -150, 200, 200, wall="#4F8F55" if False else "#C96F4A", size=18, sign_txt="অন্য দোকান")
    text(ctx, label, 0, 130, 50, "#2B1D14", maxw=300)
    ctx.restore()


def shot_girl_choice(ctx, s):
    t = s.t
    bg(ctx, "#5A2E2A")
    rgrad(ctx, 540, 900, 900, "#9B5A3C", 0.9, 0)
    cx, cy, z = kf(t, [(0, 540, 1000, 1.0), (s.dur, 540, 900, 1.18)])
    ctx.save()
    camera(ctx, cx, cy, z)
    quiet = t < s.c(25)
    person(ctx, 540, 1480, 1.5, **GIRL, arms=((30, 125), (14, 10)), mouth=s.talk("girl"), emo="sad" if quiet else "n", blink=blk(t),
           propR=phone_prop(110, 200, "crack", -0.1), head_rot=0.12 if quiet else sway(t, 0.03, 2), ly=1 if quiet else 0,
           look=0 if quiet else sway(t, 0.8, 1.2))
    if quiet:
        p = pop(t, s.c(24) + 1.2, 0.4)
        bubble(ctx, 740, 600, "...", 100, 640, 900, p=p, maxw=300)
    elif t < s.c(26):
        bubble(ctx, 540, 400, "হয়ে যাবে মানে কখন?", 66, 540, 730, p=pop(t, s.c(25), 0.35), maxw=700, fill="#FFF3D0")
    else:
        bubble(ctx, 540, 390, "আমি অপেক্ষা করব,\nনাকি অন্য দোকানে যাব?", 58, 540, 720, p=pop(t, s.c(26), 0.35), maxw=760, fill="#FFF3D0")
        g = int((t - s.c(26)) * 1.4) % 2
        _choice_card(ctx, 225, 1170, pop(t, s.c(26) + 0.5, 0.45), "অপেক্ষা", "wait", g == 0)
        _choice_card(ctx, 855, 1170, pop(t, s.c(26) + 1.1, 0.45), "অন্য দোকান", "shop", g == 1)
    ctx.restore()


# =================================================================== realisation
def shot_think(ctx, s):
    t = s.t
    bg(ctx, "#B7A06A")
    rgrad(ctx, 540, 900, 900, "#E8D9A6", 0.9, 0)
    z = lerp(1.0, 1.6, smooth(t / s.dur))
    ctx.save()
    camera(ctx, 540, lerp(1050, 880, smooth(t / s.dur)), z)
    person(ctx, 540, 1500, 1.4, **ZAHID, arms=((120, 250), (8, 4)), emo="think", blink=blk(t), look=-0.6, ly=-1,
           head_rot=sway(t, 0.03, 1.2), front_r=True, bob=sway(t, 2, 1.5))
    # echo bubble
    if t < s.c(28):
        bubble(ctx, 300, 480, "হয়ে যাবে মানে কখন?", 44, 420, 700, p=pop(t, 0.3, 0.4) * 0.9, maxw=420, fill="#F3E6C4")
    else:
        bp = pop(t, s.c(28) + 0.5, 0.5)
        ctx.save()
        ctx.translate(540, 480)
        ctx.scale(bp, bp)
        bulb(ctx, 0, 0, 52, 1.0)
        ctx.restore()
        for i in range(6):
            sparkle(ctx, 540 + math.cos(i + t) * 160 * bp, 480 + math.sin(i * 2 + t) * 120 * bp, 18 * bp, "#FFF8D8", 0.8, t)
    ctx.restore()


def gear(ctx, x, y, r, c, rot=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    for i in range(10):
        ctx.save()
        ctx.rotate(i * math.tau / 10)
        rect(ctx, -r * 0.14, -r * 1.2, r * 0.28, r * 0.4, c, r * 0.05)
        ctx.restore()
    circ(ctx, 0, 0, r, c)
    circ(ctx, 0, 0, r * 0.4, "#00000000" if False else mix(c, "#000000", 0.35))
    ctx.restore()


def shot_not_only_fix(ctx, s):
    t = s.t
    bg(ctx, "#E6C38A")
    for i in range(-2, 20):
        line(ctx, i * 120, 0, i * 120 + 700, 1920, "#DDB87B", 40, cap=cairo.LINE_CAP_BUTT)
    cx, cy, z = kf(t, [(0, 540, 900, 0.95), (s.dur, 540, 840, 1.2)])
    ctx.save()
    camera(ctx, cx, cy, z)
    phone(ctx, 540, 840, 340, 640, "crack", rot=sway(t, 0.03, 2))
    gear(ctx, 230, 560, 110, "#7A6A58", t * 0.8)
    gear(ctx, 850, 1150, 90, "#7A6A58", -t * 1.0)
    # screwdriver
    ctx.save()
    ctx.translate(860, 560)
    ctx.rotate(0.9 + sway(t, 0.1, 3))
    rect(ctx, -14, -120, 28, 150, "#C0392B", 10)
    rect(ctx, -6, 30, 12, 110, "#9FA0A0", 3)
    ctx.restore()
    pc = prog(t, s.c(29) + 1.3, 0.45)
    cross(ctx, 540, 840, 300, "#B8352B", pc, 44)
    ctx.restore()
    p = pop(t, 0.3, 0.45)
    rect(ctx, 540 - 330 * p, 1230, 660 * p, 120, "#2B1D14", 36)
    text(ctx, "শুধু ফোন ঠিক করা", 540, 1290, 66, "#FFE08A", sc=p)


def shot_when_back(ctx, s):
    t = s.t
    bg(ctx, "#D9A441")
    sunburst(ctx, 540, 700, "#D9A441", "#E2B257", t, 22, speed=0.1)
    cx, cy, z = kf(t, [(0, 540, 940, 0.95), (s.dur, 540, 840, 1.18)])
    ctx.save()
    camera(ctx, cx, cy, z)
    clock(ctx, 540, 560, 230, minutes=t * 40)
    text(ctx, "?", 220, 330, 200, "#7A1F17", rot=-0.3 + sway(t, 0.1, 3), sc=pop(t, 0.3, 0.4))
    text(ctx, "?", 840, 400, 240, "#7A1F17", rot=0.3 + sway(t, 0.1, 2.5), sc=pop(t, 0.6, 0.4))
    py = 1170 + sway(t, 14, 3)
    phone(ctx, 540, py, 190, 340, "on", rot=sway(t, 0.05, 2.2))
    checkmark(ctx, 540, py, 90, "#3E8E41", prog(t, s.c(30) + 1.2, 0.5), 18)
    p = pop(t, s.c(30) + 0.3, 0.5)
    text(ctx, "কখন?", 540, 890, 150, "#7A1F17", sc=p, stroke=0)
    ctx.restore()


# =================================================================== night experiment
def shot_night_clock(ctx, s):
    t = s.t
    vgrad(ctx, "#2A1E1A", "#3A2A22")
    interior(ctx, t, "#4A3328", "#2F211B", "#3A281F", 580)
    # window with moon
    rect(ctx, 100, 380, 220, 300, "#1B1411", 8, sc="#6B4A32", lw=10)
    circ(ctx, 215, 500, 56, "#F3E7B8")
    circ(ctx, 235, 490, 50, "#1B1411")
    rgrad(ctx, 830, 520, 520, "#FFD58A", 0.5, 0)
    k = prog(t, s.dur * 0.45, s.dur * 0.4)
    cx, cy, z = kf(t, [(0, 400, 1000, 1.0), (s.dur * 0.42, 440, 980, 1.1), (s.dur, 800, 560, 2.3)])
    ctx.save()
    camera(ctx, cx, cy, z)
    clock(ctx, 830, 520, 95, minutes=580 + t * 0.4, sec=math.floor(t * 2) / 120.0)
    person(ctx, 320, 1270, 1.0, **ZAHID_AP, arms=((12, 8), (12, 8)), blink=blk(t), look=lerp(-0.3, 1.0, smooth(k * 2)),
           ly=-k, bob=sway(t, 2, 1.2), head_rot=k * 0.1, emo="n" if k < 0.3 else "think")
    draw_counter(ctx)
    # sign "বন্ধ"
    ctx.save()
    ctx.translate(120, 900)
    ctx.rotate(sway(t, 0.08, 2))
    line(ctx, 0, -50, 0, 0, "#B9A98A", 3)
    rect(ctx, -80, 0, 160, 80, "#B8352B", 10)
    text(ctx, "বন্ধ", 0, 40, 54, "#FFF3D0")
    ctx.restore()
    ctx.restore()


def shot_ten_phones(ctx, s):
    t = s.t
    vgrad(ctx, "#5B3A29", "#3E2619")
    rgrad(ctx, 540, 350, 1100, "#FFC96B", 0.55, 0)
    cx, cy, z = kf(t, [(0, 380, 860, 1.25), (s.dur, 700, 1000, 1.25)])
    ctx.save()
    camera(ctx, cx, cy, z)
    rect(ctx, -400, 520, 2000, 1000, "#A8774A")
    for i in range(0, 12):
        line(ctx, -400, 520 + i * 90, 1600, 520 + i * 90, "#946438", 4)
    c32 = s.c(32)
    for k in range(10):
        r_, c_ = divmod(k, 5)
        x = 150 + c_ * 195
        y = 700 + r_ * 380
        done_t = c32 + 0.9 + k * 0.38
        st = "crack" if t < done_t else "on"
        sy = y - 14 * math.sin(clamp((t - done_t) * 3, 0, 1) * math.pi)
        phone(ctx, x, sy, 130, 250, st)
        text(ctx, bn(k + 1), x, y + 160, 44, "#FFF3D0")
        if t >= done_t:
            checkmark(ctx, x, sy, 50, "#3E8E41", prog(t, done_t, 0.25), 12)
    # notebook
    ctx.save()
    ctx.translate(1100, 1180)
    ctx.rotate(-0.08)
    rect(ctx, -170, -130, 340, 260, "#FFF4D6", 8, sc="#6B4226", lw=6)
    text(ctx, "শুরু—শেষ", 0, -90, 40, "#7A1F17")
    nlines = int(clamp((t - c32) / 0.4, 0, 10))
    for i in range(min(nlines, 5)):
        line(ctx, -130, -50 + i * 36, 130, -50 + i * 36, "#2B1D14", 4, 0.8)
    ctx.restore()
    ctx.restore()


def shot_notebook_chart(ctx, s):
    t = s.t
    bg(ctx, "#F3E6C8")
    for i in range(0, 40):
        line(ctx, 0, 100 + i * 60, W, 100 + i * 60, "#D9C9A3", 3)
    line(ctx, 90, 0, 90, H, "#D77A6A", 4)
    vals = [46, 44, 50, 42, 48, 40, 45, 47, 43, 49]
    c33, c34 = s.c(33), s.c(34)
    hi_t = c33 + 3.1
    cx, cy, z = kf(t, [(0, 540, 960, 1.0), (hi_t - 0.5, 540, 900, 1.12), (hi_t + 0.5, 540, 900, 1.12),
                       (c34 + 0.1, 540, 1000, 1.12), (s.dur, 540, 1000, 1.3)])
    ctx.save()
    camera(ctx, cx, cy, z)
    text(ctx, "সময় (মিনিট)", 540, 330, 80, "#7A1F17", fam="serif")
    base = 1300
    sc_ = 13.0
    line(ctx, 130, base, 990, base, "#2B1D14", 6)
    for k, v in enumerate(vals):
        p = eo3(prog(t, 0.4 + k * 0.28, 0.5))
        h = v * sc_ * p
        is_hi, is_lo = v == 50, v == 40
        col = "#D9694E"
        if is_hi and t > hi_t:
            col = "#B8352B"
        if is_lo and t > c34 + 0.3:
            col = "#4E9A3F"
        rect(ctx, 150 + k * 83, base - h, 62, h, col, 8)
        if p > 0.95:
            text(ctx, bn(v), 181 + k * 83, base - h - 36, 34, "#2B1D14")
    if t > hi_t:
        p = pop(t, hi_t, 0.4)
        ctx.save()
        ctx.translate(150 + 2 * 83 + 31, base - 50 * sc_ - 150)
        ctx.scale(p, p)
        rect(ctx, -170, -50, 340, 100, "#B8352B", 30)
        text(ctx, "সর্বোচ্চ ৫০", 0, 0, 56, "#FFF3D0")
        ctx.restore()
    if t > c34 + 0.3:
        p = pop(t, c34 + 0.3, 0.4)
        ctx.save()
        ctx.translate(150 + 5 * 83 + 31, base - 40 * sc_ - 150)
        ctx.scale(p, p)
        rect(ctx, -170, -50, 340, 100, "#4E9A3F", 30)
        text(ctx, "সর্বনিম্ন ৪০", 0, 0, 56, "#FFF3D0")
        ctx.restore()
    ctx.restore()


# =================================================================== new ad
def shot_cross_old(ctx, s):
    t = s.t
    vgrad(ctx, "#F6D5B2", "#F2B987")
    circ(ctx, 300, 1180, 260, "#F7C36B", 0.7)
    rect(ctx, -1000, 1400, 4000, 800, "#C28A5E")
    cx, cy, z = kf(t, [(0, 480, 960, 1.0), (s.dur, 700, 880, 1.35)])
    ctx.save()
    camera(ctx, cx, cy, z)
    poster(ctx, 740, 880, 560, 760, "#FFF4D6")
    text(ctx, "দ্রুত ও নির্ভরযোগ্য\nমোবাইল সার্ভিস", 740, 880, 56, "#7A1F17", maxw=500, fam="serif")
    pc = eio(prog(t, s.c(35) + 1.1, 1.0))
    mx = lerp(560, 960, pc)
    line(ctx, 520, 880, mx, 880, "#C0392B", 14)
    line(ctx, 520, 960, lerp(520, 960, clamp(pc * 1.2 - 0.2)) , 960, "#C0392B", 14) if pc > 0.2 else None
    person(ctx, 260, 1420, 1.2, **ZAHID, arms=((100, 95 + 10 * math.sin(t * 8) * (1 if pc < 1 else 0)), (8, 4)), blink=blk(t),
           look=0.8, bob=sway(t, 2, 1.5), propR=lambda c: (c.save(), c.rotate(0.5), rect(c, -10, -70, 20, 80, "#C0392B", 6), c.restore()))
    ctx.restore()


def shot_new_ad(ctx, s):
    t = s.t
    bg(ctx, "#3F5B34")
    confetti(ctx, t, ["#F2B53A", "#E9D9A0", "#C9573F"], 45, 3, size=18)
    cx, cy, z = kf(t, [(0, 540, 1000, 1.0), (s.dur, 540, 850, 1.25)])
    ctx.save()
    camera(ctx, cx, cy, z, sway(t, 0.006, 1))
    p = back(prog(t, 0.0, 0.6))
    poster(ctx, 540, 820 + (1 - p) * -900, 900, 1020, "#FFF4D6", "#2B1D14")
    ctx.save()
    ctx.translate(0, (1 - p) * -900)
    t1 = typewriter("সাধারণ মডেলের\nস্ক্রিন বদলান", prog(t, s.c(37) + 0.2, 1.8))
    if t1:
        text(ctx, t1, 540, 650, 88, "#7A1F17", fam="serif", lh=1.35)
    if t > s.c(37) + 1.9:
        q = pop(t, s.c(37) + 1.9, 0.45)
        rect(ctx, 540 - 230 * q, 820, 460 * q, 160, "#F2B53A", 30)
        text(ctx, "৫০ মিনিটে", 540, 900, 110, "#7A1F17", sc=q)
    mp = prog(t, s.c(36), 1.4)
    if t < s.c(37) + 2.0:
        ctx.save()
        ctx.translate(lerp(900, 640, mp), lerp(1000, 700, mp))
        ctx.rotate(0.6)
        rect(ctx, -14, -90, 28, 130, "#C0392B", 8)
        rect(ctx, -9, 40, 18, 40, "#2B1D14", 4)
        ctx.restore()
    ctx.restore()
    ctx.restore()


def shot_half_charge(ctx, s):
    t = s.t
    bg(ctx, "#B8452E")
    sunburst(ctx, 540, 740, "#B8452E", "#C75A41", t, 20, speed=0.08)
    z = lerp(1.0, 1.15, smooth(t / s.dur))
    ctx.save()
    camera(ctx, 540, 900, z, sway(t, 0.01, 1.5))
    sp = eio(prog(t, s.c(38) + 0.9, 0.9))
    cp = pop(t, 0.0, 0.5)
    ctx.save()
    ctx.translate(540, 740)
    ctx.scale(cp, cp)
    # left half
    ctx.save()
    ctx.translate(-sp * 60, 0)
    ctx.rectangle(-400, -400, 400, 800)
    ctx.clip()
    circ(ctx, 0, 0, 250, "#F2B53A", 1, "#B58A2D", 14)
    circ(ctx, 0, 0, 190, None, 1, "#D99A22", 8)
    text(ctx, "৳", 0, 0, 220, "#7A5518")
    ctx.restore()
    ctx.save()
    ctx.translate(sp * 120, sp * 40)
    ctx.rotate(sp * 0.25)
    ctx.rectangle(0, -400, 400, 800)
    ctx.clip()
    col = mix("#F2B53A", "#8A7A62", sp)
    circ(ctx, 0, 0, 250, col, 1, "#7A6A58", 14)
    text(ctx, "৳", 0, 0, 220, "#5A4A3A")
    ctx.restore()
    ctx.restore()
    p = pop(t, s.c(38) + 0.6, 0.5)
    text(ctx, "চার্জ অর্ধেক", 540, 1230, 130, "#FFF3D0", sc=p, stroke=0)
    seal(ctx, 900, 400, 110, "#2F4F2A", "গ্যারান্টি", 34, rot=0.2, a=1.0) if p > 0.01 else None
    ctx.restore()
