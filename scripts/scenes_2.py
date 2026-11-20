# -*- coding: utf-8 -*-
"""Scenes 6-10: realisation, night experiment, new ad, first day, the real test."""
import math
import skia
from common import *
from gfx import *
from kit import *
from textkit import draw_text, text_width
from scenes_1 import shop_front, street, city_sky, walker, hold_phone
from gfx import _cone

DIG = '০১২৩৪৫৬৭৮৯'


def bn(n):
    return ''.join(DIG[int(ch)] for ch in str(n))


def bulb(c, x, y, r, p, t):
    if p <= 0:
        return
    c.drawCircle(x, y, r * 3.2 * p, blur_paint('#ffe08a', r, .75 * p))
    for k in range(12):
        a = k * math.pi / 6
        line(c, x + math.cos(a) * r * 1.5, y + math.sin(a) * r * 1.5, x + math.cos(a) * r * (1.9 + .4 * math.sin(t * 9 + k)), y + math.sin(a) * r * (1.9 + .4 * math.sin(t * 9 + k)), stroke('#ffd24a', 7, p))
    circle(c, x, y, r, fill('#fff0a0', p)); c.drawCircle(x, y, r, stroke('#e9b83a', 5, p))
    rrect(c, x - r * .5, y + r * .9, r, r * .7, 6, fill('#8a7a68', p))


# ================================================================== SCENE 6
def scene6(c, t, T):
    k36, k37, k38, k39 = T.s(36), T.s(37), T.s(38), T.s(39)
    z = keys(t, [(48.5, 1.0), (k37, 1.12), (k39 + 1, 1.3)], smooth)
    with cam(c, 540, 1000, z, 0, t=t):
        sky(c, '#7a4a2a', '#2e1b12', -600, 2700)
        c.drawCircle(540, 760, 700, blur_paint('#f2b04a', 140, .35 + .1 * math.sin(t * 3)))
        halftone(c, -100, -100, 1200, 1700, '#ffd98a', .06, 50, 9)
        m = max(T.mouth(t, 36), 0)
        emo = 'surprised' if (k36 - .1 < t < k36 + 1.2) else ('think' if t < k36 else 'happy' if t > k38 else 'neutral')
        person(c, 540, 1560, 1.9, **ZAHID, emo=emo, mouth=0, t=t, look=(0, -.6), armL=(-12, -6), armR=(12, 6), bob=math.sin(t * 2) * 3)
        counter(c, 100, 1500, 880, glass=False)
        bulb(c, 540, 330, 54, ease_out(prog(t, k36 - .1, k36 + .4)), t)
        sw = ease_out(prog(t, k37 + .1, k37 + .6))
    # left icon: repair (crossed)
    def icon_left(c, p):
        c.save(); c.translate(230, 640); c.scale(back_out(p), back_out(p))
        circle(c, 0, 0, 150, fill('#fff3d6')); circle(c, 0, 0, 150, stroke('#2a1d17', 6))
        phone(c, 0, 0, 90, 170, 0, 'open'); line(c, -70, 60, 70, -60, stroke('#8a8a8a', 16)); circle(c, 70, -60, 22, stroke('#8a8a8a', 12))
        cross(c, 0, 0, 100, '#d9382a', prog(t, k37 + .5, k37 + 1.0), 22)
        c.restore()
    def icon_right(c, p):
        c.save(); c.translate(850, 640); c.scale(back_out(p), back_out(p))
        c.drawCircle(0, 0, 220, blur_paint('#ffe08a', 40, .6))
        circle(c, 0, 0, 160, fill('#fff3d6')); circle(c, 0, 0, 160, stroke('#2f9e55', 10))
        wall_clock(c, 0, 0, 110, minutes=t * 4, sec=t * 1)
        phone(c, 100, 90, 60, 110, 20, 'new')
        c.restore()
    popup(c, t, k37 + .1, icon_left, .4); popup(c, t, k38 + .1, icon_right, .45)
    pq = prog(t, k39 - .1, k39 + .35)
    if pq > 0:
        question(c, 850, 380, 200, '#ffd24a', pq, 8)
    pc = prog(t, k39 + .3, k39 + .8)
    if pc > 0:
        checkmark(c, 860, 900, 70, '#4fd37f', pc, 22)


# ================================================================== SCENE 7
def room_night(c, t, clock_min, zahid=True):
    shop_wall(c, t, wall=('#5d3a2b', '#3a2219'), floor='#2a1b14', clock_min=clock_min, clock_x=860, clock_r=105, poster=False)
    c.drawPath(_cone(), grad(0, 46, 0, 900, '#ffd98a', '#ffd98a', 0.0))
    c.drawRect(skia.Rect.MakeLTRB(-500, -400, 1580, 1260), fill('#120804', .18))


def s7a(c, t, T):
    k = prog(t, 57.45, 58.7)
    z = keys(t, [(57.0, 1.0), (59.6, 1.15)])
    with cam(c, 540, 900, z, 0, t=t):
        sky(c, '#2e1b12', '#9c5a2e', -700, 1500)
        circle(c, 220, 330, 90, fill('#fff1c0')); c.drawCircle(220, 330, 190, blur_paint('#fff1c0', 50, .35))
        for k_ in range(14):
            sparkle(c, (k_ * 137) % 1000 + 40, 120 + (k_ * 53) % 420, 5, '#fff3c4', .5 + .5 * math.sin(t * 3 + k_))
        building(c, -300, 700, 380, 700, '#4a2e22', seed=2, lit=.4); building(c, 1000, 640, 380, 760, '#4a2e22', seed=5, lit=.3)
        street(c, 1260, road='#2d2019')
        shop_front(c, 540, 1260, 600, 600, 'মিরপুর মোবাইল সার্ভিসিং', t, down=ease_io(k), body='#8a4a30', sign_size=36)
        pull = math.sin(t * 5) * 8 * (1 - k)
        person(c, 880, 1330, 1.0, **ZAHID, emo='neutral', t=t, flip=True, look=(-1, 0), armL=(-20, -10 + pull), armR=(150 - k * 40, 170))


def s7b(c, t, T):
    k = T.s(42)
    z = keys(t, [(k - .5, 1.0), (k + .4, 2.8), (T.s(43) + .2, 2.8)], smooth)
    cx = keys(t, [(k - .5, 540), (k + .4, 860)], smooth)
    cy = keys(t, [(k - .5, 900), (k + .4, 440)], smooth)
    with cam(c, cx, cy, z, 0, t=t):
        room_night(c, t, 20 * 60 + 5 + t * .05)
        person(c, 460, 1310, 1.45, **ZAHID, emo='think', t=t, look=(1, -.8), tilt=-5)
        counter(c, 250, 1240, 800, col='#4d3a2c', top='#9c7c52')
        wall_clock(c, 860, 420, 105, minutes=20 * 60 + 5 + prog(t, k, k + 2) * 8, sec=t * 1, glow=.5)
    popup(c, t, k + .7, lambda c, p: (c.save(), c.translate(540, 1050), c.scale(back_out(p), back_out(p)),
                                      draw_text(c, 'টিক… টিক…', 0, 0, 90, '#ffe9a8', outline='#1a0f09', outline_w=14), c.restore()), .3)


def s7c(c, t, T):
    t0 = T.s(43)
    with cam(c, 540, 960, 1.0, 0, t=t):
        sky(c, '#8a5a35', '#4d3020', -500, 1700)
        halftone(c, -100, -100, 1200, 1700, '#000000', .08, 52, 10)
        for i in range(10):
            ti = t0 + i * .13
            col, row = i % 5, i // 5
            x, y = 140 + col * 200, 540 + row * 330
            u = prog(t, ti, ti + .3)
            if u <= 0:
                continue
            c.save(); c.translate(x, y); s = back_out(u); c.scale(s, s)
            ok = t > ti + .35
            phone(c, 0, 0, 120, 230, 0, 'new' if ok else 'crack', glow=.4 if ok and t < ti + .6 else 0)
            if ok:
                circle(c, 40, 100, 30, fill('#2f9e55')); checkmark(c, 40, 100, 22, '#ffffff', prog(t, ti + .35, ti + .6), 8)
            c.restore()
        wall_clock(c, 540, 1180, 120, minutes=t * 38, sec=t * 9)
        banner_text(c, '১০টি ফোন', 540, 250, 100, fg='#2a1d17', bg='#ffd24a', p=prog(t, t0 - .1, t0 + .3), rot=-2, border='#2a1d17')


def s7d(c, t, T):
    t0, t1 = T.s(44), T.e(45)
    z = keys(t, [(t0 - .4, 1.0), (t1, 1.2)])
    with cam(c, 540, 900, z, 0, t=t):
        sky(c, '#6e4526', '#3e2616', -500, 1700)
        c.save(); c.translate(540, 900); c.rotate(-2)
        rrect(c, -430, -620, 860, 1240, 18, fill('#f6efe0'))
        c.drawRect(skia.Rect.MakeXYWH(-430, -620, 860, 120), fill('#d9382a', .0))
        for k in range(14):
            line(c, -410, -420 + k * 72, 410, -420 + k * 72, stroke('#9ab0c0' if False else '#c8bda5', 3))
        line(c, -300, -620, -300, 620, stroke('#d9382a', 3, .7))
        draw_text(c, 'শুরু', -130, -520, 62, '#2a1d17'); draw_text(c, 'শেষ', 190, -520, 62, '#2a1d17')
        rows = [('৯:০০', '৯:৪৫'), ('৯:৫০', '১০:৪০'), ('১১:০০', '১১:৪৬'), ('১১:৫০', '১২:৪০'), ('১:০০', '১:৪৪'), ('১:৫০', '২:৩৯'), ('৩:০০', '৩:৪৮')]
        prg = prog(t, t0 + .1, t1 + .1) * len(rows)
        for i, (a, b) in enumerate(rows):
            u = clamp(prg - i)
            if u <= 0:
                continue
            c.save(); c.clipRect(skia.Rect.MakeXYWH(-420, -440 + i * 140 - 20, 840 * u, 130))
            draw_text(c, bn(i + 1) + '.', -370, -400 + i * 140 + 12, 52, '#7a6a55')
            draw_text(c, a, -130, -400 + i * 140 + 12, 58, '#1a3a8a' if False else '#3a2a1e')
            line(c, -10, -400 + i * 140 - 10, 70, -400 + i * 140 - 10, stroke('#b8302a', 8)); poly(c, [(70, -400 + i * 140 - 30), (100, -400 + i * 140 - 10), (70, -400 + i * 140 + 10)], fill('#b8302a'))
            draw_text(c, b, 190, -400 + i * 140 + 12, 58, '#3a2a1e')
            c.restore()
        c.restore()


def s7e(c, t, T):
    t0 = T.s(46)
    vals = [44, 47, 50, 42, 46, 48, 40, 45, 49, 43]
    kmax, kmin = T.s(47), T.s(48)
    with cam(c, 540, 950, 1.0, 0, t=t):
        sky(c, '#e8c079', '#c88a4a', -500, 1700)
        halftone(c, -100, -100, 1200, 1700, '#ffffff', .12, 50, 10)
        rrect(c, 50, 380, 980, 980, 30, fill('#fff6df'))
        base, hh = 1260, 700
        for g in range(0, 60, 10):
            y = base - g / 55 * hh
            line(c, 110, y, 990, y, stroke('#d8c8a8', 3)); draw_text(c, bn(g), 100, y + 14, 34, '#7a6a55', align='r')
        line(c, 110, base, 990, base, stroke('#3a2a1e', 6))
        for i, v in enumerate(vals):
            u = ease_out(prog(t, t0 + i * .05, t0 + .5 + i * .05))
            x = 150 + i * 84
            col = '#c9a85c'
            if v == 50 and t > kmax - .1: col = '#e9a21a'
            if v == 40 and t > kmin - .1: col = '#2f9e55'
            rrect(c, x, base - v / 55 * hh * u, 62, v / 55 * hh * u, 10, fill(col))
        pm = prog(t, kmax - .1, kmax + .35)
        if pm > 0:
            line(c, 110, base - 50 / 55 * hh, 990, base - 50 / 55 * hh, stroke('#e9a21a', 6, pm))
            banner_text(c, 'সর্বোচ্চ ৫০ মিনিট', 540, 330, 66, fg='#2a1d17', bg='#ffd24a', p=pm, border='#2a1d17')
        pn = prog(t, kmin - .1, kmin + .35)
        if pn > 0:
            banner_text(c, 'সর্বনিম্ন ৪০ মিনিট', 540, 1470 - 0, 60, fg='#ffffff', bg='#2f9e55', p=pn, border='#ffffff') if False else None
            line(c, 110, base - 40 / 55 * hh, 990, base - 40 / 55 * hh, stroke('#2f9e55', 6, pn))
            draw_text(c, '৪০', 1000, base - 40 / 55 * hh - 14, 56, '#2f9e55', align='r', alpha=pn)
        draw_text(c, '৫০', 1000, base - 50 / 55 * hh - 14, 56, '#c9811a', align='r', alpha=pm)


def scene7(c, t, T):
    phases(c, t, [lambda c, t_: s7a(c, t_, T), (T.s(42) - .45, .5, 'iris', lambda c, t_: s7b(c, t_, T)),
                  (T.s(43) - .25, .45, 'slide', lambda c, t_: s7c(c, t_, T)), (T.s(44) - .3, .45, 'wipe', lambda c, t_: s7d(c, t_, T)),
                  (T.s(46) - .3, .45, 'iris', lambda c, t_: s7e(c, t_, T))])


# ================================================================== SCENE 8
def board(c, cx, cy, w, h):
    rrect(c, cx - w / 2 + 10, cy - h / 2 + 14, w, h, 24, fill('#000000', .3))
    rrect(c, cx - w / 2, cy - h / 2, w, h, 24, fill('#5a3a22'))
    rrect(c, cx - w / 2 + 22, cy - h / 2 + 22, w - 44, h - 44, 14, fill('#fff3d6'))
    for sx in (-1, 1):
        circle(c, cx + sx * (w / 2 - 40), cy - h / 2 + 40, 11, fill('#b9a77a'))


def s8a(c, t, T):
    k = ease_io(prog(t, 69.3, 70.4))
    z = keys(t, [(69.0, 1.0), (70.6, 1.2)])
    with cam(c, 540, 900, z, 0, t=t):
        sky(c, '#ffcf9a', '#f09a52', -700, 1500)
        c.drawCircle(540, 1120, 500, blur_paint('#fff0b0', 90, .8))
        rays(c, 540, 1100, t, '#fff6d0', .3, 12)
        building(c, -300, 700, 380, 700, '#c27447', seed=2, lit=.9); building(c, 1000, 640, 380, 760, '#b8663f', seed=5, lit=.9)
        street(c, 1260)
        shop_front(c, 540, 1260, 700, 640, 'মিরপুর মোবাইল সার্ভিসিং', t, down=1 - k, body='#c9573b', sign_size=40,
                   inside=lambda c, x, y, w, h: person(c, x + w / 2, y + h + 20, 1.0, **ZAHID, emo='happy', t=t))
        for j in range(8):
            sparkle(c, 540 + math.sin(j * 2.3) * 400, 700 + math.cos(j * 3.1 + t) * 250, 16, '#fff6d0', .5 + .5 * math.sin(t * 4 + j), t)
    popup(c, t, 69.3, lambda c, p: label_tag(c, 'পরদিন সকালে', 540, 250, 70, bg='#1a0f09', p=p, rot=-2), .4, out=71.0)


def s8b(c, t, T):
    k50, k51, k52, k53 = T.s(50), T.s(51), T.s(52), T.s(53)
    with cam(c, 540, 820, keys(t, [(k50 - .5, 1.0), (k53 + 1, 1.12)]), 0, t=t):
        sky(c, '#ffcf9a', '#f09a52', -700, 1700)
        halftone(c, -100, -100, 1200, 1700, '#ffffff', .15, 50, 10)
        board(c, 540, 700, 960, 800)
        if t < k51 - .1:
            draw_text(c, 'দ্রুত ও নির্ভরযোগ্য', 540, 640, 80, '#2a1d17')
            draw_text(c, 'মোবাইল সার্ভিস', 540, 780, 100, '#2a1d17')
            u = prog(t, k50 + .2, k50 + .8)
            if u > 0:
                line(c, 150, 600, 150 + 780 * u, 600 - 40 * u + 20, stroke('#d9382a', 16))
                line(c, 150, 760, 150 + 780 * u, 760 - 40 * u + 20, stroke('#d9382a', 16))
        else:
            u1 = prog(t, k52 - .1, T.e(52))
            u2 = prog(t, k53 - .1, T.e(53))
            c.save(); c.clipRect(skia.Rect.MakeXYWH(100, 400, 880 * u1, 300))
            draw_text(c, 'সাধারণ মডেলের', 540, 520, 78, '#2a1d17')
            draw_text(c, 'স্ক্রিন বদলান ৫০ মিনিটে', 540, 640, 74, '#b8302a')
            c.restore()
            c.save(); c.clipRect(skia.Rect.MakeXYWH(100, 700, 880 * u2, 300))
            rrect(c, 160, 710, 760, 130, 20, fill('#ffd24a'))
            draw_text(c, 'না পারলে চার্জ অর্ধেক', 540, 800, 74, '#2a1d17')
            c.restore()
            # marker
            if t < T.e(53) + .2:
                mx = 100 + 880 * (u1 if u2 <= 0 else u2); my = 640 if u2 <= 0 else 800
                c.save(); c.translate(mx, my); c.rotate(35); rrect(c, 0, -20, 24, 160, 8, fill('#b8302a')); rrect(c, 0, -34, 24, 18, 4, fill('#2a1d17')); c.restore()
        person(c, 540, 1520, 1.15, **ZAHID, emo='happy' if t > k52 else 'neutral', t=t, show_legs=False, look=(0, -.6),
               armL=(-20, -10), armR=(130 + math.sin(t * 8) * 10, 160))
        counter(c, 100, 1500, 880, glass=False)
    if t > T.e(53) - .2:
        burst(c, 540, 700, prog(t, T.e(53) - .1, T.e(53) + .6), '#ffffff', 12, 420, 560)


def scene8(c, t, T):
    phases(c, t, [lambda c, t_: s8a(c, t_, T), (T.s(50) - .55, .5, 'iris', lambda c, t_: s8b(c, t_, T))])


# ================================================================== SCENE 9
def scene9(c, t, T):
    k54, k55, k56 = T.s(54), T.s(55), T.s(56)
    z = keys(t, [(75.3, 1.0), (k56, 1.0), (k56 + 1.3, 1.5)], smooth)
    cx = keys(t, [(k56, 540), (k56 + 1.3, 740)], smooth)
    cy = keys(t, [(k56, 900), (k56 + 1.3, 700)], smooth)
    with cam(c, cx, cy, z, 0, t=t):
        shop_wall(c, t, wall=('#9cb86a', '#6f8c46'), floor='#4d4030', clock_min=540 + (t - 75) * 9, clock_x=860, clock_r=110, poster=False,
                  clock_x_dummy=0) if False else shop_wall(c, t, wall=('#9cb86a', '#6f8c46'), floor='#4d4030', clock_min=540 + (t - 75) * 9, clock_x=860, clock_r=110, poster=False)
        wall_clock(c, 860, 420, 110, minutes=540 + (t - 75) * 9, sec=t * 4, ring=('#d9382a', prog(t, k56, k56 + 2.4)) if t > k56 else None)
        person(c, 840, 1300, 1.3, **ZAHID, emo='happy' if t > k55 else 'neutral', t=t, look=(-.4, 0), armR=(30, 150 + math.sin(t * 8) * 8), seed=.7)
        counter(c, 560, 1240, 620)
        for i, ch in enumerate(CROWD):
            ti = k54 - .3 + i * .22
            u = prog(t, ti, ti + 1.0)
            if u <= 0:
                continue
            x = lerp(-160 - i * 40, 75 + i * 98, ease_out(u))
            y = 1470 + (i % 2) * 36
            looking = t > k56
            if u < 1:
                walker(c, x, y, .72, t + i, ch, speed=3.8)
            else:
                shadow_ellipse(c, x, y + 150, 66, 14)
                person(c, x, y, .72, **ch, emo='neutral', t=t, look=(.6, -1) if looking else (.2, 0), seed=i * .9,
                       tilt=-4 if looking else 0, armL=(-8, -6), armR=(8, 6))
            if u >= 1:
                p = prog(t, ti + 1.0, ti + 1.25)
                if p > 0 and t < k55 + .1:
                    c.save(); c.translate(x, y - 330); c.scale(back_out(p), back_out(p))
                    circle(c, 0, 0, 34, fill('#ffd24a')); draw_text(c, bn(i + 1), 0, 14, 42, '#2a1d17'); c.restore()
    banner_text(c, 'ছয়জন কাস্টমার', 540, 250, 90, fg='#2a1d17', bg='#ffd24a', p=prog(t, k54, k54 + .4), rot=-2, border='#2a1d17')
    if k55 < t < k56 - .2:
        p = prog(t, k55 + .1, k55 + .5)
        c.save(); c.translate(540, 520); c.scale(back_out(p), back_out(p))
        banner_text(c, 'দাম?', 0, 0, 100, fg='#ffffff', bg='#5a3a22', p=1)
        cross(c, 0, 0, 120, '#d9382a', prog(t, k55 + .3, k55 + .7), 24)
        c.restore()
    if t > k56 + .2:
        label_tag(c, '৫০ মিনিট…', 540, 250, 76, bg='#1a0f09', p=prog(t, k56 + .2, k56 + .6), rot=2) if False else None


# ================================================================== SCENE 10
WEIRD = lambda c, x, y, rot=0: (c.save(), c.translate(x, y), c.rotate(rot), rrect(c, -90, -140, 180, 280, 34, fill('#6a8f5b')), rrect(c, -78, -128, 156, 256, 26, fill('#151515')),
                              rrect(c, -70, -120, 140, 130, 18, fill('#e0b04a')), circle(c, 0, 80, 34, fill('#e9e0c8')), c.restore())


def s10a(c, t, T):
    k = T.s(57)
    with cam(c, 540, 900, 1.0 + .05 * prog(t, 80.5, 83.5), 0, t=t):
        sky(c, '#f1d9a4', '#d9a05a', -500, 1700)
        halftone(c, -100, -100, 1200, 1700, '#ffffff', .15, 50, 10)
        flip = prog(t, 81.2, 82.0)
        c.save(); c.translate(540, 780)
        rrect(c, -330, -380, 660, 760, 30, fill('#000000', .25)) if False else None
        rrect(c, -340, -400, 680, 800, 30, fill('#fff6df')); rrect(c, -340, -400, 680, 170, 30, fill('#b8302a'))
        for sx in (-180, 180):
            circle(c, sx, -400, 20, fill('#5a3a22'))
        draw_text(c, 'তৃতীয় সপ্তাহ', 0, -285, 84, '#fff6df')
        for r in range(3):
            for q in range(7):
                if r * 7 + q < 21:
                    circle(c, -270 + q * 90, -130 + r * 120, 30, fill('#f0e2c0'))
                    draw_text(c, bn(r * 7 + q + 1), -270 + q * 90, -130 + r * 120 + 14, 36, '#7a6a55')
        pp = prog(t, 82.2, 82.8)
        c.drawOval(skia.Rect.MakeLTRB(-300, 90, -240 + 60 * 0 + 480 * 0 + 180, 170), stroke('#d9382a', 8, pp)) if False else None
        c.restore()
        # sheets flipping away
        for i in range(4):
            u = prog(t, 81.0 + i * .22, 81.5 + i * .22)
            if 0 < u < 1:
                c.save(); c.translate(540, 380); c.rotate(-u * 40); c.translate(-u * 700, -u * 500)
                rrect(c, -340, -20, 680, 760, 30, fill('#fff6df', 1 - u)); c.restore()
        wall_clock(c, 900, 260, 90, minutes=t * 5, sec=t * 5) if False else None


def s10b(c, t, T):
    k58, k59 = T.s(58), T.s(59)
    cx = keys(t, [(k58 - .3, 560), (k59, 480), (T.s(60), 480)], smooth)
    z = keys(t, [(k58 - .3, 1.0), (k59, 1.35), (T.s(60) + .3, 1.35)], smooth)
    with cam(c, cx, 920, z, 0, t=t):
        shop_wall(c, t, wall=('#a9c070', '#7a9650'), floor='#51442f', clock_min=700 + t * .2, clock_x=860, clock_r=100, poster=True)
        person(c, 800, 1300, 1.45, **ZAHID, emo='think' if t > k59 else 'neutral', t=t, look=(-.8, 0), armR=(10, 6), tilt=-3)
        counter(c, 460, 1240, 720)
        u = prog(t, k58 - .1, k58 + .9)
        x = lerp(-250, 240, ease_out(u))
        if u < 1:
            walker(c, x, 1400, 1.28, t, CUST3, speed=3.4, hold=lambda c: (c.rotate(180), WEIRD(c, 0, -85, 0), c.scale(1, 1)) if False else None)
        else:
            shadow_ellipse(c, x, 1400 + 205 * 1.28, 100, 20)
            person(c, x, 1400, 1.28, **CUST3, emo='neutral', t=t, look=(.8, 0), armR=(100, -172), armL=(-8, -6),
                   hold=lambda c: (c.rotate(180), c.scale(.55, .55), WEIRD(c, 0, -140)))
        if u >= 1:
            pass
        pw = prog(t, k59, k59 + .4)
        if pw > 0:
            c.save(); c.translate(240, 800); c.scale(back_out(pw), back_out(pw)); c.rotate(-4)
            c.drawCircle(0, 0, 230, blur_paint('#ffe08a', 40, .5))
            WEIRD(c, 0, 0, 0)
            for kk in range(5):
                sparkle(c, math.cos(kk * 1.3 + t * 2) * 190, math.sin(kk * 1.3 + t * 2) * 190, 18, '#fff3b0', .8, t)
            c.restore()
    popup(c, t, k59 + .1, lambda c, p: banner_text(c, 'বিরল মডেল', 540, 280, 100, fg='#fff6df', bg='#b8302a', rot=-3, p=p), .4, out=T.s(60) + .2)


def s10c(c, t, T):
    t0 = T.s(60)
    p = prog(t, t0 - .1, t0 + .7)
    mins = p * 70
    over = mins > 50
    shake = math.sin(t * 50) * 6 * (1 if over else 0)
    with cam(c, 540, 900, 1.0 + .05 * p, 0, t=t):
        sky(c, '#e8c079' if not over else '#c9573b', '#b8764a' if not over else '#7a2d1c', -500, 1700)
        halftone(c, -100, -100, 1200, 1700, '#ffffff', .1, 50, 10)
        c.save(); c.translate(540 + shake, 800)
        c.drawCircle(0, 0, 420, blur_paint('#000000', 30, .25))
        circle(c, 0, 0, 400, fill('#fff6df')); circle(c, 0, 0, 400, stroke('#5a3a22', 22))
        c.drawArc(skia.Rect.MakeLTRB(-340, -340, 340, 340), -90, min(mins, 50) / 60 * 360, False, stroke('#2f9e55', 40, 1, skia.Paint.kButt_Cap))
        if over:
            c.drawArc(skia.Rect.MakeLTRB(-340, -340, 340, 340), -90 + 50 / 60 * 360, (mins - 50) / 60 * 360, False, stroke('#d9382a', 40, 1, skia.Paint.kButt_Cap))
        a = mins / 60 * 2 * math.pi
        line(c, 0, 0, math.sin(a) * 300, -math.cos(a) * 300, stroke('#2a1d17', 16)); circle(c, 0, 0, 22, fill('#2a1d17'))
        draw_text(c, bn(int(mins)), 0, 200, 140, '#d9382a' if over else '#2a1d17')
        draw_text(c, 'মিনিট', 0, 280, 54, '#5a3a22')
        c.restore()
        # 50 limit marker
        a50 = 50 / 60 * 2 * math.pi
        line(c, 540 + math.sin(a50) * 350, 800 - math.cos(a50) * 350, 540 + math.sin(a50) * 470, 800 - math.cos(a50) * 470, stroke('#2f9e55', 14))
        draw_text(c, '৫০', 540 + math.sin(a50) * 540, 800 - math.cos(a50) * 520 + 20, 54, '#2f9e55')
    if over:
        banner_text(c, 'সত্তর মিনিট!', 540, 1250, 110, fg='#ffffff', bg='#b8302a', rot=-2 + shake * .05, p=prog(t, t0 + .55, t0 + .85), border='#ffffff')


def s10d(c, t, T):
    k61, k62, k63, k64, k65, k66 = [T.s(i) for i in (61, 62, 63, 64, 65, 66)]
    cx = keys(t, [(k61, 540), (k63, 520), (k65, 460)], smooth)
    z = keys(t, [(k61 - .2, 1.0), (k63, 1.1), (k65, 1.3)], smooth)
    with cam(c, cx, 920, z, 0, t=t):
        shop_wall(c, t, wall=('#a9c070', '#7a9650'), floor='#51442f', clock_min=800 + t * .2, clock_x=860, clock_r=100, poster=True)
        mz = max(T.mouth(t, 62), T.mouth(t, 63), T.mouth(t, 61) * .5)
        nod = math.sin(prog(t, k66, k66 + 1.0) * math.pi * 3) * 10 if t > k66 else 0
        person(c, 800, 1300, 1.45, **ZAHID, emo='neutral' if t > k66 else 'happy', mouth=mz, t=t, look=(-.8, 0), armR=talk_arm(t, mz), tilt=nod, bob=nod * .3)
        counter(c, 460, 1240, 720)
        mc = max(T.mouth(t, 64), T.mouth(t, 65))
        emo = 'surprised' if (t > k64 and t < T.e(65) + .4) else ('happy' if t > k66 else 'neutral')
        shadow_ellipse(c, 240, 1400 + 205 * 1.28, 100, 20)
        give = prog(t, k61, k61 + .6)
        person(c, 240, 1400, 1.28, **CUST3, emo=emo, mouth=mc, t=t, look=(.8, 0), armL=(-8, -6), armR=(100 - give * 0, -172), seed=2.2)
        if t < k62 + .6:
            c.save(); c.translate(560 - give * 0 + lerp(0, -160, 0), 1190); WEIRD(c, 0, 0, 80) if False else None; c.restore()
    bt = lambda i, d=.3: prog(t, T.s(i), T.s(i) + .22) * (1 - prog(t, T.e(i) + d, T.e(i) + d + .3))
    bubble(c, 790, 520, 620, 130, 'ভাই, আমার কথা রাখতে পারিনি।', tail=(-120, 90), size=38, bg='#fff3c4', p=bt(62, .3), t=t)
    bubble(c, 790, 520, 600, 190, 'তাই শ্রমের চার্জ\nঅর্ধেক দিন।', tail=(-120, 90), size=50, bg='#fff3c4', p=bt(63, .6), t=t)
    bubble(c, 330, 560, 560, 190, 'আপনি নিজে থেকেই\nকমাচ্ছেন?', tail=(100, 80), size=52, p=bt(65, .5), t=t)
    # charge halves
    pb = prog(t, k63 + .4, k63 + .9) * (1 - prog(t, k64 + .6, k64 + 1.0))
    if pb > 0:
        c.save(); c.translate(540, 300); c.scale(back_out(pb), back_out(pb))
        rrect(c, -300, -90, 600, 180, 24, fill('#fff6df')); c.drawRoundRect(skia.Rect.MakeXYWH(-300, -90, 600, 180), 24, 24, stroke('#2a1d17', 5))
        c.save(); c.clipRect(skia.Rect.MakeXYWH(0, -90, 300, 180)); rrect(c, -300, -90, 600, 180, 24, fill('#d9382a', .25)); c.restore()
        draw_text(c, 'শ্রমের চার্জ', -150, 20, 48, '#2a1d17'); draw_text(c, '−৫০%', 150, 28, 76, '#d9382a')
        c.restore()


def s10e(c, t, T):
    k67 = T.s(67)
    with cam(c, 540, 900, 1.0 + .05 * prog(t, k67, 96), 0, t=t):
        city_sky(c, t, '#f6d38e', '#e8975a')
        street(c, 1260)
        shop_front(c, 540, 1260, 560, 560, 'মিরপুর মোবাইল সার্ভিসিং', t, sign_size=38, body='#c9573b',
                   inside=lambda c, x, y, w, h: person(c, x + w / 2, y + h + 10, .95, **ZAHID, emo='happy', t=t, armR=(150 + math.sin(t * 7) * 20, 150)))
        u = prog(t, k67 - .1, k67 + 2.0)
        for i, ch in enumerate((CUST3, dict(CUST4, skin='#c58f62', style='short', beard='stubble'))):
            x = lerp(-250 - i * 170, 300 + i * 170, ease_out(u)) if i == 0 else lerp(-250 - 170, 300 + 170, ease_out(prog(t, k67 + .0, k67 + 2.2)))
            walker(c, x, 1345, .9 - i * .06, t + i, ch, speed=3.4, emo='happy' if u > .6 else 'neutral')
        for k in range(6):
            ph = (t * .7 + k * .17) % 1
            hp = skia.Path(); x, y = 300 + k * 60, 900 - ph * 360
            hp.moveTo(x, y + 20); hp.cubicTo(x - 38, y - 8, x - 20, y - 38, x, y - 14); hp.cubicTo(x + 20, y - 38, x + 38, y - 8, x, y + 20)
            c.drawPath(hp, fill('#d9382a', (1 - ph) * prog(t, k67 + 1, k67 + 1.6)))
    popup(c, t, k67, lambda c, p: label_tag(c, 'পরের সপ্তাহে', 540, 250, 70, bg='#1a0f09', p=p, rot=-2), .4, out=T.e(68) + .1)
    popup(c, t, T.s(68) + .4, lambda c, p: banner_text(c, 'ভাইকে নিয়ে!', 540, 380, 90, fg='#2a1d17', bg='#ffd24a', p=p, rot=2, border='#2a1d17'), .4)


def scene10(c, t, T):
    phases(c, t, [lambda c, t_: s10a(c, t_, T), (T.s(58) - .35, .45, 'wipe', lambda c, t_: s10b(c, t_, T)),
                  (T.s(60) - .1, .4, 'iris', lambda c, t_: s10c(c, t_, T)), (T.s(61) - .3, .45, 'slide', lambda c, t_: s10d(c, t_, T)),
                  (T.s(67) - .3, .5, 'iris', lambda c, t_: s10e(c, t_, T))])


SCENES = {6: scene6, 7: scene7, 8: scene8, 9: scene9, 10: scene10}
