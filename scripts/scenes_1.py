# -*- coding: utf-8 -*-
"""Scenes 1-5: hook, the shop, the ad, customers walking away, the schoolgirl."""
import math
import skia
from common import *
from gfx import *
from kit import *
from gfx import _cone
from textkit import draw_text, text_width


# ------------------------------------------------------------------ shared exterior pieces
def shop_front(c, cx, by, w, h, sign, t, down=0.0, body='#c9573b', sign_bg='#2a1d17', sign_fg='#ffe9a8', sign_size=54,
               inside=None, lit=True):
    x = cx - w / 2
    top = by - h
    c.drawRect(skia.Rect.MakeXYWH(x - 30, top - 20, w + 60, h + 20), fill(mix(body, '#000000', .25)))
    c.drawRect(skia.Rect.MakeXYWH(x, top, w, h), fill(body))
    rrect(c, x + 20, top + 14, w - 40, 112, 14, fill(sign_bg))
    c.drawRoundRect(skia.Rect.MakeXYWH(x + 28, top + 22, w - 56, 96), 10, 10, stroke(sign_fg, 3, .6))
    draw_text(c, sign, cx, top + 14 + 112 / 2 + sign_size * .34, sign_size, sign_fg)
    # awning
    ay = top + 140
    n = 10
    for k in range(n):
        col = '#b8302a' if k % 2 == 0 else '#f1e5c4'
        p = skia.Path()
        x0 = x + k * w / n; x1 = x0 + w / n
        p.moveTo(x0, ay); p.lineTo(x1, ay); p.lineTo(x1, ay + 56); p.quadTo((x0 + x1) / 2, ay + 92, x0, ay + 56); p.close()
        c.drawPath(p, fill(col))
    # opening
    ox, oy, ow, oh = x + 40, ay + 110, w - 80, by - (ay + 110)
    c.drawRect(skia.Rect.MakeXYWH(ox, oy, ow, oh), grad(0, oy, 0, oy + oh, '#f2c97a' if lit else '#4a3a30', '#c98a4a' if lit else '#2a1f1a'))
    if inside:
        c.save(); c.clipRect(skia.Rect.MakeXYWH(ox, oy, ow, oh)); inside(c, ox, oy, ow, oh); c.restore()
    c.drawRect(skia.Rect.MakeXYWH(ox - 12, oy - 10, ow + 24, 12), fill(mix(body, '#000000', .4)))
    shutter(c, ox, oy, ow, oh, down)
    c.drawRect(skia.Rect.MakeXYWH(x - 30, by, w + 60, 26), fill('#8a7a68'))
    return ox, oy, ow, oh


def street(c, y, x0=-900, x1=2000, road='#4a3a33'):
    c.drawRect(skia.Rect.MakeLTRB(x0, y, x1, y + 130), fill('#a39280'))
    c.drawRect(skia.Rect.MakeLTRB(x0, y + 130, x1, y + 900), grad(0, y + 130, 0, y + 900, road, mix(road, '#000000', .3)))
    for k in range(-8, 14):
        c.drawRect(skia.Rect.MakeXYWH(k * 260, y + 420, 140, 12), fill('#e8d9b0', .55))


def city_sky(c, t, c0='#f6cf82', c1='#e8975a', sun=True):
    sky(c, c0, c1, -700, 1500)
    if sun:
        circle(c, 780, 420, 150, fill('#fff1c0', .85))
        c.drawCircle(780, 420, 320, blur_paint('#fff1c0', 80, .5))
    for i, (bx, bw, bh, col) in enumerate([(-700, 260, 700, '#b8663f'), (-420, 230, 900, '#a65a38'), (-180, 220, 600, '#c27447'),
                                           (1100, 240, 800, '#a65a38'), (1330, 260, 650, '#b8663f'), (1570, 240, 880, '#c27447'),
                                           (200, 170, 360, '#d28a58'), (780, 190, 440, '#d28a58')]):
        building(c, bx, 1100 - bh, bw, bh + 40, col, seed=i, lit=.3)


def rickshaw(c, x, y, s, t, flip=False):
    c.save(); c.translate(x, y); c.scale(-s if flip else s, s)
    for wx in (-90, 70):
        circle(c, wx, 0, 62, stroke('#2a1d17', 9))
        for k in range(8):
            a = k * math.pi / 4 + t * 6
            line(c, wx, 0, wx + math.cos(a) * 58, math.sin(a) * 58, stroke('#d9c27a', 2.5))
    rrect(c, -110, -110, 190, 28, 10, fill('#b8302a'))
    p = skia.Path(); p.moveTo(-100, -110); p.cubicTo(-100, -230, 70, -230, 70, -110); p.close()
    c.drawPath(p, fill('#d94a3a')); c.drawPath(p, stroke('#e9b83a', 6))
    rrect(c, -86, -105, 150, 18, 6, fill('#f1e5c4'))
    line(c, 80, -110, 150, -20, stroke('#2a1d17', 9))
    c.restore()
    person(c, x + (40 if flip else -40) * s, y - 40 * s, .34 * s / 0.8, skin='#a86e45', shirt='#e0b04a', style='cap', show_legs=False)


def walker(c, x, y, s, t, ch, flip=False, speed=3.4, **kw):
    wp = walk_pose(t, speed)
    shadow_ellipse(c, x, y + 205 * s, 80 * s, 18 * s)
    person(c, x, y + wp['bob'] * s, s, **ch, flip=flip, legs=wp['legs'], armL=wp['armL'], armR=wp['armR'], t=t, **kw)


def hold_phone(rot=180, pw=84, ph=160, screen='crack', cracks=False):
    return lambda c: (c.rotate(rot), phone(c, 0, -ph * .55, pw, ph, 0, screen, cracks=cracks))


# ================================================================== SCENE 1
def s1a(c, t, T):
    z = keys(t, [(0, 2.15), (0.8, 1.9), (3.7, 1.0)], ease_out)
    cy = keys(t, [(0, 800), (3.7, 880)])
    sh = 10 * max(0, 1 - t / 1.4) + (3 if t < 3.8 else 0)
    with cam(c, 590, cy, z, 0, shake=sh, t=t):
        shop_wall(c, t, wall=('#d2603a', '#9c3b25'), floor='#5a3a2a', clock_min=t * 70, clock_x=880, clock_r=105)
        m = T.mouth(t, 1)
        person(c, 640, 1300, 1.5, **ZAHID, emo='worried', mouth=m, armL=(-100, 172), armR=(100, -172), t=t,
               bob=math.sin(t * 13) * 3, look=(0.2, 0.3), tilt=math.sin(t * 5) * 3, hold=hold_phone(), seed=0.4)
        counter(c, 380, 1240, 800)
        for k in range(4):   # spilled screws / tools
            circle(c, 520 + k * 38, 1215, 7, fill('#c9c0b0'))
    # slam title + stopwatch (screen space)
    sp = .55 + .45 * prog(t, 0, .3)
    jit = math.sin(t * 40) * 4 * max(0, 1 - t / .8)
    banner_text(c, '৫০ মিনিট', 540 + jit, 330, 190, fg='#ffd24a', bg='#1a0f09', pad=44, rot=-3 + jit * .2, p=sp, border='#ffd24a')
    popup(c, t, .5, lambda c, p: (c.save(), c.translate(860, 640), c.scale(back_out(p), back_out(p)),
                                  stopwatch(c, 0, 0, 100, (t * 0.35) % 1), c.restore()), .4)
    popup(c, t, 1.3, lambda c, p: question(c, 190, 640, 150, '#ffe9a8', p, -10), .35)


def s1b(c, t, T):
    z = keys(t, [(3.4, 1.0), (7.6, 1.25)])
    cy = keys(t, [(3.4, 900), (7.6, 780)])
    with cam(c, 540, cy, z, 0, t=t):
        sky(c, '#ffd57e', '#f0873a', -700, 1500)
        rays(c, 540, 650, t, '#fff0b0', .32)
        for i, (bx, bw, bh, col) in enumerate([(-300, 300, 800, '#b8663f'), (-40, 150, 600, '#c27447'),
                                               (930, 160, 700, '#c27447'), (1080, 300, 850, '#b8663f')]):
            building(c, bx, 1260 - bh, bw, bh, col, seed=i, lit=.8)
        street(c, 1260)
        shop_front(c, 540, 1260, 760, 700, '৫০ মিনিটে স্ক্রিন বদল', t, sign_size=50,
                   inside=lambda c, x, y, w, h: person(c, x + w / 2, y + h + 20, 1.05, **ZAHID, emo='happy',
                                                       armR=(150 + math.sin(t * 7) * 25, 150), t=t))
        # fortune: coins fountain
        for k in range(16):
            ph = (t * 0.55 + k * 0.137) % 1
            coin(c, 540 + math.sin(k * 2.1) * 320 * ph, 1000 - ph * 900, 26, t * 6 + k)
        for k in range(10):
            sparkle(c, 540 + math.sin(k * 1.9 + t) * 420, 500 + math.cos(k * 2.7 + t * 1.3) * 300, 20 + (k % 3) * 8,
                    a=.5 + .5 * math.sin(t * 5 + k), rot=t * 2)
        # customers streaming in
        for i, ch in enumerate((CUST1, CUST2, CUST4, CUST5)):
            t0 = 3.9 + i * 0.5
            side = -1 if i % 2 == 0 else 1
            u = prog(t, t0, t0 + 2.4)
            x = 540 + side * (700 * (1 - ease_out(u)) + 130 + i * 25)
            walker(c, x, 1330 - (1 - abs(u - .5) * 2) * 0, 0.78, t + i, ch, flip=(side > 0), speed=3.8)
    popup(c, t, T.s(2) - .1, lambda c, p: banner_text(c, 'ভাগ্য বদল!', 540, 280, 118, fg='#2a1d17', bg='#ffd24a', rot=3, p=p,
                                                      border='#2a1d17'), .45)


def s1c(c, t, T):
    z = keys(t, [(7.3, 1.0), (10.9, 1.4)])
    flick = 0.0
    with cam(c, 620, 960, z, 0, t=t):
        shop_wall(c, t, wall=('#6e594c', '#4d3d34'), floor='#2f241e', clock_min=t * 0.7, clock_x=880, lamp=False, poster=False)
        c.drawRect(skia.Rect.MakeLTRB(-500, -400, 1580, 1260), fill('#000000', .22))
        person(c, 760, 1320, 1.45, **{**ZAHID, 'shirt': '#5b6330'}, emo='sad', mouth=0.0, t=t, tilt=-7 + math.sin(t * 1.5) * 2,
               armL=(-70, 150), armR=(70, -150), look=(0, 1), bob=math.sin(t * 1.4) * 4)
        counter(c, 380, 1240, 800, col='#4d3a2c', top='#9c7c52')
        # rent bill
        c.save(); c.translate(560, 1215); c.rotate(-6)
        rrect(c, -110, -150, 220, 150, 6, fill('#f1e8d2'))
        draw_text(c, 'ভাড়া', 0, -105, 42, '#3a2a1e')
        draw_text(c, '২২,০০০৳', 0, -52, 40, '#b8302a')
        for k in range(2):
            rrect(c, -80, -34 + k * 14, 160 - k * 50, 6, 3, fill('#3a2a1e', .5))
        pst = prog(t, 8.5, 8.8)
        if pst > 0:
            c.save(); c.rotate(-14); s = 1.0 + (1 - back_out(pst)) * 1.5; c.scale(s, s)
            c.drawRoundRect(skia.Rect.MakeXYWH(-80, -118, 160, 66), 8, 8, stroke('#c0392b', 7, pst))
            draw_text(c, 'বাকি', 0, -70, 54, '#c0392b', alpha=pst); c.restore()
        c.restore()
        # shutter coming down
        down = prog(t, 9.2, 10.6)
        shutter(c, -500, -400, 2080, 1700, ease_io(down) * .8)
    popup(c, t, 7.7, lambda c, p: label_tag(c, 'এক বছর আগে', 540, 250, 66, bg='#1a0f09', fg='#ffe9a8', p=p, rot=-2), .4, out=9.4)
    screen_fade(c, prog(t, 10.2, 10.9) * .45)


def scene1(c, t, T):
    phases(c, t, [lambda c, t_: s1a(c, t_, T), (T.s(2) - .2, .45, 'iris', lambda c, t_: s1b(c, t_, T)),
                  (T.s(4) - .3, .5, 'wipe', lambda c, t_: s1c(c, t_, T))])


# ================================================================== SCENE 2
def s2a(c, t, T):
    z = keys(t, [(10.6, .72), (13.9, 1.45)], ease_io)
    cy = keys(t, [(10.6, 900), (13.9, 1010)], ease_io)
    with cam(c, 540, cy, z, 0, t=t):
        city_sky(c, t)
        street(c, 1260)
        rickshaw(c, keys(t, [(10.6, -400), (14, 1500)], lambda u: u), 1500, .8, t)
        shop_front(c, 540, 1260, 520, 520, 'মিরপুর মোবাইল সার্ভিসিং', t, sign_size=40, body='#c9573b',
                   inside=lambda c, x, y, w, h: (person(c, x + w / 2, y + h + 10, .9, **ZAHID, emo='neutral', t=t),
                                                 counter(c, x - 20, y + h - 60, w + 40, glass=False)))
        for k in range(3):
            circle(c, 80 + k * 400 + math.sin(t + k) * 30, 160 + k * 50, 70, fill('#ffffff', .25))
    popup(c, t, T.s(7) + .25, lambda c, p: (c.save(), c.translate(540, 330 - (1 - ease_out(p)) * -0), c.scale(back_out(p), back_out(p)),
                                           _pin(c), banner_text(c, 'মিরপুর, ঢাকা', 0, 200, 80, fg='#fff7e0', bg='#2a1d17', p=1),
                                           c.restore()), .5, out=13.6)


def _pin(c):
    p = skia.Path(); p.moveTo(0, 90); p.cubicTo(-80, -20, -60, -100, 0, -100); p.cubicTo(60, -100, 80, -20, 0, 90)
    c.drawPath(p, fill('#d9382a')); c.drawPath(p, stroke('#ffffff', 5, .9)); circle(c, 0, -34, 24, fill('#ffffff'))


def s2b(c, t, T):
    k1, k2 = T.s(8) + .25, T.s(9) + .1
    cx = keys(t, [(13.3, 700), (k1 - .1, 640), (k1 + .6, 250), (k2 - .1, 250), (k2 + .5, 860)], smooth)
    cyy = keys(t, [(13.3, 900), (k1 - .1, 840), (k1 + .6, 400), (k2 - .1, 400), (k2 + .5, 420)], smooth)
    zz = keys(t, [(13.3, 1.1), (k1 - .1, 1.1), (k1 + .6, 2.3), (k2 - .1, 2.3), (k2 + .5, 2.9)], smooth)
    with cam(c, cx, cyy, zz, 0, t=t):
        shop_wall(c, t, wall=('#dcab62', '#bb8346'), floor='#6e4a31', clock_min=612 + t * .12, clock_x=860, clock_r=100, poster=False)
        # father's photo
        fx, fy = 245, 360
        c.drawCircle(fx, fy, 230, blur_paint('#fff0b0', 40, .35 + .15 * math.sin(t * 2)))
        rrect(c, fx - 120, fy - 160, 240, 320, 8, fill('#5a3a22'))
        c.save(); c.clipRect(skia.Rect.MakeXYWH(fx - 104, fy - 144, 208, 288))
        c.drawRect(skia.Rect.MakeXYWH(fx - 104, fy - 144, 208, 288), grad(0, fy - 144, 0, fy + 144, '#e3cfa6', '#bfa377'))
        person(c, fx, fy + 190, .68, skin='#a9754d', shirt='#d9d2c0', style='cap', beard='white', show_legs=False, emo='happy', t=t)
        c.restore()
        for k in range(12):
            circle(c, fx - 120 + k * 22, fy - 168 + math.sin(k) * 4 + abs(k - 5.5) * 3, 13, fill('#f08a1c' if k % 2 else '#f2b21c'))
        person(c, 560, 1300, 1.45, **ZAHID, emo='sad' if t < k2 else 'neutral', t=t, look=(-0.8, -0.3), armL=(-10, -6), armR=(10, 6))
        counter(c, 380, 1240, 800)
        # dust motes
        for k in range(14):
            sparkle(c, 200 + (k * 137) % 800 + math.sin(t + k) * 15, 300 + (k * 71) % 700 + t * 8 % 30, 5, '#fff3c4', .5)


def s2c(c, t, T):
    z = keys(t, [(16.4, 1.0), (18.0, 1.12)])
    with cam(c, 540, 960, z, 0, t=t):
        sky(c, '#e8a04a', '#b8662a', -600, 1500)
        halftone(c, -100, -100, 1200, 1400, '#ffffff', .1, 44, 9)
        rays(c, 540, 800, t, '#ffe4a0', .15, 10)
        m = T.mouth(t, 10)
        sw = math.sin(t * 9)
        person(c, 540, 1280, 1.5, **ZAHID, emo='worried', mouth=m, armL=(-70 + sw * 30, -150 + sw * 20), armR=(70 - sw * 30, 150 - sw * 20),
               t=t, bob=abs(sw) * -8, look=(sw * .5, 0))
        counter(c, 200, 1250, 680, glass=False)
        t0 = T.s(10)
        # popups around him
        def flyer(c, p):
            c.save(); c.translate(230, 600); c.rotate(-9 + (1 - p) * 40); c.scale(back_out(p), back_out(p))
            rrect(c, -110, -150, 220, 300, 8, fill('#fff6df')); c.drawRoundRect(skia.Rect.MakeXYWH(-110, -150, 220, 300), 8, 8, stroke('#2a1d17', 4))
            rrect(c, -90, -130, 180, 70, 6, fill('#b8302a')); draw_text(c, 'সার্ভিস', 0, -80, 48, '#fff6df')
            phone(c, 0, 50, 70, 130, 0, 'new')
            c.restore()
        def tag(c, p):
            banner_text(c, '৩০% ছাড়', 810, 560, 78, fg='#2a1d17', bg='#ffd24a', rot=7, p=p, border='#2a1d17')
        def stars(c, p):
            c.save(); c.translate(540, 380); s = back_out(p); c.scale(s, s)
            for k in range(5):
                sparkle(c, (k - 2) * 78, 0, 38, '#ffd24a', 1, t * 1.5 + k)
            c.restore()
        def heart(c, p):
            for k in range(6):
                ph = ((t * .8 + k * .17) % 1)
                x, y = 840 + math.sin(k * 3 + t * 2) * 60, 900 - ph * 380
                c.save(); c.translate(x, y); c.scale(.8 + k % 3 * .2, .8 + k % 3 * .2)
                hp = skia.Path(); hp.moveTo(0, 22); hp.cubicTo(-40, -8, -22, -40, 0, -16); hp.cubicTo(22, -40, 40, -8, 0, 22)
                c.drawPath(hp, fill('#d9382a', (1 - ph) * p)); c.restore()
        popup(c, t, t0 + .1, flyer, .35); popup(c, t, t0 + .3, tag, .35)
        popup(c, t, t0 + .5, stars, .35); popup(c, t, t0 + .7, heart, .3)
        for b in (t0 + .1, t0 + .3, t0 + .5):
            burst(c, 540, 800, prog(t, b, b + .5), '#fff0b0', 8, 300, 520)


def s2d(c, t, T):
    t0 = T.s(11)
    z = keys(t, [(17.5, 1.0), (20.8, 1.3)])
    cx = keys(t, [(17.5, 560), (20.8, 700)])
    with cam(c, cx, 950, z, 0, t=t):
        shop_wall(c, t, wall=('#a9b36a', '#7e8a46'), floor='#5b4a38', clock_min=t * 2.2, clock_x=860, clock_r=110, poster=False)
        person(c, 560, 1330, 1.5, **ZAHID, emo='neutral', t=t, look=(0, 1), tilt=8, armL=(-30, 140), armR=(34 + math.sin(t * 14) * 5, 150),
               hold=lambda c: (c.rotate(180), rrect(c, -4, -90, 8, 70, 3, fill('#d9d4c8')), rrect(c, -9, -20, 18, 24, 5, fill('#d9822b'))))
        counter(c, 330, 1240, 850, glass=False)
        # phone being repaired + sparks
        phone(c, 600, 1195, 110, 70, 90, 'open')
        for k in range(4):
            ph = (t * 2.3 + k * .27) % 1
            sparkle(c, 600 + math.sin(k * 3) * 40, 1170 - ph * 90, 9 * (1 - ph), '#fff3b0', 1 - ph)
        # unused stopwatch, crossed out
        stopwatch(c, 960, 1130, 80, (t * .1) % 1)
        c.drawCircle(960, 1130, 100, fill('#2f241a', .35))
        cp = prog(t, T.s(12) + .1, T.s(12) + .6)
        cross(c, 960, 1130, 90, '#d9382a', cp, 22)
    # clock in focus-less bg: floating "?" none


def scene2(c, t, T):
    phases(c, t, [lambda c, t_: s2a(c, t_, T), (T.s(8) - .4, .5, 'slide', lambda c, t_: s2b(c, t_, T)),
                  (T.s(10) - .1, .45, 'iris', lambda c, t_: s2c(c, t_, T)), (T.s(11) + .1, .45, 'wipe', lambda c, t_: s2d(c, t_, T))])


# ================================================================== SCENE 3
def scene3(c, t, T):
    kq = T.s(15)
    z = keys(t, [(20.4, 1.0), (T.s(14), 1.15), (kq - .2, 1.2), (kq + .8, 1.55)], smooth)
    cy = keys(t, [(20.4, 800), (kq, 760), (kq + .8, 640)], smooth)
    rot = math.sin(t * 17) * 1.4 * prog(t, kq + .2, kq + 1.0) if t > kq else 0
    with cam(c, 540, cy, z, rot, t=t):
        c.drawRect(skia.Rect.MakeLTRB(-500, -500, 1600, 1500), fill('#c36a47'))
        for r in range(-3, 24):                      # brick wall
            for k in range(-2, 8):
                bx = k * 200 + (100 if r % 2 else 0)
                rrect(c, bx, r * 70, 192, 62, 4, fill(mix('#c36a47', '#7a3a24', ((r * 7 + k * 3) % 5) / 8)))
        # banner
        sw = math.sin(t * 2.2)
        c.save(); c.translate(540, 560); c.skew(sw * .01, 0)
        for sx in (-440, 440):
            line(c, sx, -380, sx * .9, -170, stroke('#2a1d17', 7))
        cloth = skia.Path()
        cloth.moveTo(-480, -190)
        cloth.cubicTo(-240, -190 + sw * 14, 240, -190 - sw * 14, 480, -190)
        cloth.lineTo(480, 210)
        cloth.cubicTo(240, 210 - sw * 14, -240, 210 + sw * 14, -480, 210)
        cloth.close()
        c.save(); c.translate(10, 14); c.drawPath(cloth, blur_paint('#000000', 14, .35)); c.restore()
        c.drawPath(cloth, fill('#fff3d6'))
        c.drawPath(cloth, stroke('#b8302a', 14))
        p14 = prog(t, T.s(14) - .1, T.s(14) + 1.0)
        c.save(); c.clipRect(skia.Rect.MakeXYWH(-480, -200, 960 * (0.04 + .96 * p14 if t > T.s(14) - .2 else 0.0), 420))
        draw_text(c, 'দ্রুত ও নির্ভরযোগ্য', 0, -35, 94, '#b8302a')
        draw_text(c, 'মোবাইল সার্ভিস', 0, 110, 118, '#2a1d17')
        c.restore()
        c.restore()
        # Zahid beneath
        pr = prog(t, kq, kq + .4)
        person(c, 540, 1330, 1.4, **ZAHID, emo='think' if t > kq else 'happy', mouth=0, t=t,
               armL=(-12, -8), armR=(10 + pr * 110, 8 - pr * 160 if pr else 6), look=(0, -.8 if t > kq else 0))
        counter(c, 160, 1250, 760, glass=False)
        if t > kq:
            popup(c, t, kq + .05, lambda c, p: (question(c, 200, 340, 260, '#ffd24a', p, -12), None), .4)
            popup(c, t, kq + .25, lambda c, p: question(c, 880, 300, 330, '#ffffff', p, 10), .4)
            popup(c, t, kq + .5, lambda c, p: (c.save(), c.translate(760, 1000), c.scale(back_out(p), back_out(p)),
                                              stopwatch(c, 0, 0, 100, (t - kq) * .6 % 1), c.restore()), .4)
            ul = prog(t, kq + .3, kq + .9)
            line(c, 120, 400, 120 + 560 * ul, 400, stroke('#d9382a', 10))


# ================================================================== SCENE 4
def s4a(c, t, T):
    with cam(c, 540, 900, 1.0 + .06 * prog(t, 24.4, 26), 0, t=t):
        city_sky(c, t, '#f1cf8e', '#d98f55')
        street(c, 1260)
        shop_front(c, 540, 1260, 520, 520, 'মিরপুর মোবাইল সার্ভিসিং', t, sign_size=40)
        for i, ch in enumerate((CUST1, CUST2, CUST3, CUST4)):
            t0 = 24.5 + i * .3
            u = prog(t, t0 - .4, t0 + 1.6)
            side = -1 if i % 2 == 0 else 1
            x = 540 + side * (900 * (1 - ease_out(u)) + 220 + (i // 2) * 130)
            walker(c, x, 1345 + (i % 2) * 40, 0.82, t + i * .3, ch, flip=(side > 0), speed=3.6)


def s4b(c, t, T):
    kA, kB, kC = T.s(18), T.s(19), T.s(20)
    cx = keys(t, [(25.4, 520), (kC, 560), (T.s(21), 600)], smooth)
    z = keys(t, [(25.4, 1.0), (kA, 1.12), (T.s(21), 1.2)], smooth)
    with cam(c, cx, 920, z, 0, t=t):
        shop_wall(c, t, wall=('#a9b36a', '#7e8a46'), floor='#5b4a38', clock_min=500 + t * .1, clock_x=860, clock_r=100, poster=True)
        # Zahid
        mz = T.mouth(t, 19) + T.mouth(t, 21) * .0
        emo = 'worried' if t > T.s(20) else 'neutral'
        person(c, 780, 1300, 1.45, **ZAHID, emo=emo, mouth=mz, t=t, armR=talk_arm(t, mz), look=(-.7, 0),
               tilt=-4 if t > T.s(21) else 0, seed=.2)
        counter(c, 420, 1240, 760)
        # customer enters then stands
        u = prog(t, 25.3, 26.4)
        x = lerp(-250, 230, ease_out(u))
        mc = max(T.mouth(t, 18), T.mouth(t, 20), T.mouth(t, 17) * .5)
        if u < 1:
            walker(c, x, 1400, 1.28, t, CUST1, speed=3.4, hold=hold_phone(), emo='neutral')
        else:
            ch = CUST1
            person(c, x, 1400, 1.28, **ch, emo='neutral' if t < T.s(20) else 'angry' if False else 'worried', mouth=mc, t=t, look=(.7, 0),
                   armR=(100, -172), armL=(-9, -6), hold=hold_phone(), seed=1.3)
        shadow_ellipse(c, x, 1400 + 205 * 1.28, 100, 20)
    # bubbles
    bubble_t = lambda i, d=0: (prog(t, T.s(i), T.s(i) + .25) * (1 - prog(t, T.e(i) + d, T.e(i) + d + .3)))
    bubble(c, 300, 640, 480, 130, 'ভাই, কতক্ষণ লাগবে?', tail=(110, 70), size=46, p=bubble_t(18, .5), t=t)
    bubble(c, 790, 520, 380, 120, 'হয়ে যাবে।', tail=(-100, 90), size=54, bg='#fff3c4', p=bubble_t(19, .4), t=t)
    bubble(c, 300, 640, 330, 130, 'কখন?', tail=(110, 70), size=62, p=bubble_t(20, .5), t=t)
    pq = prog(t, T.s(21) + .15, T.s(21) + .6) * (1 - prog(t, T.e(21), T.e(21) + .3))
    bubble(c, 790, 520, 270, 130, '...', tail=(-100, 90), size=70, bg='#fff3c4', p=pq, t=t, think=False)
    if t > T.s(21):
        pq = prog(t, T.s(21) + .6, T.s(21) + 1.0)
        question(c, 790, 400, 190, '#ffffff', pq, 12)


def s4c(c, t, T):
    t0 = T.s(22)
    cx = keys(t, [(t0 - .3, 330), (t0 + 2.4, 800)], smooth)
    with cam(c, cx, 900, 1.0, 0, t=t):
        city_sky(c, t, '#e6bd7d', '#cf8750', sun=False)
        street(c, 1260)
        shop_front(c, 100, 1260, 520, 520, 'মিরপুর মোবাইল সার্ভিসিং', t, sign_size=40, body='#a8472f')
        # big shop
        shop_front(c, 1030, 1260, 780, 760, 'মেগা মোবাইল শো-রুম', t, sign_size=56, body='#2f6b4f', sign_bg='#b8302a', sign_fg='#fff6df',
                   inside=lambda c, x, y, w, h: [phone(c, x + 90 + k * 110, y + 150 + (k % 2) * 90, 70, 130, 0, 'new', glow=0.0) for k in range(6)])
        for k in range(18):
            circle(c, 660 + k * 44, 560 + abs(math.sin(t * 3 + k)) * 0, 9, fill('#fff0b0' if (int(t * 4) + k) % 2 else '#ffcc55'))
        u = prog(t, t0 + .1, t0 + 2.2)
        x = lerp(130, 1010, smooth(u))
        if u < 1:
            walker(c, x, 1345, .85, t, CUST1, flip=True, speed=3.6, hold=hold_phone(pw=60, ph=110), emo='neutral')
        # Zahid watching sadly at his door
        person(c, 100, 1160, .62, **ZAHID, emo='sad', t=t, look=(1, 0), show_legs=False, armL=(-5, -5), armR=(5, 5))
    popup(c, t, T.s(23) + .1, lambda c, p: banner_text(c, 'বড় দোকান', 700, 300, 90, fg='#fff6df', bg='#b8302a', p=p, rot=-3), .4)


def scene4(c, t, T):
    phases(c, t, [lambda c, t_: s4a(c, t_, T), (25.45, .4, 'slide', lambda c, t_: s4b(c, t_, T)),
                  (T.s(22) - .15, .5, 'wipe', lambda c, t_: s4c(c, t_, T))])


# ================================================================== SCENE 5
def s5_room(c, t, clock_min, zoomed=False):
    shop_wall(c, t, wall=('#8a4a36', '#5e3226'), floor='#3a261e', clock_min=clock_min, clock_x=860, clock_r=100, poster=False)
    c.drawRect(skia.Rect.MakeLTRB(-500, -400, 1580, 1260), fill('#1a0d08', .25))
    c.drawPath(_cone(), grad(0, 46, 0, 900, '#ffd98a', '#ffd98a', 0.0))


def s5a(c, t, T):
    kx = T.s(24)
    z = keys(t, [(37.4, 1.0), (T.s(25), 1.1)])
    with cam(c, 560, 920, z, 0, t=t):
        s5_room(c, t, 1260 + t * .2)
        mz = T.mouth(t, 24) * 0
        person(c, 800, 1300, 1.45, **ZAHID, emo='neutral', t=t, look=(-.8, 0), armR=(10 + math.sin(t * 3) * 3, 6))
        counter(c, 460, 1240, 720, col='#5a3a28', top='#a98258')
        u = prog(t, 37.6, 38.9)
        x = lerp(-240, 250, ease_out(u))
        m = T.mouth(t, 24) * 0
        if u < 1:
            wp = walk_pose(t, 3.4)
            shadow_ellipse(c, x, 1400 + 175 * 1.2, 90, 18)
            person(c, x, 1400 + wp['bob'], 1.2, **GIRL, backpack=True, legs=wp['legs'], armL=wp['armL'], armR=(100, -172), t=t,
                   emo='worried', hold=hold_phone(pw=80, ph=150))
        else:
            shadow_ellipse(c, x, 1400 + 175 * 1.2, 90, 18)
            person(c, x, 1400, 1.2, **GIRL, backpack=True, emo='worried', t=t, look=(.8, 0), armL=(-8, -6), armR=(100, -172),
                   hold=hold_phone(pw=80, ph=150))


def s5b(c, t, T):
    k25, k26 = T.s(25), T.s(26)
    z = keys(t, [(k25 - .3, 1.0), (k26 - .1, 1.0), (k26 + .6, 1.0)])
    with cam(c, 540, 960, 1.0, 0, t=t):
        sky(c, '#f2c97e', '#d98b4b', -500, 1500)
        halftone(c, -100, -100, 1200, 1400, '#ffffff', .12, 46, 10)
        # desk
        c.drawRect(skia.Rect.MakeLTRB(-100, 1050, 1200, 1700), grad(0, 1050, 0, 1700, '#9c6a3f', '#6e4526'))
        # calendar
        pc = prog(t, k25 - .1, k25 + .45)
        c.save(); c.translate(300, 560); c.rotate(-5); s = back_out(pc); c.scale(s, s)
        rrect(c, -190, -230, 380, 440, 14, fill('#fff6df')); rrect(c, -190, -230, 380, 100, 14, fill('#b8302a'))
        draw_text(c, 'পরীক্ষা', 0, -160, 64, '#fff6df')
        draw_text(c, 'কাল', 0, 50, 150, '#b8302a')
        pc2 = prog(t, k25 + .4, k25 + .9)
        c.drawOval(skia.Rect.MakeLTRB(-150, -50 - 20, 150, 90 + 20), stroke('#2a1d17', 7, pc2))
        c.restore()
        # books
        for k, col in enumerate(('#e0b04a', '#7a8f3c', '#b8453a')):
            rrect(c, 580 + k * 6, 1000 - k * 60, 300 - k * 20, 56, 8, fill(col))
        # phone with notes + cracks
        pp = prog(t, k26 - .1, k26 + .5)
        c.save(); c.translate(760, 560); c.rotate(8 - (1 - pp) * 20); s = back_out(pp) * 1.0; c.scale(s * 1.5, s * 1.5)
        phone(c, 0, 0, 160, 300, 0, 'notes', cracks=True)
        c.restore()
        for k in range(8):
            ph = (t * .7 + k * .13) % 1
            sparkle(c, 700 + math.sin(k * 5) * 130, 760 - ph * 380, 7, '#fff3b0', 1 - ph)
        # ticking clock
        wall_clock(c, 200, 1250, 120, minutes=t * 3, sec=t * 1.0)
        label_tag(c, '২৪ ঘণ্টাও নেই!', 540, 220, 64, bg='#1a0f09', p=prog(t, k25 + .3, k25 + .8), rot=-2)


def s5c(c, t, T):
    k31, k32 = T.s(31), T.s(32)
    z = keys(t, [(T.s(27) - .3, 1.0), (T.s(30), 1.1), (k31, 1.3), (k32 + 1, 1.55)], smooth)
    cx = keys(t, [(T.s(27) - .3, 540), (k31, 440), (k32 + 1, 330)], smooth)
    with cam(c, cx, 900, z, 0, t=t):
        s5_room(c, t, 1380 + t * 2.5)
        mz = max(T.mouth(t, 29), 0)
        sw_ = t > T.s(30)
        person(c, 800, 1300, 1.45, **ZAHID, emo='worried' if t > T.s(30) else 'neutral', mouth=mz, t=t, look=(-.8, 0),
               armR=talk_arm(t, mz))
        counter(c, 460, 1240, 720, col='#5a3a28', top='#a98258')
        mg = max(T.mouth(t, 28), T.mouth(t, 31), T.mouth(t, 32), T.mouth(t, 33), T.mouth(t, 27) * .6)
        emo = 'worried' if t < T.s(30) else ('sad' if t < k31 else 'angry' if False else 'sad')
        shadow_ellipse(c, 250, 1400 + 175 * 1.2, 90, 18)
        person(c, 250, 1400, 1.2, **GIRL, backpack=True, emo=emo, mouth=mg, t=t, look=(.8, 0), armL=(-8, -6), armR=(100, -172),
               hold=hold_phone(pw=80, ph=150, screen='notes', cracks=True), tilt=-3 + math.sin(t) * 2)
    bt = lambda i, d=.3: prog(t, T.s(i), T.s(i) + .22) * (1 - prog(t, T.e(i) + d, T.e(i) + d + .3))
    bubble(c, 300, 600, 560, 130, 'আজ রাতের মধ্যে পাব?', tail=(120, 80), size=46, p=bt(28, .5), t=t)
    bubble(c, 760, 520, 380, 120, 'হয়ে যাবে।', tail=(-100, 90), size=54, bg='#fff3c4', p=bt(29, .4), t=t)
    # silence
    ps = prog(t, T.s(30) + .3, T.s(30) + .7) * (1 - prog(t, T.s(31) - .05, T.s(31) + .2))
    bubble(c, 300, 600, 250, 120, '...', tail=(120, 80), size=64, p=ps, t=t)
    bubble(c, 330, 520, 640, 200, 'হয়ে যাবে\nমানে কখন?', tail=(150, 80), size=60, p=prog(t, T.s(31), T.s(31) + .25) * (1 - prog(t, T.s(32) - .05, T.s(32) + .15)), t=t)
    # choice icons
    ch = prog(t, T.s(32) + .1, T.s(32) + .5)
    if ch > 0:
        c.save(); c.translate(540, 1000)
        s = back_out(ch); c.scale(s, s)
        rrect(c, -480, -90, 450, 180, 28, fill('#fff6df')); draw_text(c, 'অপেক্ষা?', -255, 22, 62, '#2a1d17')
        rrect(c, 30, -90, 450, 180, 28, fill('#b8302a')); draw_text(c, 'অন্য দোকান?', 255, 22, 56, '#fff6df')
        c.restore()


def scene5(c, t, T):
    phases(c, t, [lambda c, t_: s5a(c, t_, T), (T.s(25) - .25, .45, 'iris', lambda c, t_: s5b(c, t_, T)),
                  (T.s(27) - .3, .45, 'wipe', lambda c, t_: s5c(c, t_, T))])


SCENES = {1: scene1, 2: scene2, 3: scene3, 4: scene4, 5: scene5}
