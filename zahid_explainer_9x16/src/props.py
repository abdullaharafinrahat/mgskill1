import math, numpy as np
from PIL import Image, ImageDraw
from engine import *
WHITE = (255, 255, 255); CREAM = (250, 240, 220); SAND = (238, 214, 170); TEAL = (36, 120, 130); DTEAL = (20, 70, 84)
MUST = (246, 190, 62); CORAL = (238, 100, 84); NAVY = (26, 34, 78); LILAC = (120, 100, 190); MINT = (150, 214, 180)
NIGHT = (16, 20, 48); RED = (226, 60, 60); GREEN = (60, 170, 100); GRAY = (150, 150, 165); DAWN = (255, 176, 120)
def bn(n): return str(n).translate(str.maketrans('0123456789', '০১২৩৪৫৬৭৮৯'))
def paste_text(p, t, cx, cy):
    p.im.alpha_composite(t, (int(cx * 2 - t.width / 2), int(cy * 2 - t.height / 2)))
def b_shop(kind='small'):
    if kind == 'big':
        p = Pen(320, 600); p.rr((20, 40, 300, 590), (70, 82, 120), 10)
        for r in range(8):
            for c in range(4): p.rr((40 + c * 62, 70 + r * 46, 84 + c * 62, 98 + r * 46), (255, 230, 140) if (r + c) % 3 else (150, 190, 235), 3, 2)
        p.rr((30, 372, 290, 418), (255, 70, 150), 10); paste_text(p, text_img('মেগা মোবাইল হাব', 24, WHITE, 0), 160, 395)
        p.rr((60, 440, 260, 590), (170, 220, 245), 6); p.d.line([(160 * 2, 440 * 2), (160 * 2, 590 * 2)], fill=INK, width=6)
        p.rr((20, 30, 300, 50), (255, 70, 150), 6); return p.done()
    dim = kind == 'smalldim'
    wall = (170, 140, 100) if dim else (222, 172, 108); aw = ((120, 90, 90), (170, 160, 150)) if dim else ((226, 70, 70), WHITE)
    p = Pen(380, 330); p.rr((20, 70, 360, 322), wall, 6)
    for i in range(8):
        x0 = 14 + i * 44; p.poly([(x0, 96), (x0 + 44, 96), (x0 + 48, 46), (x0 + 4, 46)] if False else [(x0, 100), (x0 + 44, 100), (x0 + 40, 56), (x0 + 4, 56)], aw[i % 2], 2)
    p.rr((50, 6, 330, 52), (60, 70, 100) if dim else NAVY, 8); paste_text(p, text_img('মোবাইল সার্ভিস', 30, (200, 200, 210) if dim else (255, 236, 150), 0), 190, 29)
    p.rr((40, 120, 170, 290), (140, 150, 170) if dim else (170, 220, 245), 4)
    for i in range(3): p.rr((54 + i * 38, 190, 78 + i * 38, 240), (50, 54, 76), 4, 2)
    p.rr((210, 120, 340, 322), (60, 40, 40) if dim else (255, 214, 120), 4)
    return p.done()
def b_shutter(w=300, h=210, q=1.0):
    p = Pen(w + 8, h + 8); hh = int(h * q)
    if hh > 6:
        p.rr((4, 4, 4 + w, 4 + hh), (170, 176, 190), 3)
        for y in range(4 + 14, 4 + hh, 14): p.d.line([(4 * 2, y * 2), ((4 + w) * 2, y * 2)], fill=INK, width=3)
        p.rr((4 + w / 2 - 22, 4 + hh - 12, 4 + w / 2 + 22, 4 + hh - 4), (90, 94, 110), 3, 2)
    return p.done()
def b_poster(txt, size=40, strike=0.0, reveal=1.0, col=INK, bg=(255, 244, 214), pw=0):
    t = text_img(txt, size, col, 0); tw, th = t.width / 2, t.height / 2
    w, h = max(tw + 60, pw), th + 56; p = Pen(w + 20, h + 60)
    p.cap([(60, 30), (w / 2 + 10, 4)], 2.5, (120, 90, 60), 1.5); p.cap([(w - 40, 30), (w / 2 + 10, 4)], 2.5, (120, 90, 60), 1.5)
    p.rr((10, 30, 10 + w, 30 + h), bg, 10)
    p.rr((18, 38, 2 + w, 22 + h), None, 6, 0); p.d.rounded_rectangle([20 * 2, 40 * 2, (w) * 2, (28 + h - 12) * 2], 8, outline=(226, 70, 70), width=5)
    if reveal < 1: t = t.crop((0, 0, max(1, int(t.width * reveal)), t.height))
    p.im.alpha_composite(t, (int((10 + w / 2) * 2 - tw), int((30 + h / 2) * 2 - th)))
    if strike > 0:
        x0 = (10 + w / 2) * 2 - tw - 20; x1 = (10 + w / 2) * 2 + tw + 20; y = (30 + h / 2) * 2
        for dy, ww in ((0, 12), (th * .9, 12)):
            p.d.line([(x0, y - th * .45 + dy * .5), (x0 + (x1 - x0) * strike, y - th * .45 + dy * .5 - 10 * strike)], fill=(226, 40, 40), width=ww)
    return p.done()
VALS = [44, 47, 50, 41, 46, 48, 40, 45, 49, 43]
def b_bars(prog=1.0, hi=0):
    p = Pen(680, 560); p.rr((4, 4, 676, 556), CREAM, 18)
    for v in range(0, 61, 10):
        y = 500 - v / 60 * 420
        p.d.line([(70 * 2, y * 2), (660 * 2, y * 2)], fill=(200, 190, 170) if v else INK, width=3 if v else 7)
        paste_text(p, text_img(bn(v), 22, (90, 80, 70), 0), 40, y)
    for i, v in enumerate(VALS):
        r = eo(cl((prog * 12 - i) / 2)); hgt = v / 60 * 420 * r
        col = (220, 190, 120)
        if hi == 1 and i == 2: col = CORAL
        if hi == 2 and i == 6: col = TEAL
        if hi == 0: col = MUST
        if hgt > 1: p.rr((90 + i * 54, 500 - hgt, 90 + i * 54 + 38, 500), col, 4, 2)
    return p.done()
def b_cal(top='', big='', col=RED, w=200, h=230):
    p = Pen(w + 16, h + 16); p.rr((8, 14, 8 + w, 14 + h), WHITE, 12); p.rr((8, 14, 8 + w, 62), col, 12); p.rr((8, 50, 8 + w, 62), col, 0, 0)
    for x in (50, w - 34): p.rr((x, 4, x + 12, 34), (210, 210, 220), 5, 2)
    paste_text(p, text_img(top, 28, WHITE, 0), 8 + w / 2, 40)
    paste_text(p, text_img(big, 80, INK, 0), 8 + w / 2, 14 + h * .65); return p.done()
TIMES = ['১০:০০ – ১০:৪৫', '১১:০০ – ১১:৫০', '১২:১০ – ১২:৫০', '০২:০০ – ০২:৪৪', '০৩:০০ – ০৩:৪৮']
def b_notebook(n=0):
    p = Pen(320, 440); p.rr((10, 10, 310, 430), (255, 252, 240), 10); p.d.line([(60 * 2, 14 * 2), (60 * 2, 426 * 2)], fill=(240, 120, 120), width=4)
    for y in range(60, 420, 38): p.d.line([(16 * 2, y * 2), (304 * 2, y * 2)], fill=(190, 205, 230), width=3)
    for i in range(min(n, 5)): paste_text(p, text_img(TIMES[i], 25, (30, 40, 120), 0), 190, 50 + i * 38)
    for y in (90, 190, 290): p.ell((22, y, 40, y + 18), (200, 200, 210), 2)
    return p.done()
def b_book(title='Tested\nAdvertising\nMethods', col=(200, 50, 60), open_=0.0):
    p = Pen(260, 340); p.rr((14, 14, 246, 326), col, 10); p.rr((14, 14, 34, 326), tuple(int(v * .7) for v in col), 6)
    p.rr((52, 40, 230, 150), (250, 236, 200), 6, 2)
    paste_text(p, text_img(title, 26, INK, 0, lead=1.15), 141, 95)
    paste_text(p, text_img('John Caples', 22, (255, 236, 160), 0), 141, 230); p.rr((100, 270, 186, 280), MUST, 3, 0); return p.done()
def b_balloon(text='', col=CORAL, pop=0):
    p = Pen(200, 300); 
    p.cap([(100, 215), (92, 250), (108, 280), (100, 296)], 1.8, INK, 0)
    p.poly([(100, 206), (88, 224), (112, 224)], col, 2); p.ell((20, 10, 180, 215), col, 3)
    p.ell((40, 34, 66, 76), tuple(min(255, v + 70) for v in col), 0)
    paste_text(p, text_img(text, 38, WHITE, 3), 100, 112); return p.done()
def b_tag(half=0, text='চার্জ', col=MUST):
    p = Pen(260, 150); p.poly([(10, 75), (50, 15), (250, 15), (250, 135), (50, 135)], col, 3); p.ell((34, 66, 54, 86), CREAM, 2.5)
    paste_text(p, text_img(text, 44, INK, 0), 150, 76); im = p.done()
    if half == 1: im.paste((0, 0, 0, 0), (im.width // 2, 0, im.width, im.height))
    if half == 2: im.paste((0, 0, 0, 0), (0, 0, im.width // 2, im.height))
    return im
def b_stopw(a=0, r=70, red=0):
    p = Pen(2 * r + 30, 2 * r + 40); c = r + 15; cy = r + 30
    p.rr((c - 9, 4, c + 9, 24), (150, 150, 165), 3); p.rr((c - 26, 0, c + 26, 8), (150, 150, 165), 3, 2)
    p.ell((c - r, cy - r, c + r, cy + r), (230, 60, 60) if red else (60, 70, 100), 4); p.ell((c - r + 10, cy - r + 10, c + r - 10, cy + r - 10), WHITE, 3)
    for i in range(60):
        ang = math.radians(i * 6); L = 9 if i % 5 == 0 else 4
        p.cap([(c + math.sin(ang) * (r - 14), cy - math.cos(ang) * (r - 14)), (c + math.sin(ang) * (r - 14 - L), cy - math.cos(ang) * (r - 14 - L))], 1.4, INK)
    ang = math.radians(a); p.line([(c, cy), (c + math.sin(ang) * (r - 20), cy - math.cos(ang) * (r - 20))], 3.5, RED, 1.5); p.ell((c - 6, cy - 6, c + 6, cy + 6), INK, 0)
    return p.done()
def b_sign(l='অপেক্ষা', r='অন্য দোকান'):
    p = Pen(560, 440); p.rr((268, 40, 292, 430), (150, 110, 70), 4)
    p.poly([(20, 70), (240, 70), (270, 100), (240, 130), (20, 130)], GREEN, 3); p.poly([(540, 200), (320, 200), (290, 230), (320, 260), (540, 260)], CORAL, 3)
    paste_text(p, text_img(l, 34, WHITE, 3), 130, 100); paste_text(p, text_img(r, 34, WHITE, 3), 420, 230)
    p.ell((250, 22, 310, 52), (150, 110, 70), 3); return p.done()
def b_sun(r=90): p = Pen(2 * r + 8, 2 * r + 8); p.ell((4, 4, 4 + 2 * r, 4 + 2 * r), (255, 214, 90), 0); return p.done()
def b_rays(r=260, n=14):
    p = Pen(2 * r, 2 * r)
    for i in range(n):
        a0 = math.radians(i * 360 / n); a1 = a0 + math.radians(360 / n / 2.4)
        p.d.polygon([(r * 2, r * 2), (r * 2 + math.cos(a0) * r * 2, r * 2 + math.sin(a0) * r * 2), (r * 2 + math.cos(a1) * r * 2, r * 2 + math.sin(a1) * r * 2)], fill=(255, 255, 255, 60))
    return p.done()
def b_moon(r=60):
    p = Pen(2 * r + 10, 2 * r + 10); p.ell((5, 5, 5 + 2 * r, 5 + 2 * r), (250, 244, 200), 0)
    p.ell((5 + r * .5, 5 - r * .1, 5 + 2.2 * r, 5 + 1.7 * r), None, 0); p.d.ellipse([(5 + r * .6) * 2, (5 - r * .05) * 2, (5 + 2.3 * r) * 2, (5 + 1.75 * r) * 2], fill=(0, 0, 0, 0)); return p.done()
def b_bulb():
    p = Pen(120, 160); p.ell((25, 10, 95, 80), (255, 226, 90), 3); p.poly([(40, 70), (80, 70), (74, 100), (46, 100)], (255, 226, 90), 3); p.rr((44, 100, 76, 120), GRAY, 3); p.rr((50, 120, 70, 132), GRAY, 3); return p.done()
def b_cloud(col=(90, 96, 130), w=300):
    p = Pen(w + 20, 150)
    for (x, y, r) in ((60, 80, 46), (120, 56, 56), (190, 70, 50), (240, 90, 38)): p.ell((x - r, y - r + 20, x + r, y + r + 20), col, 3)
    p.rr((40, 90, 270, 125), col, 14, 0); return p.done()
def b_bolt(): p = Pen(80, 200); p.poly([(50, 4), (10, 100), (38, 100), (22, 196), (72, 80), (42, 80)], (255, 230, 80), 3); return p.done()
def b_burst(col=MUST, r=90, n=10):
    p = Pen(2 * r + 10, 2 * r + 10); pts = []
    for i in range(n * 2):
        a = i * math.pi / n; rr_ = r if i % 2 == 0 else r * .5; pts.append((r + 5 + math.cos(a) * rr_, r + 5 + math.sin(a) * rr_))
    p.poly(pts, col, 3); return p.done()
def b_coin(face=0, r=80):
    p = Pen(2 * r + 12, 2 * r + 12); col = (170, 175, 190) if face == 0 else (255, 205, 60)
    p.ell((6, 6, 6 + 2 * r, 6 + 2 * r), col, 4); p.ell((6 + 12, 6 + 12, 6 + 2 * r - 12, 6 + 2 * r - 12), tuple(int(v * .88) for v in col), 2)
    if face: paste_text(p, text_img('৳', 78, INK, 0), r + 6, r + 6)
    else: p.cap([(r - 24, r - 24 + 12), (r + 36, r + 36 + 12)], 8, (90, 90, 110), 0); p.cap([(r + 36, r - 24 + 12), (r - 24, r + 36 + 12)], 8, (90, 90, 110), 0)
    return p.done()
def b_check(col=GREEN, w=70): p = Pen(w, w); p.cap([(w * .15, w * .55), (w * .4, w * .8), (w * .86, w * .22)], w * .14, col, 2); return p.done()
def b_cross(col=RED, w=70): p = Pen(w, w); p.cap([(w * .2, w * .2), (w * .8, w * .8)], w * .13, col, 2); p.cap([(w * .8, w * .2), (w * .2, w * .8)], w * .13, col, 2); return p.done()
def b_wrench(): p = Pen(160, 60); p.line([(30, 30), (130, 30)], 16, (170, 176, 190), 3); p.ell((6, 8, 52, 52), (170, 176, 190), 3); p.rr((8, 22, 30, 38), None, 0, 0); p.d.rectangle([8 * 2, 24 * 2, 28 * 2, 36 * 2], fill=(0, 0, 0, 0)); return p.done()
def b_broom(): p = Pen(80, 220); p.line([(40, 10), (40, 130)], 8, (170, 120, 70), 2.5); p.poly([(18, 128), (62, 128), (74, 210), (6, 210)], MUST, 3); return p.done()
def b_card(text, w=200, h=90, col=CORAL, size=34, tc=WHITE):
    p = Pen(w + 8, h + 8); p.rr((4, 4, 4 + w, 4 + h), col, 14); paste_text(p, text_img(text, size, tc, 0), 4 + w / 2, 4 + h / 2); return p.done()
def b_map():
    p = Pen(640, 820); p.rr((4, 4, 636, 816), (232, 238, 214), 14)
    for (x0, y0, x1, y1, c) in ((30, 40, 280, 230, (210, 224, 190)), (320, 40, 610, 190, (240, 226, 200)), (30, 270, 250, 520, (240, 226, 200)), (300, 250, 610, 500, (210, 224, 190)), (30, 560, 330, 790, (240, 226, 200)), (370, 540, 610, 790, (210, 224, 190))): p.rr((x0, y0, x1, y1), c, 10, 2)
    p.cap([(0, 500), (200, 540), (330, 520), (460, 530), (640, 480)], 26, (150, 200, 235), 3)
    for x in (300, 350): p.d.line([(x * 2, 0), (x * 2, 1640)], fill=(255, 255, 255), width=14)
    return p.done()
def b_pin(): p = Pen(80, 120); p.poly([(40, 112), (8, 52), (72, 52)], RED, 3); p.ell((6, 6, 74, 74), RED, 3); p.ell((26, 26, 54, 54), WHITE, 2); return p.done()
def b_spot(r=100, a=190):
    S = 800; yy, xx = np.mgrid[0:S, 0:S].astype(np.float32); d = np.sqrt((xx - S / 2) ** 2 + (yy - S / 2) ** 2)
    al = np.clip((d - r * 2) / 90, 0, 1) * a
    arr = np.zeros((S, S, 4), np.uint8); arr[..., 0] = 4; arr[..., 1] = 6; arr[..., 2] = 24; arr[..., 3] = al.astype(np.uint8); return Image.fromarray(arr, 'RGBA')
def b_pane(w, h, col, r=10): return b_rr(w, h, col, r)
def b_bench(w=640): p = Pen(w, 90); p.rr((6, 8, w - 6, 34), (150, 105, 70), 6); [p.rr((x, 34, x + 16, 80), (110, 80, 54), 3) for x in (40, w - 56)]; return p.done()
def b_counter(w=420, h=150):
    p = Pen(w, h); p.rr((6, 20, w - 6, h - 6), (150, 105, 70), 8); p.rr((6, 6, w - 6, 28), (190, 140, 96), 6); return p.done()
def b_desk(w=520, h=170):
    p = Pen(w, h); p.rr((6, 6, w - 6, 30), (200, 150, 100), 6); p.rr((16, 30, w - 16, h - 6), (150, 105, 70), 6)
    p.rr((w / 2 - 70, 54, w / 2 + 70, 120), (120, 82, 56), 6, 2); return p.done()
def b_wall(w=900, h=1300, col=(236, 214, 170)):
    p = Pen(w, h); p.d.rectangle([0, 0, w * 2, h * 2], fill=col)
    for x in range(0, w, 90): p.d.line([(x * 2, 0), (x * 2, h * 2)], fill=tuple(int(v * .93) for v in col), width=4)
    return p.im
def b_skyline(col=(120, 140, 190), w=900, h=500, seed=1):
    rng = np.random.RandomState(seed); p = Pen(w, h); x = 0
    while x < w:
        bw = int(rng.randint(60, 130)); bh = int(rng.randint(120, 440)); p.rr((x, h - bh, x + bw, h + 10), col, 2, 2)
        for wy in range(h - bh + 16, h - 10, 34):
            for wx in range(x + 10, x + bw - 14, 26): p.d.rectangle([wx * 2, wy * 2, (wx + 12) * 2, (wy + 16) * 2], fill=(255, 226, 150, 200) if rng.rand() > .45 else (255, 255, 255, 40))
        x += bw + 4
    return p.im
def b_phonepart(): p = Pen(80, 40); p.rr((4, 4, 76, 36), (90, 94, 120), 5); return p.done()
def b_ring(r=60, col=WHITE, wd=6):
    p = Pen(2 * r + 12, 2 * r + 12); p.d.ellipse([6 * 2, 6 * 2, (6 + 2 * r) * 2, (6 + 2 * r) * 2], outline=col, width=wd * 2); return p.done()
def b_hand(): p = Pen(90, 120); p.rr((26, 40, 66, 110), (240, 190, 150), 16); p.rr((34, 4, 52, 60), (240, 190, 150), 8); return p.done()
def b_scalepost(): p = Pen(60, 520); p.rr((24, 10, 36, 500), (140, 100, 70), 4); p.poly([(0, 508), (30, 470), (60, 508)], (140, 100, 70), 3); p.ell((18, 0, 42, 24), MUST, 3); return p.done()
def b_beam(w=460): p = Pen(w, 36); p.rr((6, 8, w - 6, 26), (120, 84, 56), 8); return p.done()
def b_pan(label, w=170, col=MUST, tc=INK, size=30, h=64):
    p = Pen(w + 20, h + 100)
    p.cap([(w / 2 + 10, 0), (14, 78)], 1.8, INK, 0); p.cap([(w / 2 + 10, 0), (w + 6, 78)], 1.8, INK, 0)
    p.rr((10, 76, 10 + w, 76 + h - 20), col, 10); paste_text(p, text_img(label, size, tc, 0), 10 + w / 2, 76 + (h - 20) / 2); return p.done()
B.update(shop=b_shop, shutter=b_shutter, poster=b_poster, bars=b_bars, cal=b_cal, notebook=b_notebook, book=b_book, balloon=b_balloon, tag=b_tag,
         stopw=b_stopw, sign=b_sign, sun=b_sun, rays=b_rays, moon=b_moon, bulb=b_bulb, cloud=b_cloud, bolt=b_bolt, burst=b_burst, coin=b_coin, check=b_check,
         cross=b_cross, wrench=b_wrench, broom=b_broom, card=b_card, map=b_map, pin=b_pin, spot=b_spot, bench=b_bench, counter=b_counter, desk=b_desk,
         wall=b_wall, skyline=b_skyline, ring=b_ring, hand=b_hand, scalepost=b_scalepost, beam=b_beam, pan=b_pan, pane=b_pane)
ENV = np.load('/tmp/work/db.npy')
def mouth_level(gt):
    i = int(gt * 100); v = ENV[i:i + 6].max() if i < len(ENV) else -80
    return 0 if v < -38 else 1 if v < -24 else 2
def chr_(sc, name, x, y, z=1., s=1., expr='neutral', pose='down', talk=(), ex=(), po=(), look=0, lk=(), walk=None, sil=None, anim=None, a=1., flip=False, ph=None):
    phs = (hash(name) % 7) * .43 if ph is None else ph; st = sc.meta['start']
    def key(t):
        e = expr
        for tt, v in ex:
            if t >= tt: e = v
        p_ = pose
        for tt, v in po:
            if t >= tt: p_ = v
        lo = look
        for tt, v in lk:
            if t >= tt: lo = v
        m = 0
        for a0, a1 in talk:
            if a0 <= t <= a1: m = mouth_level(st + t); break
        w = -1 if walk is None else walk(t)
        br = int((math.sin(t * 2.0 + phs) + 1) * 1.99)
        return ('char', name, e, int(((t + phs) % 3.3) < .13), m, p_, br, lo, w, sil)
    return sc.add(key, x, y, z=z, s_=s, anchor=(.5, .936), anim=anim, a=a, flip=flip)
def walk_fn(t0, t1):
    return lambda t: int(t * 9) % 8 if t0 <= t <= t1 else -1
def txt(sc, s, x, y, size=64, fill=WHITE, stroke=5, t0=0, kind='pop', z=1., anim=None, fixed=False, d=.4, rot=0, t1=1e9):
    return sc.add(('text', s, size, fill, stroke, INK), x, y, z=z, anim=comb(enter(t0, kind, d), anim or (lambda t: {})), fixed=fixed, rot=rot, t1=t1)
def img(sc, key, x, y, t0=0, kind='pop', z=1., s=1., anim=None, rot=0, anchor=(.5, .5), fixed=False, d=.4, a=1., t1=1e9, flip=False, dist=80):
    return sc.add(key, x, y, z=z, s_=s, rot=rot, anchor=anchor, anim=comb(enter(t0, kind, d, dist), anim or (lambda t: {})), fixed=fixed, a=a, t1=t1, flip=flip)
def count_txt(sc, x, y, t0, t1, v0, v1, size=150, fill=WHITE, stroke=8, z=1., fixed=False, hold_anim=None, t_end=1e9):
    def key(t):
        v = int(round(lerp(v0, v1, eo(ramp(t, t0, t1))))); return ('text', bn(v), size, fill, stroke, INK)
    def an(t):
        if t < t0: return dict(a=0)
        if t1 <= t <= t1 + .4: return dict(s=1 + .35 * (1 - eo((t - t1) / .4)) ** 2)
        return {}
    return sc.add(key, x, y, z=z, anim=comb(an, hold_anim or (lambda t: {})), fixed=fixed, t1=t_end)
def stamp(sc, s, x, y, t0, size=80, fill=RED, rot=-8, z=1., fixed=False):
    def an(t):
        x_ = (t - t0) / .22
        if x_ <= 0: return dict(a=0)
        if x_ >= 1: return {}
        return dict(s=lerp(3.2, 1, eo(x_)), a=cl(x_ * 4))
    return sc.add(('text', s, size, fill, 6, INK), x, y, z=z, rot=rot, anim=an, fixed=fixed)
def bgwall(sc, c1, c2, z=.25): sc.bg(c1, c2, z)
def parallax_shapes(sc, col, z, n, seed, y0, y1, w=(60, 160)):
    rng = np.random.RandomState(seed)
    for i in range(n):
        ww = int(rng.randint(*w)); x = rng.randint(-100, 820); y = rng.randint(y0, y1)
        sc.add(('rr', ww, int(ww * rng.uniform(.5, 1.6)), col, 14, 0), x, y, z=z)
