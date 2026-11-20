# -*- coding: utf-8 -*-
"""Scene helpers: characters, walking, phase transitions."""
import math
import skia
from common import *
from gfx import *

ZAHID = dict(skin='#bf8456', hair='#1c1411', style='short', shirt='#7d8c3a', pants='#3a2f2b', beard='stubble')
GIRL = dict(skin='#d6a077', hair='#1c1411', style='pigtails', shirt='#f4efe4', pants='#5a2a24', uniform=True)
CUST1 = dict(skin='#a86e45', hair='#2a1d17', style='bald', shirt='#c9573b', pants='#3d3a33')
CUST2 = dict(skin='#d2995f', hair='#1c1411', style='curly', shirt='#e0b04a', pants='#4a3b30')
CUST3 = dict(skin='#c58f62', hair='#1c1411', style='cap', shirt='#6e8f5b', pants='#44382e', beard='white')
CUST4 = dict(skin='#b57a4e', hair='#1c1411', style='short', shirt='#d98a3a', pants='#33302c')
CUST5 = dict(skin='#dba97e', hair='#3a2418', style='bun', shirt='#b8453a', pants='#4a3a33')
CUST6 = dict(skin='#9a6440', hair='#1c1411', style='short', shirt='#8c6a4a', pants='#2f2b28', beard='stubble')
CROWD = [CUST1, CUST2, CUST3, CUST4, CUST5, CUST6]


def walk_pose(t, speed=3.2, amp=26):
    ph = t * speed * math.pi
    return dict(legs=(math.sin(ph) * amp, -math.sin(ph) * amp), bob=-abs(math.sin(ph)) * 7,
                armL=(-10 + math.sin(ph) * 22, -10 + math.sin(ph) * 14), armR=(10 - math.sin(ph) * 22, 10 - math.sin(ph) * 14))


def talk_arm(t, m, base=(10, 6), k=1.0):
    """Gesturing right arm while speaking."""
    a = math.sin(t * 6.1) * 18 * m * k
    return (base[0] + 25 * m * k + a, base[1] + 55 * m * k - a * .6)


def phases(c, t, plist):
    """plist=[fn0,(t1,dur,kind,fn1),(t2,dur,kind,fn2)...]; fn(c,t). Transitions centred on t_i."""
    idx = 0
    for i in range(1, len(plist)):
        if t >= plist[i][0] - plist[i][1] / 2:
            idx = i
    if idx == 0:
        plist[0](c, t)
        return
    t_i, dur, kind, fn = plist[idx]
    prev = plist[idx - 1] if idx - 1 == 0 else plist[idx - 1][3]
    p = (t - (t_i - dur / 2)) / dur
    if p >= 1:
        fn(c, t)
        return
    prev(c, t)
    e = ease_io(p)
    c.save()
    if kind == 'iris':
        path = skia.Path(); path.addCircle(W / 2, H * .5, e * 1700)
        c.clipPath(path, doAntiAlias=True)
    elif kind == 'slide':
        c.translate(W * (1 - e), 0); c.clipRect(skia.Rect.MakeWH(W, H))
    elif kind == 'up':
        c.translate(0, H * (1 - e)); c.clipRect(skia.Rect.MakeWH(W, H))
    elif kind == 'wipe':
        path = skia.Path(); x0 = -300 + e * (W + 600)
        path.moveTo(0, 0); path.lineTo(x0 + 300, 0); path.lineTo(x0, H); path.lineTo(0, H); path.close()
        c.clipPath(path, doAntiAlias=True)
    fn(c, t)
    c.restore()
    if kind == 'iris':
        c.drawCircle(W / 2, H * .5, e * 1700, stroke('#ffe9b0', 8 * (1 - e) + 1, 0.7 * (1 - p)))


def popup(c, t, t0, fn, dur=0.4, out=None):
    """Call fn(c, p) with pop progress p; hides before t0 and after out."""
    if t < t0 or (out is not None and t > out):
        return
    p = prog(t, t0, t0 + dur)
    if out is not None:
        p = min(p, 1 - prog(t, out - 0.25, out))
    fn(c, p)


def float_y(t, a=8, sp=2.0, ph=0.0):
    return math.sin(t * sp + ph) * a
