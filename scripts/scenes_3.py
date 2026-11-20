# -*- coding: utf-8 -*-
"""Scenes 11-14: the lesson, the book, the takeaway, the ending."""
import math
import skia
from common import *
from gfx import *
from kit import *
from textkit import draw_text, text_width
from scenes_1 import shop_front, street, walker
from gfx import _cone
from scenes_2 import bn, bulb


def gauge(c, x, y, r, needle, p=1.0):
    c.save(); c.translate(x, y); c.scale(back_out(p), back_out(p))
    circle(c, 0, 0, r * 1.05, fill('#fff6df')); circle(c, 0, 0, r * 1.05, stroke('#5a3a22', 12))
    c.drawArc(skia.Rect.MakeLTRB(-r * .8, -r * .8, r * .8, r * .8), 150, 80, False, stroke('#2f9e55', 26, 1, skia.Paint.kButt_Cap))
    c.drawArc(skia.Rect.MakeLTRB(-r * .8, -r * .8, r * .8, r * .8), 230, 80, False, stroke('#e9a21a', 26, 1, skia.Paint.kButt_Cap))
    c.drawArc(skia.Rect.MakeLTRB(-r * .8, -r * .8, r * .8, r * .8), 310, 80, False, stroke('#d9382a', 26, 1, skia.Paint.kButt_Cap))
    a = math.radians(150 + needle * 240)
    line(c, 0, 0, math.cos(a) * r * .7, math.sin(a) * r * .7, stroke('#2a1d17', 10)); circle(c, 0, 0, 16, fill('#2a1d17'))
    c.restore()


def shield(c, x, y, r, p=1.0, chk=1.0):
    c.save(); c.translate(x, y); c.scale(back_out(p), back_out(p))
    c.drawCircle(0, 0, r * 1.5, blur_paint('#ffe08a', 40, .6))
    sp = skia.Path(); sp.moveTo(0, -r); sp.cubicTo(r * .9, -r * .8, r * 1.0, -r * .6, r * .95, -r * .1)
    sp.cubicTo(r * .9, r * .6, r * .3, r * .9, 0, r * 1.1); sp.cubicTo(-r * .3, r * .9, -r * .9, r * .6, -r * .95, -r * .1)
    sp.cubicTo(-r * 1.0, -r * .6, -r * .9, -r * .8, 0, -r)
    c.drawPath(sp, fill('#2f9e55')); c.drawPath(sp, stroke('#fff6df', 12))
    checkmark(c, 0, 0, r * .55, '#ffffff', chk, r * .16)
    c.restore()


# ================================================================== SCENE 11
def scene11(c, t, T):
    k69, k70, k71 = T.s(69), T.s(70), T.s(71)
    z = keys(t, [(94.8, 1.0), (99.8, 1.22)])
    with cam(c, 540, 930, z, 0, t=t):
        shop_wall(c, t, wall=('#f0c378', '#d99a4a'), floor='#7a5236', clock_min=840 + t * .2, clock_x=860, clock_r=110, poster=False)
        c.drawCircle(860, 420, 260, blur_paint('#fff1b0', 50, .55))
        person(c, 540, 1300, 1.5, **ZAHID, emo='happy' if t > k70 else 'think', mouth=0, t=t, look=(.9, -.6), armL=(-12, -6),
               armR=(14 + 80 * prog(t, k71, k71 + .5), 8 - 150 * prog(t, k71, k71 + .5)), tilt=3)
        counter(c, 200, 1240, 880)
        bulb(c, 330, 330, 40, ease_out(prog(t, k69 + .5, k69 + .9)), t)
    # speed gauge and shield
    g = prog(t, k70 - .1, k70 + .4)
    if g > 0:
        gauge(c, 270, 700, 150, .25 + .6 * prog(t, k70, k70 + 1.2) + math.sin(t * 20) * .02, g)
        label_tag(c, 'দ্রুত কাজ', 270, 930, 56, bg='#1a0f09', p=g)
    s = prog(t, k71 - .1, k71 + .45)
    if s > 0:
        shield(c, 810, 700, 130, s, prog(t, k71 + .35, k71 + .8))
        label_tag(c, 'প্রতিশ্রুতি', 810, 930, 56, bg='#2f6b4f', p=s)
    if g > 0 and s > 0:
        draw_text(c, '+', 540, 740, 130, '#2a1d17', outline='#fff6df', outline_w=14, alpha=min(g, s))
    popup(c, t, k69 + .1, lambda c, p: label_tag(c, 'ধীরে ধীরে…', 540, 250, 70, bg='#1a0f09', p=p, rot=-2), .4, out=k70 + .2)


# ================================================================== SCENE 12
def book(c, x, y, s, flip=0.0, t=0.0):
    c.save(); c.translate(x, y); c.scale(s * max(.05, abs(math.cos(flip))), s)
    rrect(c, -270 + 14, -370 + 20, 540, 740, 14, fill('#000000', .4))
    rrect(c, -270, -370, 540, 740, 14, fill('#7a1f2a'))
    rrect(c, -270, -370, 40, 740, 6, fill('#5a1520'))
    c.drawRoundRect(skia.Rect.MakeXYWH(-215, -320, 460, 640), 8, 8, stroke('#e9c25a', 6))
    draw_text(c, 'TESTED', 10, -190, 100, '#e9c25a')
    draw_text(c, 'ADVERTISING', 10, -80, 78, '#f6efe0')
    draw_text(c, 'METHODS', 10, 20, 100, '#e9c25a')
    line(c, -120, 80, 140, 80, stroke('#e9c25a', 5))
    draw_text(c, 'John Caples', 10, 220, 66, '#f6efe0')
    c.restore()


def scene12(c, t, T):
    k72, k73, k74, k75, k76, k77 = [T.s(i) for i in (72, 73, 74, 75, 76, 77)]
    def a(c, t):
        z = keys(t, [(99.5, 1.0), (k74, 1.2)])
        with cam(c, 540, 860, z, 0, t=t):
            sky(c, '#4a2e20', '#1e120c', -600, 1700)
            rays(c, 540, 800, t, '#e9c25a', .14, 12)
            u = prog(t, 99.9, k72 + .5)
            book(c, 540, 820 - (1 - ease_out(u)) * 600, .95 + .05 * math.sin(t * 2), (1 - ease_out(u)) * 6.0, t)
            for k in range(10):
                sparkle(c, 540 + math.sin(k * 2.1 + t) * 420, 820 + math.cos(k * 3.3 + t * .8) * 520, 10 + k % 3 * 5, '#ffe9a8', .6 * u, t * 2)
    def b(c, t):
        with cam(c, 540, 900, 1.0 + .04 * prog(t, k74, k76), 0, t=t):
            sky(c, '#e8d3a2', '#bf9a62', -600, 1700)
            halftone(c, -100, -100, 1200, 1700, '#ffffff', .12, 50, 10)
            words = [('ভালো', 300, 520, '#f4a62a'), ('সেরা', 780, 700, '#7a8f3c'), ('দ্রুত', 420, 1000, '#d9582a')]
            for i, (w_, x, y, col) in enumerate(words):
                ti = k74 - .1 + i * .18
                u = prog(t, ti, ti + .35)
                if u <= 0:
                    continue
                dfl = prog(t, k75, k75 + .9)
                c.save(); c.translate(x + math.sin(t * 2 + i) * 12, y + float_y(t, 14, 2.2, i) + dfl * 400)
                s = back_out(u) * (1 - dfl * .4); c.scale(s, s)
                # balloon
                oval(c, 0, 0, 190, 120, fill(mix(col, '#808080', dfl * .8)))
                c.drawOval(skia.Rect.MakeLTRB(-190, -120, 190, 120), stroke('#2a1d17', 5))
                oval(c, -80, -50, 40, 20, fill('#ffffff', .4))
                draw_text(c, w_, 0, 30, 96, '#fffaf0')
                c.restore()
            st = prog(t, k75 - .05, k75 + .25)
            if st > 0:
                c.save(); c.translate(540, 780); c.rotate(-10); s = 1 + (1 - back_out(st)) * 1.4; c.scale(s, s)
                c.drawRoundRect(skia.Rect.MakeXYWH(-250, -110, 500, 220), 24, 24, stroke('#d9382a', 14, st))
                draw_text(c, 'দাবি', 0, 50, 170, '#d9382a', alpha=st)
                c.restore()
    def d(c, t):
        with cam(c, 540, 900, 1.0 + .05 * prog(t, k76, 108), 0, t=t):
            sky(c, '#ffd57e', '#e8913a', -600, 1700)
            rays(c, 540, 760, t, '#fff0b0', .3, 14)
            u = prog(t, k76 - .05, k76 + .5)
            c.save(); c.translate(540, 720); s = back_out(u); c.scale(s, s)
            c.drawCircle(0, 0, 420, blur_paint('#fff6d0', 60, .8))
            circle(c, 0, 0, 330, fill('#fff6df')); circle(c, 0, 0, 330, stroke('#e9a21a', 24))
            draw_text(c, '৫০', 0, 70, 300, '#2a1d17')
            draw_text(c, 'মিনিট', 0, 200, 90, '#b8302a')
            c.restore()
            for i, (txt, x) in enumerate((('প্রমাণযোগ্য', 300), ('বিশ্বাসযোগ্য', 780))):
                p = prog(t, k77 + i * .3, k77 + i * .3 + .4)
                if p > 0:
                    banner_text(c, txt, x, 1180, 62, fg='#fff6df', bg='#2f6b4f', p=p, rot=-2 + i * 4)
            checkmark(c, 880, 480, 80, '#2f9e55', prog(t, k76 + .6, k76 + 1.1), 24)
            stopwatch(c, 190, 480, 80, (t * .2) % 1) if t > k76 + .3 else None
    phases(c, t, [a, (k74 - .3, .45, 'iris', b), (k76 - .25, .45, 'wipe', d)])


# ================================================================== SCENE 13
def scene13(c, t, T):
    k78, k79, k80, k81 = [T.s(i) for i in (78, 79, 80, 81)]
    def a(c, t):
        with cam(c, 540, 900, 1.0 + .05 * prog(t, 107, 110), 0, t=t):
            sky(c, '#f6d97a', '#e9c04a', -600, 1700)
            for k in range(-2, 28):
                line(c, -100, k * 80, 1200, k * 80, stroke('#c9a83a', 3, .7))
            line(c, 130, -100, 130, 1700, stroke('#d9382a', 4, .6))
            u = prog(t, 107.4, k78 + .4)
            banner_text(c, 'PRACTICAL', 540, 520, 150, fg='#ffd24a', bg='#1a0f09', p=u, rot=-3, border='#ffd24a')
            banner_text(c, 'TAKEAWAY', 540, 760, 150, fg='#1a0f09', bg='#ffd24a', p=prog(t, 107.6, k78 + .5), rot=2, border='#1a0f09')
            bulb(c, 880, 260, 46, ease_out(prog(t, k78 + .3, k78 + .7)), t)
            for k in range(6):
                sparkle(c, 200 + k * 160, 1000 + math.sin(k + t * 2) * 30, 14, '#ffffff', .8, t * 2)
            p2 = prog(t, k78 + .8, k78 + 1.2)
            if p2 > 0:
                c.save(); c.translate(540, 1050); s = back_out(p2); c.scale(s, s)
                draw_text(c, 'বিজ্ঞাপন লেখার আগে…', 0, 0, 72, '#1a0f09')
                line(c, -330, 28, 330 * (2 * prog(t, k78 + 1.0, k79 + .5) - 1), 28, stroke('#d9382a', 8)) if t > k78 + 1.0 else None
                c.restore()
    def b(c, t):
        zz = keys(t, [(k80, 1.0), (k81 + 1.8, 1.25)], smooth)
        with cam(c, 540, 900, zz, 0, t=t):
            sky(c, '#fff0c4', '#f1cf7a', -600, 1700)
            halftone(c, -100, -100, 1200, 1700, '#d9a21a', .15, 50, 10)
            rrect(c, 70, 320, 940, 760, 40, fill('#000000', .2))
            rrect(c, 50, 300, 940, 760, 40, fill('#fffaf0')); c.drawRoundRect(skia.Rect.MakeXYWH(50, 300, 940, 760), 40, 40, stroke('#1a0f09', 8))
            u = prog(t, k81 - .1, k81 + .5)
            for i, ln in enumerate(('আমার কথাটা কি কেউ', 'ঘড়ি ধরে মিলিয়ে', 'দেখতে পারবে?')):
                a_ = prog(t, k81 + i * .45 - .05, k81 + i * .45 + .3)
                draw_text(c, ln, 520, 520 + i * 150, 88, '#b8302a' if i == 1 else '#1a0f09', alpha=a_)
            sw = prog(t, k81 - .2, k81 + .4)
            c.save(); c.translate(820, 1180); s = back_out(sw); c.scale(s, s)
            stopwatch(c, 0, 0, 150, ((t - k81) * .12) % 1)
            c.restore()
            ck = prog(t, T.e(81) - .35, T.e(81) + .15)
            if ck > 0:
                checkmark(c, 330, 1190, 120, '#2f9e55', ck, 36)
            q = prog(t, k80 - .1, k80 + .4)
            if q > 0 and u <= 0:
                draw_text(c, 'নিজেকে জিজ্ঞেস করো…', 540, 700, 80, '#1a0f09', alpha=q)
            elif u > 0:
                pass
    phases(c, t, [a, (k80 - .25, .45, 'slide', b)])


# ================================================================== SCENE 14
def scene14(c, t, T):
    k82, k83, k84, k85, k86, k87 = [T.s(i) for i in (82, 83, 84, 85, 86, 87)]
    def a(c, t):
        z = keys(t, [(113.8, 1.0), (k82 + .4, 1.0), (k82 + 1.6, 2.5), (k83 - .2, 2.5), (k83 + .6, 1.1), (k84 + 1.4, 1.35)], smooth)
        cx = keys(t, [(113.8, 540), (k82 + .4, 560), (k82 + 1.6, 860), (k83 - .2, 860), (k83 + .6, 640)], smooth)
        cy = keys(t, [(113.8, 900), (k82 + 1.6, 440), (k83 - .2, 440), (k83 + .6, 940)], smooth)
        with cam(c, cx, cy, z, 0, t=t):
            shop_wall(c, t, wall=('#f6cb7e', '#df9f4c'), floor='#7d5538', clock_min=900 + t * .1, clock_x=860, clock_r=105, poster=True)
            c.drawCircle(860, 420, 300, blur_paint('#fff6c8', 60, .5))
            c.drawPath(_cone(), grad(0, 46, 0, 900, '#fff4c0', '#fff4c0', 0.0))
            look = (1, -.6) if t < k83 + .2 else (.2, 0)
            person(c, 560, 1300, 1.5, **ZAHID, emo='happy', t=t, look=look, armL=(-12, -6), armR=(12 + (40 if t > k84 else 0), 6), tilt=3 if t < k83 else 0)
            counter(c, 250, 1240, 800)
            # happy customers peeking
            if t > k83:
                for i, ch in enumerate((CUST3, CUST2)):
                    u = prog(t, k83 + .2 + i * .3, k83 + 1.0 + i * .3)
                    shadow_ellipse(c, 150 + i * 100, 1700, 60, 14)
                    person(c, lerp(-100, 130 + i * 110, ease_out(u)), 1560, .85, **ch, emo='happy', t=t, look=(.5, -.5), show_legs=True,
                           legs=(math.sin(t * 8) * 20 * (1 - u), -math.sin(t * 8) * 20 * (1 - u)))
    def b(c, t):
        with cam(c, 540, 900, 1.0 + .04 * prog(t, k85, k86), 0, t=t):
            sky(c, '#f6e6c0', '#e5c68a', -600, 1700)
            halftone(c, -100, -100, 1200, 1700, '#ffffff', .2, 50, 10)
            u = prog(t, k85, k85 + .35)
            dfl = prog(t, k85 + .5, k85 + 1.6)
            c.save(); c.translate(540 + math.sin(t * 2) * 14, 620 - dfl * 140 + float_y(t, 16, 2.4)); s = back_out(u); c.scale(s, s)
            oval(c, 0, 0, 330, 200, fill('#fffaf0')); c.drawOval(skia.Rect.MakeLTRB(-330, -200, 330, 200), stroke('#2a1d17', 7))
            for k in range(3):
                circle(c, -200 + k * 200, 190, 32 - k * 6, fill('#fffaf0'))
            draw_text(c, 'দ্রুত', 0, 50, 190, '#2a1d17')
            c.restore()
            p = prog(t, k85 + .5, k85 + .9)
            if p > 0:
                draw_text(c, '=', 540, 1010, 190, '#2a1d17', alpha=p)
                banner_text(c, 'দাবি', 540, 1260, 150, fg='#fffaf0', bg='#b8302a', p=p, rot=-3)
    def d(c, t):
        with cam(c, 540, 900, 1.0 + .04 * prog(t, k86, k87), 0, t=t):
            sky(c, '#ffd57e', '#e8913a', -600, 1700)
            rays(c, 540, 700, t, '#fff0b0', .3, 14)
            u = prog(t, k86, k86 + .4)
            c.save(); c.translate(540, 640); s = back_out(u); c.scale(s, s)
            c.drawCircle(0, 0, 400, blur_paint('#fff6d0', 50, .7))
            rrect(c, -420, -200, 840, 400, 40, fill('#fffaf0')); c.drawRoundRect(skia.Rect.MakeXYWH(-420, -200, 840, 400), 40, 40, stroke('#2a1d17', 8))
            draw_text(c, 'পঞ্চাশ', 0, -10, 170, '#b8302a'); draw_text(c, 'মিনিট', 0, 150, 150, '#2a1d17')
            c.restore()
            p = prog(t, k86 + .5, k86 + .9)
            if p > 0:
                draw_text(c, '=', 540, 1010, 190, '#2a1d17', alpha=p)
                banner_text(c, 'প্রতিশ্রুতি', 540, 1260, 130, fg='#fffaf0', bg='#2f6b4f', p=p, rot=2)
                shield(c, 880, 330, 90, prog(t, k86 + .9, k86 + 1.3), prog(t, k86 + 1.2, k86 + 1.6)) if t > k86 + .9 else None
                stopwatch(c, 200, 330, 80, 1.0)
            burst(c, 540, 1260, prog(t, k86 + .5, k86 + 1.2), '#ffffff', 12, 360, 520)
    def e(c, t):
        with cam(c, 540, 900, 1.0, 0, t=t):
            sky(c, '#c9473a', '#8a2a22', -600, 1700)
            halftone(c, -100, -100, 1200, 1700, '#ffffff', .1, 54, 12)
            wall_clock(c, 540, 480, 170, minutes=t * 3, sec=t * 2, glow=.4)
            draw_text(c, 'আরও practical গল্পের জন্য', 540, 860, 62, '#fff6df')
            pl = 1 + .06 * math.sin(t * 8)
            c.save(); c.translate(540, 1060); c.scale(pl * back_out(prog(t, k87, k87 + .4)), pl * back_out(prog(t, k87, k87 + .4)))
            rrect(c, -330, -90, 660, 180, 90, fill('#ffd24a')); c.drawRoundRect(skia.Rect.MakeXYWH(-330, -90, 660, 180), 90, 90, stroke('#1a0f09', 8))
            draw_text(c, 'ফলো করুন', 0, 36, 100, '#1a0f09')
            c.restore()
            # tap finger
            fy = 1160 - abs(math.sin(t * 5)) * 30
            c.save(); c.translate(760, fy); c.rotate(-20)
            rrect(c, -22, 0, 44, 120, 22, fill('#e8b88f')); rrect(c, -22, -40, 44, 70, 22, fill('#e8b88f')); circle(c, 0, 90, 56, fill('#e8b88f'))
            c.restore()
    phases(c, t, [a, (k85 - .3, .45, 'iris', b), (k86 - .1, .4, 'wipe', d), (k87 - .2, .4, 'slide', e)])


SCENES = {11: scene11, 12: scene12, 13: scene13, 14: scene14}
