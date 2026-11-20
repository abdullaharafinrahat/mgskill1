# -*- coding: utf-8 -*-
"""Vector drawing kit: characters, props, backgrounds, effects (Skia)."""
import math
import skia
from common import *
from textkit import draw_text, text_width


# ------------------------------------------------------------ basic helpers
def rrect(c, x, y, w, h, r, paint):
    c.drawRoundRect(skia.Rect.MakeXYWH(x, y, w, h), r, r, paint)


def circle(c, x, y, r, paint):
    c.drawCircle(x, y, r, paint)


def oval(c, cx, cy, rx, ry, paint):
    c.drawOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry), paint)


def line(c, x0, y0, x1, y1, paint):
    c.drawLine(x0, y0, x1, y1, paint)


def poly(c, pts, paint, close=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    c.drawPath(p, paint)


def shadow_ellipse(c, x, y, rx, ry, a=0.28):
    c.drawOval(skia.Rect.MakeLTRB(x - rx, y - ry, x + rx, y + ry), blur_paint('#000000', ry * 0.5, a))


class cam:
    """Context manager: apply a camera (centre, zoom, rotation) to world drawing."""

    def __init__(self, c, cx, cy, z=1.0, rot=0.0, shake=0.0, t=0.0):
        self.c, self.a = c, (cx, cy, z, rot, shake, t)

    def __enter__(self):
        cx, cy, z, rot, shake, t = self.a
        c = self.c
        c.save()
        c.translate(W / 2, H / 2)
        if shake:
            c.translate(noise(t * 3, 1) * shake, noise(t * 3, 5) * shake)
            c.rotate(noise(t * 2, 9) * shake * 0.03)
        c.rotate(rot)
        c.scale(z, z)
        c.translate(-cx, -cy)

    def __exit__(self, *a):
        self.c.restore()


def sky(c, c0, c1, y0=-600, y1=1400, x0=-800, x1=1900):
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1 + 1500), grad(0, y0, 0, y1, c0, c1))


def rays(c, cx, cy, t, col, a=0.18, n=14, r=2200):
    for i in range(n):
        a0 = (i / n) * 2 * math.pi + t * 0.15
        a1 = a0 + math.pi / n * 0.8
        poly(c, [(cx, cy), (cx + math.cos(a0) * r, cy + math.sin(a0) * r), (cx + math.cos(a1) * r, cy + math.sin(a1) * r)],
             fill(col, a))


def halftone(c, x0, y0, x1, y1, col, a=0.12, step=36, r=7):
    p = fill(col, a)
    j = 0
    y = y0
    while y < y1:
        x = x0 + (step / 2 if j % 2 else 0)
        while x < x1:
            c.drawCircle(x, y, r, p)
            x += step
        y += step * 0.86
        j += 1


# ------------------------------------------------------------ person
def _limb(c, p0, a1, l1, a2, l2, col1, col2, w1, w2):
    r1, r2 = math.radians(a1), math.radians(a2)
    p1 = (p0[0] + math.sin(r1) * l1, p0[1] + math.cos(r1) * l1)
    p2 = (p1[0] + math.sin(r2) * l2, p1[1] + math.cos(r2) * l2)
    c.drawLine(p0[0], p0[1], p1[0], p1[1], stroke(col1, w1))
    c.drawLine(p1[0], p1[1], p2[0], p2[1], stroke(col2, w2))
    return p1, p2


def person(c, x, y, s=1.0, *, skin='#c48a5a', hair='#1c1411', style='short', shirt='#7d8c3a', pants='#3a2f2b',
           flip=False, emo='neutral', mouth=0.0, look=(0, 0), armL=(-9, -6), armR=(9, 6), legs=(0, 0), lean=0,
           tilt=0, t=0.0, seed=0.0, beard=None, hold=None, holdL=None, bob=0.0, show_legs=True, uniform=False,
           backpack=False, accent='#e8d9b0', shoe='#241a16', alpha=1.0):
    """Draw a front-facing cartoon person. Origin = hip centre; head ~300px above."""
    c.save()
    c.translate(x, y + bob)
    c.scale(-s if flip else s, s)
    c.rotate(lean)
    skin_d = mix(skin, '#000000', 0.18)
    # legs
    if show_legs:
        for sx, sw in ((-30, legs[0]), (30, legs[1])):
            _limb(c, (sx, -6), sw, 100, sw * 0.4, 105, pants, pants, 46, 42)
            r1 = math.radians(sw); r2 = math.radians(sw * 0.4)
            fx = sx + math.sin(r1) * 100 + math.sin(r2) * 105
            fy = -6 + math.cos(r1) * 100 + math.cos(r2) * 105
            oval(c, fx + 10, fy + 6, 34, 15, fill(shoe))
    # backpack behind
    if backpack:
        rrect(c, -78, -235, 156, 190, 40, fill('#a8472f'))
        rrect(c, -78, -140, 156, 60, 24, fill('#8c3a26'))
    # torso
    body = skia.Path()
    body.moveTo(-60, 4); body.lineTo(-74, -170)
    body.quadTo(-76, -214, -34, -218); body.lineTo(34, -218)
    body.quadTo(76, -214, 74, -170); body.lineTo(60, 4); body.close()
    c.drawPath(body, fill(shirt))
    c.drawPath(body, stroke(mix(shirt, '#000000', 0.2), 3, 0.35))
    if uniform:   # white shirt + maroon pinafore
        poly(c, [(-66, 4), (-72, -120), (72, -120), (66, 4)], fill('#7d2f2f'))
        poly(c, [(-44, -120), (-30, -216), (-14, -216), (-22, -120)], fill('#7d2f2f'))
        poly(c, [(44, -120), (30, -216), (14, -216), (22, -120)], fill('#7d2f2f'))
        circle(c, 0, -140, 6, fill('#e8c98a'))
    else:
        for k in range(3):
            circle(c, 0, -150 + k * 42, 5, fill(mix(shirt, '#000000', 0.35)))
        rrect(c, 22, -170, 36, 40, 6, fill(mix(shirt, '#000000', 0.12)))
    # neck + collar
    rrect(c, -20, -250, 40, 50, 14, fill(skin_d))
    poly(c, [(-22, -222), (0, -190), (22, -222), (12, -226), (0, -210), (-12, -226)], fill(mix(shirt, '#ffffff', 0.25)))
    # arms
    for side, ang, hk in ((-1, armL, holdL), (1, armR, hold)):
        sh = (side * 62, -196)
        p1, p2 = _limb(c, sh, ang[0], 92, ang[1], 88, shirt, skin, 40, 30)
        circle(c, p1[0], p1[1], 20, fill(shirt))
        circle(c, p2[0], p2[1], 19, fill(skin))
        if hk:
            c.save(); c.translate(*p2); c.rotate(-ang[1]); hk(c); c.restore()
    # head
    c.save()
    c.translate(0, -230)
    c.rotate(tilt)
    c.translate(0, 230)
    hy = -298
    oval(c, -62, hy + 8, 13, 19, fill(skin_d)); oval(c, 62, hy + 8, 13, 19, fill(skin_d))
    oval(c, 0, hy, 62, 68, fill(skin))
    # hair
    hp = fill(hair)
    if style in ('short', 'pigtails', 'curly'):
        h = skia.Path()
        h.moveTo(-64, hy + 6); h.cubicTo(-80, hy - 110, 80, hy - 110, 64, hy + 6)
        h.quadTo(46, hy - 38, 0, hy - 44); h.quadTo(-46, hy - 38, -64, hy + 6)
        c.drawPath(h, hp)
        if style == 'curly':
            for k in range(-3, 4):
                circle(c, k * 19, hy - 56 + abs(k) * 5, 21, hp)
    if style == 'pigtails':
        for sx in (-1, 1):
            rrect(c, sx * 84 - 15, hy + 14, 30, 100, 15, hp)
            circle(c, sx * 70, hy + 6, 14, fill('#d94a3a'))
    if style == 'cap':
        h = skia.Path()
        h.moveTo(-66, hy - 22); h.cubicTo(-70, hy - 110, 70, hy - 110, 66, hy - 22); h.close()
        c.drawPath(h, fill('#efe9d6'))
        c.drawPath(h, stroke('#cfc6ac', 3))
        for k in range(-2, 3):
            circle(c, k * 22, hy - 54 + abs(k) * 4, 4, fill('#c9bd9a'))
    if style == 'bald':
        oval(c, -58, hy - 4, 8, 22, hp); oval(c, 58, hy - 4, 8, 22, hp)
    if style == 'bun':
        h = skia.Path()
        h.moveTo(-64, hy + 6); h.cubicTo(-80, hy - 110, 80, hy - 110, 64, hy + 6)
        h.quadTo(46, hy - 38, 0, hy - 44); h.quadTo(-46, hy - 38, -64, hy + 6)
        c.drawPath(h, hp); circle(c, 0, hy - 84, 24, hp)
    if beard == 'stubble':
        p = skia.Path(); p.moveTo(-58, hy + 12); p.quadTo(0, hy + 150, 58, hy + 12); p.quadTo(0, hy + 40, -58, hy + 12)
        c.drawPath(p, fill('#2a1d17', 0.45))
    if beard == 'white':
        p = skia.Path(); p.moveTo(-60, hy + 6); p.quadTo(0, hy + 170, 60, hy + 6); p.quadTo(0, hy + 40, -60, hy + 6)
        c.drawPath(p, fill('#e9e6df'))
    # face
    nose = fill(skin_d)
    oval(c, 0, hy + 14, 8, 6, nose)
    if beard in ('stubble', 'white') or style == 'curly':
        p = skia.Path(); p.moveTo(-22, hy + 30); p.quadTo(0, hy + 22, 22, hy + 30); p.quadTo(0, hy + 38, -22, hy + 30)
        c.drawPath(p, fill('#2a1d17' if beard != 'white' else '#d9d4c8'))
    # eyes
    blink = 0.12 if ((t + seed) % 3.4) < 0.13 else 1.0
    eyeh = {'surprised': 1.3, 'happy': 0.8, 'sad': 0.85, 'angry': 0.8}.get(emo, 1.0) * blink
    for sx in (-1, 1):
        ex, ey = sx * 25, hy - 4
        oval(c, ex, ey, 12.5, 14.5 * eyeh, fill('#ffffff'))
        circle_y = ey + look[1] * 4
        oval(c, ex + look[0] * 5, circle_y, 6.5, 7.5 * min(1, eyeh + .1), fill('#1a120f'))
        if eyeh > 0.5:
            circle(c, ex + look[0] * 5 + 2, circle_y - 2.5, 2, fill('#ffffff'))
    # brows
    bi, bo, br = {'worried': (-10, 6, -4), 'sad': (-12, 8, -2), 'angry': (10, -4, 2), 'happy': (0, -3, -10),
                  'surprised': (-4, -4, -14), 'think': (-3, 4, -4), 'neutral': (0, 0, 0)}.get(emo, (0, 0, 0))
    bp = stroke(hair if style != 'cap' else '#2a1d17', 8)
    for sx in (-1, 1):
        yo = hy - 34 + br
        line(c, sx * 40, yo - bo * .6 if emo != 'think' or sx < 0 else yo - 10, sx * 12, yo - bi * .6, bp)
    # mouth
    my = hy + 56
    if mouth > 0.06:
        hgt = 5 + 30 * mouth
        oval(c, 0, my + hgt * 0.3, 15 + 6 * mouth, hgt * 0.6 + 2, fill('#3b1814'))
        oval(c, 0, my + hgt * 0.55, 9, hgt * 0.22 + 1, fill('#c4584c'))
    elif emo in ('happy',):
        p = skia.Path(); p.moveTo(-22, my - 4); p.quadTo(0, my + 36, 22, my - 4); p.close()
        c.drawPath(p, fill('#3b1814')); oval(c, 0, my + 3, 15, 4, fill('#ffffff'))
    elif emo in ('worried', 'sad'):
        p = skia.Path(); p.moveTo(-16, my + 10); p.quadTo(0, my - 8, 16, my + 10)
        c.drawPath(p, stroke('#3b1814', 5))
    elif emo == 'surprised':
        oval(c, 0, my + 6, 11, 14, fill('#3b1814'))
    elif emo == 'angry':
        line(c, -14, my + 6, 14, my + 6, stroke('#3b1814', 6))
    elif emo == 'think':
        p = skia.Path(); p.moveTo(-14, my + 4); p.quadTo(8, my + 10, 18, my - 2)
        c.drawPath(p, stroke('#3b1814', 5))
    else:
        line(c, -13, my + 4, 13, my + 4, stroke('#3b1814', 5))
    # sweat
    if emo in ('worried', 'sad', 'surprised'):
        ph = (t * 0.9 + seed) % 1.0
        dy = ph * 70
        a = 1 - max(0, ph - .7) / .3
        p = skia.Path(); sx0, sy0 = 62, hy - 40 + dy
        p.moveTo(sx0, sy0 - 18); p.quadTo(sx0 + 14, sy0 + 2, sx0, sy0 + 10); p.quadTo(sx0 - 14, sy0 + 2, sx0, sy0 - 18)
        c.drawPath(p, fill('#bfe3f0', a))
    c.restore()
    c.restore()


# ------------------------------------------------------------ props
def phone(c, x, y, w=150, h=290, rot=0, screen='crack', t=0.0, glow=0.0, case='#2b2321', parts=False, cracks=False):
    c.save(); c.translate(x, y); c.rotate(rot)
    if glow:
        c.drawCircle(0, 0, max(w, h) * 0.75, blur_paint('#ffd36b', 30, glow))
    rrect(c, -w / 2, -h / 2, w, h, w * .16, fill(case))
    rrect(c, -w / 2 + 6, -h / 2 + 6, w - 12, h - 12, w * .12, fill('#101010'))
    sw, sh = w - 18, h - 20
    c.save()
    c.clipRRect(skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(-sw / 2, -sh / 2, sw, sh), w * .1, w * .1), doAntiAlias=True)
    full = skia.Rect.MakeXYWH(-sw / 2, -sh / 2, sw, sh)
    if screen == 'off':
        c.drawRect(full, fill('#1b1b1b'))
        poly(c, [(-sw / 2, -sh / 2), (sw / 2, -sh / 2), (-sw / 2, sh / 4)], fill('#ffffff', 0.05))
    if screen == 'crack':
        c.drawRect(full, grad(0, -sh / 2, 0, sh / 2, '#e9a24a', '#c4542f'))
    if screen == 'new':
        c.drawRect(full, grad(0, -sh / 2, 0, sh / 2, '#ffd36b', '#e0562f'))
        circle(c, 0, -sh * .08, sw * .22, fill('#fff3c4', 0.9))
        poly(c, [(-sw / 2, sh * .2), (-sw * .1, -sh * .02), (sw * .15, sh * .18), (sw * .32, sh * .06), (sw / 2, sh * .24),
                 (sw / 2, sh / 2), (-sw / 2, sh / 2)], fill('#7a2d1c'))
    if screen == 'notes':
        c.drawRect(full, fill('#f6efe0'))
        for k in range(9):
            wd = sw * (0.5 + 0.4 * ((k * 53) % 7) / 7)
            rrect(c, -sw / 2 + 12, -sh / 2 + 22 + k * (sh / 11), wd, 7, 3, fill('#5b4636' if k % 4 else '#c0392b', 0.8))
    if screen == 'open':
        c.drawRect(full, fill('#3a332f'))
        rrect(c, -sw * .36, -sh * .3, sw * .72, sh * .35, 8, fill('#2a8a4a'))
        for k in range(4):
            circle(c, -sw * .2 + k * sw * .13, sh * .22, 9, fill('#c9a85c'))
    if screen == 'crack' or cracks:
        cx0, cy0 = sw * .12, -sh * .12
        sp = stroke('#ffffff', 2.2, 0.9)
        for k in range(9):
            a = k * math.pi * 2 / 9 + 0.3
            ln = (0.3 + 0.35 * ((k * 37) % 10) / 10) * h
            pth = skia.Path(); pth.moveTo(cx0, cy0)
            pth.lineTo(cx0 + math.cos(a) * ln * .5, cy0 + math.sin(a) * ln * .5 + 6)
            pth.lineTo(cx0 + math.cos(a + .1) * ln, cy0 + math.sin(a + .1) * ln)
            c.drawPath(pth, sp)
        for rr in (28, 55):
            c.drawCircle(cx0, cy0, rr, stroke('#ffffff', 1.6, 0.6))
        if screen == 'crack':
            c.drawRect(full, fill('#000000', 0.18))
    c.restore()
    rrect(c, -w * .12, -h / 2 + 12, w * .24, 7, 3.5, fill('#000000', 0.6))
    c.restore()


def wall_clock(c, x, y, r, minutes=0.0, sec=0.0, tint='#6b4226', face='#f6ecd4', dust=False, glow=0.0, ring=None):
    if glow:
        c.drawCircle(x, y, r * 1.5, blur_paint('#ffe08a', r * .3, glow))
    c.drawCircle(x + r * .04, y + r * .06, r * 1.08, blur_paint('#000000', r * .08, 0.3))
    circle(c, x, y, r * 1.08, fill(tint))
    circle(c, x, y, r * 1.0, fill(mix(tint, '#ffffff', .22)))
    circle(c, x, y, r * .9, fill(face))
    if ring is not None:
        col, frac = ring
        oval_r = skia.Rect.MakeLTRB(x - r * .96, y - r * .96, x + r * .96, y + r * .96)
        c.drawArc(oval_r, -90, 360 * frac, False, stroke(col, r * .08, 1.0, skia.Paint.kButt_Cap))
    for k in range(60):
        a = k * math.pi / 30
        big = k % 5 == 0
        r0 = r * (.74 if big else .82)
        line(c, x + math.sin(a) * r0, y - math.cos(a) * r0, x + math.sin(a) * r * .87, y - math.cos(a) * r * .87,
             stroke('#3a2a1e', r * (.035 if big else .015)))
    mh = (minutes % 60) / 60 * 2 * math.pi
    hh = (minutes / 60 % 12) / 12 * 2 * math.pi
    line(c, x, y, x + math.sin(hh) * r * .5, y - math.cos(hh) * r * .5, stroke('#2a1c12', r * .07))
    line(c, x, y, x + math.sin(mh) * r * .75, y - math.cos(mh) * r * .75, stroke('#2a1c12', r * .05))
    sa = (sec % 60) / 60 * 2 * math.pi
    line(c, x - math.sin(sa) * r * .15, y + math.cos(sa) * r * .15, x + math.sin(sa) * r * .8, y - math.cos(sa) * r * .8,
         stroke('#c0392b', r * .02))
    circle(c, x, y, r * .06, fill('#c0392b'))
    if dust:
        for k in range(5):
            line(c, x - r * .9, y - r * .9 + k * 8, x - r * .45, y - r * .55 + k * 4, stroke('#ffffff', 1.5, .35))


def bubble(c, x, y, w, h, text, tail=(0, 60), size=46, bg='#ffffff', fg='#2a1d17', p=1.0, t=0.0, border='#2a1d17', think=False):
    """Speech bubble with pop-in. (x,y) = centre."""
    if p <= 0.01:
        return
    sc = back_out(p) if p < 1 else 1.0
    c.save(); c.translate(x, y); c.scale(sc, sc); c.translate(0, math.sin(t * 2.2) * 3)
    c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2 + 6, -h / 2 + 8, w, h), h / 2.4, h / 2.4, blur_paint('#000000', 8, 0.25))
    tx, ty = tail
    if think:
        for k, rr in enumerate((16, 11, 7)):
            circle(c, tx * (0.45 + k * .28) * .6 + 0, h / 2 + 20 + k * 26, rr, fill(bg))
    else:
        poly(c, [(tx * .5 - 26, h / 2 - 10), (tx, h / 2 + ty), (tx * .5 + 26, h / 2 - 10)], fill(bg))
    rrect(c, -w / 2, -h / 2, w, h, h / 2.4, fill(bg))
    if border:
        c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2, -h / 2, w, h), h / 2.4, h / 2.4, stroke(border, 4, 0.9))
    lines = text.split('\n')
    for i, ln in enumerate(lines):
        draw_text(c, ln, 0, size * 0.34 + (i - (len(lines) - 1) / 2) * size * 1.15, size, fg)
    c.restore()


def sparkle(c, x, y, r, col='#fff3b0', a=1.0, rot=0):
    c.save(); c.translate(x, y); c.rotate(rot)
    p = skia.Path()
    p.moveTo(0, -r); p.quadTo(r * .12, -r * .12, r, 0); p.quadTo(r * .12, r * .12, 0, r)
    p.quadTo(-r * .12, r * .12, -r, 0); p.quadTo(-r * .12, -r * .12, 0, -r)
    c.drawPath(p, fill(col, a)); c.restore()


def coin(c, x, y, r, rot=0):
    c.save(); c.translate(x, y); c.scale(abs(math.cos(rot)) * .8 + .2, 1)
    circle(c, 0, 0, r, fill('#e9b83a')); circle(c, 0, 0, r * .78, stroke('#b98a1c', r * .12))
    draw_text(c, '৳', 0, r * .35, r * 1.0, '#a8760f')
    c.restore()


def stopwatch(c, x, y, r, t_frac=0.0, col='#d9822b', hand='#2a1d17', face='#fff6df'):
    rrect(c, x - r * .16, y - r * 1.38, r * .32, r * .3, 5, fill('#5b4636'))
    circle(c, x, y, r * 1.08, fill(col)); circle(c, x, y, r * .92, fill(face))
    for k in range(12):
        a = k * math.pi / 6
        line(c, x + math.sin(a) * r * .72, y - math.cos(a) * r * .72, x + math.sin(a) * r * .84, y - math.cos(a) * r * .84,
             stroke('#3a2a1e', r * .04))
    a = t_frac * 2 * math.pi
    c.drawArc(skia.Rect.MakeLTRB(x - r * .6, y - r * .6, x + r * .6, y + r * .6), -90, t_frac * 360, False,
              stroke('#c0392b', r * .1, 1.0, skia.Paint.kButt_Cap))
    line(c, x, y, x + math.sin(a) * r * .74, y - math.cos(a) * r * .74, stroke(hand, r * .06))
    circle(c, x, y, r * .07, fill(hand))


def banner_text(c, text, cx, cy, size, fg='#fff7e0', bg='#b8302a', pad=34, rot=0, p=1.0, border='#fff7e0'):
    w = text_width(text, size) + pad * 2
    h = size * 1.55
    c.save(); c.translate(cx, cy); c.rotate(rot)
    s = back_out(p); c.scale(s, s)
    c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2 + 6, -h / 2 + 10, w, h), 18, 18, blur_paint('#000000', 8, .35))
    rrect(c, -w / 2, -h / 2, w, h, 18, fill(bg))
    if border:
        c.drawRoundRect(skia.Rect.MakeXYWH(-w / 2 + 8, -h / 2 + 8, w - 16, h - 16), 12, 12, stroke(border, 3, .8))
    draw_text(c, text, 0, size * .34, size, fg)
    c.restore()
    return w


def checkmark(c, x, y, r, col='#2f9e55', p=1.0, wd=None):
    wd = wd or r * .28
    pth = skia.Path()
    pts = [(x - r * .55, y), (x - r * .12, y + r * .45), (x + r * .6, y - r * .5)]
    pth.moveTo(*pts[0])
    if p < .5:
        u = p / .5
        pth.lineTo(pts[0][0] + (pts[1][0] - pts[0][0]) * u, pts[0][1] + (pts[1][1] - pts[0][1]) * u)
    else:
        u = (p - .5) / .5
        pth.lineTo(*pts[1])
        pth.lineTo(pts[1][0] + (pts[2][0] - pts[1][0]) * u, pts[1][1] + (pts[2][1] - pts[1][1]) * u)
    c.drawPath(pth, stroke(col, wd))


def cross(c, x, y, r, col='#c0392b', p=1.0, wd=None):
    wd = wd or r * .28
    if p > 0:
        u = min(1, p / .5)
        line(c, x - r, y - r, x - r + 2 * r * u, y - r + 2 * r * u, stroke(col, wd))
    if p > .5:
        u = (p - .5) / .5
        line(c, x + r, y - r, x + r - 2 * r * u, y - r + 2 * r * u, stroke(col, wd))


def question(c, x, y, size, col='#ffffff', p=1.0, rot=0, outline='#3a1d12'):
    c.save(); c.translate(x, y); c.rotate(rot); s = back_out(p); c.scale(s, s)
    draw_text(c, '?', 0, size * .36, size, col, outline=outline, outline_w=size * .12)
    c.restore()


# ------------------------------------------------------------ shop pieces
def shop_wall(c, t, wall=('#e2b36b', '#c58a4a'), floor='#6e4a31', clock_min=None, with_clock=True, clock_x=860,
              clock_r=100, poster=True, lamp=True, shelf_col='#8a5a35', x0=-500, x1=1580, ceil='#f3e3bd'):
    c.drawRect(skia.Rect.MakeLTRB(x0, -400, x1, 1260), grad(0, -400, 0, 1260, wall[0], wall[1]))
    # wainscot
    c.drawRect(skia.Rect.MakeLTRB(x0, 900, x1, 1260), fill(mix(wall[1], '#000000', .18)))
    c.drawRect(skia.Rect.MakeLTRB(x0, 896, x1, 910), fill(mix(wall[1], '#ffffff', .15)))
    c.drawRect(skia.Rect.MakeLTRB(x0, 1260, x1, 2400), grad(0, 1260, 0, 2400, floor, mix(floor, '#000000', .35)))
    for k in range(-6, 14):
        line(c, 540 + (k * 170 - 540) * 1.0, 1260, 540 + (k * 420 - 540 * 4) * 1.0, 2400, stroke(mix(floor, '#000000', .3), 3, .5))
    # shelves with phone boxes
    for sy in (330, 560):
        c.drawRect(skia.Rect.MakeLTRB(x0 + 400, sy, 700, sy + 18), fill(shelf_col))
        for k in range(8):
            bx = -60 + k * 74
            bh = 70 + (k * 29) % 36
            rrect(c, bx, sy - bh, 60, bh, 5, fill(['#c9573b', '#e0b04a', '#7a8f3c', '#f2e6cc', '#a8472f'][k % 5]))
            c.drawRect(skia.Rect.MakeXYWH(bx + 6, sy - bh + 8, 48, 6), fill('#ffffff', .4))
    if poster:
        rrect(c, 130, 200, 230, 310, 10, fill('#f6efe0'))
        rrect(c, 146, 216, 198, 130, 8, fill('#d9822b'))
        phone(c, 245, 280, 62, 110, 0, 'new')
        for k in range(4):
            rrect(c, 150, 366 + k * 30, 190 - k * 24, 10, 5, fill('#5b4636', .7))
    if with_clock:
        wall_clock(c, clock_x, 420, clock_r, minutes=(clock_min if clock_min is not None else (t * 1.4)), sec=t)
    if lamp:
        rrect(c, 120, 20, 840, 26, 10, fill('#fffbe6'))
        c.drawRect(skia.Rect.MakeLTRB(120, 46, 960, 700), grad(0, 46, 0, 700, '#fff2b8', '#fff2b8', 0.0))
        c.drawPath(_cone(), grad(0, 46, 0, 800, '#fff4c0', '#fff4c0', 0.0))


def _cone():
    p = skia.Path(); p.moveTo(160, 46); p.lineTo(920, 46); p.lineTo(1100, 900); p.lineTo(-20, 900); p.close()
    return p


def counter(c, x, y, w, col='#7a4b2a', top='#d2a56b', glass=True, items=True, t=0.0):
    """Counter: top surface at y. Front panel below."""
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, 340), grad(0, y, 0, y + 340, col, mix(col, '#000000', .35)))
    for k in range(int(w // 170) + 1):
        rrect(c, x + 22 + k * 170, y + 50, 140, 240, 10, stroke(mix(col, '#000000', .4), 5))
    c.drawRect(skia.Rect.MakeXYWH(x - 14, y - 22, w + 28, 36), fill(top))
    c.drawRect(skia.Rect.MakeXYWH(x - 14, y + 8, w + 28, 8), fill(mix(top, '#000000', .25)))
    if glass:
        rrect(c, x + 30, y - 120, 200, 100, 8, fill('#dfeee8', .35))
        c.drawRoundRect(skia.Rect.MakeXYWH(x + 30, y - 120, 200, 100), 8, 8, stroke('#ffffff', 3, .6))


def shutter(c, x, y, w, h, down, col='#8e8a80'):
    """Rolling shutter covering fraction `down` (0..1) of area from the top."""
    hh = h * down
    if hh < 2:
        return
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, hh), grad(0, y, 0, y + hh, mix(col, '#ffffff', .15), mix(col, '#000000', .1)))
    k = 0
    while k * 26 < hh:
        c.drawRect(skia.Rect.MakeXYWH(x, y + k * 26, w, 3), fill('#000000', .22))
        k += 1
    rrect(c, x, y + hh - 16, w, 20, 6, fill(mix(col, '#000000', .35)))
    circle(c, x + w / 2, y + hh - 6, 9, fill('#d9c27a'))


def building(c, x, y, w, h, col, win=True, t=0.0, seed=0, lit=0.5):
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, h), fill(col))
    c.drawRect(skia.Rect.MakeXYWH(x, y, w, 14), fill(mix(col, '#000000', .25)))
    if win:
        cols = max(1, int(w // 90)); rows = max(1, int(h // 150))
        for i in range(cols):
            for j in range(rows):
                on = ((i * 7 + j * 13 + seed * 5) % 10) / 10 < lit
                rrect(c, x + 20 + i * (w - 40) / cols, y + 40 + j * 150, (w - 40) / cols - 22, 90, 6,
                      fill('#ffd98a' if on else mix(col, '#000000', .35)))


def label_tag(c, text, x, y, size=44, bg='#2a1d17', fg='#ffe9a8', p=1.0, rot=0):
    if p <= 0:
        return
    return banner_text(c, text, x, y, size, fg=fg, bg=bg, pad=30, rot=rot, p=p, border=None)


def burst(c, x, y, p, col='#ffe08a', n=10, r0=40, r1=220):
    if p <= 0 or p >= 1:
        return
    for k in range(n):
        a = k * 2 * math.pi / n
        d0 = r0 + (r1 - r0) * ease_out(p); d1 = d0 + 40 * (1 - p)
        line(c, x + math.cos(a) * d0, y + math.sin(a) * d0, x + math.cos(a) * d1, y + math.sin(a) * d1, stroke(col, 8 * (1 - p), 1 - p))


def vignette(c, a=0.45):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial((W / 2, H / 2), 1250, [C('#000000', 0), C('#1a0d05', a)], [0.55, 1.0]))
    c.drawRect(skia.Rect.MakeWH(W, H), p)


def screen_fade(c, a, col='#000000'):
    if a > 0.001:
        c.drawRect(skia.Rect.MakeWH(W, H), fill(col, a))
