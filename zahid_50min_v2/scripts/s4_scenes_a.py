"""Script 4a: scenes 1-10 of the story (each scene = vector drawing function f(c, t, d, C, m))
   t = local time, d = scene duration, C = local start time of each sentence chunk (+ d at the end), m = voice amplitude."""
import math
from s2_lib import *

ZS, ZA = "#D6A23A", "#5A2E22"     # Zahid shirt / apron
SHOP = "জাহিদ মোবাইল"

# ---------------------------------------------------------------- helpers
def bg(c, a, b):
    rect(c, -2600, -3000, 6400, 3000, a); rect(c, -2600, 1920, 6400, 3000, b); grad(c, -2600, 0, 6400, 1920, a, b)

def floor(c, y, color, line_col=None):
    rect(c, -2600, y, 6400, 2400, color)
    rect(c, -2600, y, 6400, 10, line_col or mix(color, "#000000", 0.25))

def kf(t, pts):
    if t <= pts[0][0]: return pts[0][1:]
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        if t <= b[0]:
            q = ease_io((t - a[0]) / max(b[0] - a[0], 1e-6))
            return tuple(lerp(a[k], b[k], q) for k in (1, 2, 3))
    return pts[-1][1:]

def ph(c, t, t0, t1, fn, fade=0.35, slide=0):
    if t < t0 or t > t1 + fade: return
    a = min(prog(t, t0, fade), 1 - prog(t, t1, fade))
    if a <= 0.01: return
    with alpha_layer(c, a):
        with xform(c, 0, (1 - a) * slide):
            fn(t - t0)

def speak(m, t, t0, t1):
    return min(1.0, m * 1.15) if t0 <= t < t1 else 0.0

def zahid(c, x, y, s=1.0, facing=-1, **kw):
    return person(c, x, y, s, skin="#B97A50", shirt=ZS, pants="#3B2F27", hair="#1E1612", style="short",
                  mustache=True, apron=ZA, facing=facing, **kw)

def customer(c, x, y, s=1.0, facing=1, shirt="#F1EBDD", **kw):
    return person(c, x, y, s, skin="#A66B43", shirt=shirt, pants="#4A4038", hair="#1E1612", style="topi",
                  facing=facing, **kw)

def girl(c, x, y, s=1.0, facing=1, **kw):
    return person(c, x, y, s, skin="#D9A06F", shirt="#FFFFFF", pants="#2F5D3A", hair="#1E1612", style="girl",
                  skirt="#2F5D3A", bag=True, facing=facing, **kw)

def counter_front(c, x0, x1, y0, y1, top="#A9743F", body="#7A4A28"):
    rect(c, x0, y0, x1 - x0, y1 - y0, body)
    rect(c, x0 - 14, y0 - 20, x1 - x0 + 28, 34, top, r=8)
    for i in range(3):
        rect(c, x0 + 24 + i * ((x1 - x0 - 48) / 3), y0 + 40, (x1 - x0 - 48) / 3 - 16, y1 - y0 - 70, mix(body, "#000000", 0.12), r=8)

def shelf(c, x, y, w, items=4):
    rect(c, x, y, w, 20, "#6B4A2B", r=6)
    for i in range(items):
        rect(c, x + 30 + i * (w - 60) / items, y - 70, 70, 70, ["#E4572E", "#F4B942", "#6BA368", "#C9A227"][i % 4], r=8)
        rect(c, x + 30 + i * (w - 60) / items + 12, y - 54, 46, 28, "#FFFFFF", r=5, a=140)

def thought_cloud(c, cx, cy, w, h, p=1.0, tail_to=None):
    if p <= 0.01: return
    s = back_out(p)
    with xform(c, cx, cy, s):
        for dx, dy, r in ((-0.33, 0.05, 0.28), (0, -0.12, 0.34), (0.33, 0.04, 0.3), (-0.12, 0.2, 0.28), (0.18, 0.22, 0.26)):
            circ(c, dx * w, dy * h, r * h, "#000000", 40, blur=8)
        for dx, dy, r in ((-0.33, 0.05, 0.28), (0, -0.12, 0.34), (0.33, 0.04, 0.3), (-0.12, 0.2, 0.28), (0.18, 0.22, 0.26)):
            circ(c, dx * w, dy * h, r * h, "#FFFFFF")
        rect(c, -0.33 * w, -0.1 * h, 0.66 * w, 0.4 * h, "#FFFFFF")
    if tail_to:
        for k, r in enumerate((26, 18, 11)):
            q = (k + 1) / 4
            circ(c, lerp(cx, tail_to[0], q + 0.1), lerp(cy + h * 0.45, tail_to[1], q), r * s, "#FFFFFF")

# ---------------------------------------------------------------- 1. hook
def s_hook(c, t, d, C, m):
    bg(c, "#F4C95D", "#E39A2F"); rays(c, 540, 650, t, "#FFF3C4", 55)
    dots(c, -100, -100, 1200, 2000, 90, 6, "#FFFFFF", 50, ox=t * 10, oy=t * 6)
    out = ease_io(prog(t, C[1] - 0.35, 0.6))
    with xform(c, 0, out * 1700):
        s = pop(t, 0.1, 0.6)
        mn = 300 * ease_io(prog(t, 0.35, 1.9))
        with xform(c, 540, 640, max(s, 0.01)):
            wall_clock(c, 0, 0, 330, minute=mn, hour=mn / 12, wedge_to=mn)
        sw = prog(t, 2.2, 0.5)
        if t < 2.3:
            phone(c, 250, 1230, screen="cracked", s=0.95, rot=-8)
        else:
            phone(c, 250, 1230 - (1 - ease_out(sw)) * 500 * 0, screen="good", s=0.95 + 0.15 * math.sin(sw * math.pi), rot=-8)
            for i in range(6):
                a = i * 60 + t * 30; r = 70 + 90 * ease_out(prog(t, 2.3, 0.6))
                sparkle(c, 250 + math.cos(math.radians(a)) * r, 1230 + math.sin(math.radians(a)) * r, 22 * (1 - prog(t, 2.3, 1.2)))
        tag(c, 760, 1210, "৫০ মিনিট", 74, "#D1452F", "#FFFFFF", pop(t, 1.9, 0.5), rot=-4)
    # phase 2
    if t > C[1] - 0.2:
        q = ease_out(prog(t, C[1] - 0.2, 0.8))
        with xform(c, 0, -(1 - q) * 1700):
            shop_front(c, 540, 1270, 640, sign=SHOP, shutter=0.0)
        for i in range(16):
            x = 40 + i * 68; y = ((t - C[1] - i * 0.21) * 520) % 1700 - 120
            if t > C[1] + i * 0.05 and 0 < y < 1500:
                circ(c, x, y + 8, 30, "#000000", 40, blur=5); coin(c, x, y, 30)
        for i in range(5):
            sparkle(c, 140 + i * 200, 380 + 60 * math.sin(t * 3 + i), 26 + 10 * math.sin(t * 5 + i), "#FFFFFF", 220)

def cam_hook(t, d, C):
    return kf(t, [(0, 1.0, 540, 700), (C[1] - 0.6, 1.12, 540, 760), (C[1] + 0.3, 1.0, 540, 800), (d, 1.22, 540, 900)])

# ---------------------------------------------------------------- 2. rent / shutter
def s_rent(c, t, d, C, m):
    bg(c, "#5B2A22", "#2A1411")
    for i in range(70):  # rain
        x = (i * 97 + t * 260) % 1500 - 200; y = (i * 211 + t * 1500) % 2200 - 150
        line(c, x, y, x - 22, y + 70, "#D8C3A5", 3, 70)
    floor(c, 1300, "#2B1812")
    sh = ease_io(prog(t, 0.2, d - 0.4)) * 0.8
    shop_front(c, 640, 1300, 700, sign=SHOP, shutter=sh, lit=sh < 0.5, wall="#C9A66F")
    if sh > 0.3:
        draw_text(c, "বন্ধ", 640, 1130, 72, "#FFFFFF", int(255 * prog(sh, 0.3, 0.3)), rot=-4, outline=("#D1452F", 10))
    hx, hy = zahid(c, 250, 1330, 1.05, facing=1, mood="worried", sweat=True, t=t, armF=(60 + 6 * math.sin(t * 2), 40), look=1)
    with xform(c, hx + 8, hy - 20, 1, -8 + 3 * math.sin(t * 2)):
        rect(c, -60, -90, 130, 170, "#FFFFFF", r=8); rect(c, -60, -90, 130, 36, "#D1452F", r=8)
        draw_text(c, "ভাড়া", 5, -62, 30, "#FFFFFF")
        for i in range(3): line(c, -42, -20 + i * 28, 50, -20 + i * 28, "#8A7F70", 5)
    tag(c, 330, 560, "ভাড়া বাকি!", 56, "#D1452F", "#FFFFFF", pop(t, 0.5, 0.5), rot=-5)

def cam_rent(t, d, C):
    return kf(t, [(0, 1.0, 540, 760), (d, 1.5, 380, 900)])

# ---------------------------------------------------------------- 3. street
def s_street(c, t, d, C, m):
    bg(c, "#F7C59F", "#EF8E55")
    circ(c, 760, 560, 220, "#FFE9C2", 255); circ(c, 760, 560, 300, "#FFE9C2", 70)
    for i, (x, w, h, col_) in enumerate([(-400, 380, 900, "#B0805A"), (-40, 300, 700, "#C8956A"), (780, 260, 760, "#C8956A"), (1000, 400, 1000, "#A87550")]):
        building(c, x, 1300, w, h, col_, lit=0.3, seed=i, wcol="#FFE7B0")
    building(c, -120, 1300, 330, 840, "#8E5E3E", lit=0.5, seed=3, wcol="#FFE7B0")
    building(c, 870, 1300, 330, 960, "#8E5E3E", lit=0.6, seed=1, wcol="#FFE7B0")
    floor(c, 1300, "#5A4A40")
    rect(c, -2600, 1300, 6400, 240, "#6B5A4E")
    for i in range(10): rect(c, i * 220 - 60 - (t * 30 % 220), 1420, 120, 12, "#F7E7C8", r=4)
    sc = pop(t, 0.0, 0.6)
    shop_front(c, 540, 1300, 440 * (0.85 + 0.15 * sc), sign=SHOP, shutter=0.0, scale_text=0.9)
    rickshaw(c, -300 + t * 330, 1520, 1.0, t, "#E4572E")
    rickshaw(c, 1500 - t * 250, 1640, 0.8, t, "#6BA368", facing=-1)
    # map pin
    pinp = pop(t, 0.5, 0.6); py = 480 - (1 - pinp) * 300 + 8 * math.sin(t * 4)
    with xform(c, 540, py, max(pinp, 0.01)):
        circ(c, 0, 60, 14, "#000000", 70, blur=6)
        poly(c, [(-44, -60), (44, -60), (0, 54)], "#D1452F"); circ(c, 0, -62, 56, "#D1452F"); circ(c, 0, -62, 22, "#FFFFFF")
    tag(c, 540, 330, "মিরপুর", 72, "#2B2118", "#FFE9A8", pop(t, 0.7, 0.5))

def cam_street(t, d, C):
    return kf(t, [(0, 1.0, 540, 760), (d, 1.45, 540, 960)])

# ---------------------------------------------------------------- 4. inside (father photo, old clock)
def s_inside(c, t, d, C, m):
    bg(c, "#9AA862", "#5F6B3A")
    for i in range(-3, 12): rect(c, i * 130, -100, 60, 1500, "#FFFFFF", a=14)
    floor(c, 1330, "#6B4A2B")
    shelf(c, 20, 1000, 300, 3); shelf(c, 760, 1060, 330, 4)
    # father frame
    fx, fy = 290, 640
    rect(c, fx - 200, fy - 250, 400, 500, "#000000", r=16, a=60, blur=14)
    rect(c, fx - 200, fy - 250, 400, 500, "#5A3A1E", r=16); rect(c, fx - 170, fy - 220, 340, 440, "#E9DCC0", r=8)
    c.save(); c.clipRect(skia.Rect.MakeXYWH(fx - 170, fy - 220, 340, 440))
    rect(c, fx - 170, fy - 220, 340, 440, "#CBB892")
    person(c, fx, fy + 330, 0.85, skin="#A8754F", shirt="#EDE6D4", style="grey", mustache=True, facing=1, mood="neutral",
           legs=False, blink=False)
    c.restore()
    for i in range(9):
        circ(c, fx - 190 + i * 47.5, fy - 252 + 22 * math.sin(i * 0.7 + 1) + 26, 20, "#F28C28" if i % 2 else "#F4B942")
    # key
    kp = pop(t, 0.5, 0.6)
    with xform(c, fx, 1040 + 8 * math.sin(t * 2), max(kp, 0.01), 12 * math.sin(t * 2)):
        line(c, 0, -70, 0, -30, "#6B4A2B", 5)
        circ(c, 0, 0, 36, "#E5C158", stroke=14); rect(c, -8, 30, 16, 110, "#E5C158", r=6); rect(c, 8, 90, 34, 14, "#E5C158", r=4); rect(c, 8, 118, 24, 12, "#E5C158", r=4)
        for i in range(4): sparkle(c, math.cos(i * 1.6 + t * 2) * 80, 40 + math.sin(i * 1.6 + t * 2) * 80, 14, "#FFFFFF", 230)
    # old clock
    cx_, cy_ = 790, 520
    p = pop(t, C[1] - 0.1, 0.6) if t > C[1] - 0.6 else 1.0
    sway = 3 * math.sin(t * 2.4)
    with xform(c, cx_, cy_ - 200, 1, sway):
        with xform(c, 0, 200, 1):
            pass
    wall_clock(c, cx_, cy_, 190, minute=(t * 24) % 360, hour=(t * 2) + 100, rim="#3A2412", face="#F2E3BE")
    rect(c, cx_ - 60, cy_ + 200, 120, 24, "#3A2412", r=8)
    pend = math.sin(t * 3.2) * 18
    with xform(c, cx_, cy_ + 214, 1, pend):
        line(c, 0, 0, 0, 170, "#3A2412", 8); circ(c, 0, 190, 34, "#C9A227"); circ(c, 0, 190, 22, "#E5C158")
    if t > C[1]:
        tag(c, cx_, cy_ - 270, "পুরনো ঘড়ি", 50, "#2B2118", "#FFE9A8", pop(t, C[1] + 0.2, 0.5))
    if t < C[1]:
        tag(c, fx, fy - 330, "বাবা", 56, "#2B2118", "#FFE9A8", pop(t, 0.3, 0.5))

def cam_inside(t, d, C):
    return kf(t, [(0, 1.45, 300, 780), (C[1] - 0.3, 1.4, 300, 800), (C[1] + 0.5, 1.55, 790, 640), (d, 1.7, 790, 600)])

# ---------------------------------------------------------------- 5. busy but never timed
def s_busy(c, t, d, C, m):
    bg(c, "#EFE2BF", "#D9C493")
    dots(c, -100, -100, 1200, 2000, 80, 5, "#B39A63", 60)
    floor(c, 1320, "#B58B52")
    # wall clock (ignored)
    cx_, cy_ = 800, 470
    dust = prog(t, C[1], 1.0)
    wall_clock(c, cx_, cy_, 170, minute=40, hour=200, face=mix("#FFF6E0", "#CFC3A5", dust), rim="#6B5B45")
    for i in range(3):
        arc(c, cx_ - 130, cy_ - 130, 40 + i * 22, 180, 270, "#FFFFFF", 3, 200 * dust)
    # bench
    rect(c, 360, 1090, 560, 40, "#8A5A34", r=8); rect(c, 390, 1130, 40, 240, "#6B4326"); rect(c, 850, 1130, 40, 240, "#6B4326")
    work = math.sin(t * 7) * 6
    phone(c, 640, 1052, 150, 40, rot=0, screen="off", s=1.0)
    line(c, 740, 1075, 800 + work, 1052, "#8A8F8C", 10); rect(c, 790 + work, 1038, 40, 26, "#D1452F", r=8)
    zahid(c, 250, 1350, 1.12, facing=1, mood="neutral", t=t, armF=(62 + work, 55), look=1)
    # icons pop around
    icons = [(megaphone, 760, 760, 0.3), (broom, 920, 960, 0.75), (price_tag, 520, 560, 1.15)]
    fade = 1 - ease_in(prog(t, 2.7, 0.45))
    question(c, 330, 520, 170 * pop(t, 3.0, 0.4), "#D1452F", 255, rot=-8)
    with alpha_layer(c, fade):
        p0 = pop(t, 0.3, 0.5)
        with xform(c, 560, 700 + 10 * math.sin(t * 3), max(p0, 0.01)): megaphone(c, 0, 0, 1.3, -12)
        p1 = pop(t, 0.8, 0.5)
        with xform(c, 920, 880 + 10 * math.sin(t * 3 + 1), max(p1, 0.01)): broom(c, 0, 0, 1.3, 14)
        p2 = pop(t, 1.3, 0.5)
        with xform(c, 640, 540 + 10 * math.sin(t * 3 + 2), max(p2, 0.01)): price_tag(c, 0, 0, "৳ কম", 1.3, -6)
    # the one thing never done
    if t > C[1]:
        q = pop(t, C[1] + 0.5, 0.5)
        with xform(c, 330, 1020, max(q, 0.01)):  # stopwatch with cross
            circ(c, 0, 0, 80, "#2B2118"); circ(c, 0, 0, 64, "#FFF6E0"); rect(c, -12, -102, 24, 24, "#2B2118", r=6)
            line(c, 0, 0, 0, -44, "#2B2118", 7); line(c, 0, 0, 30, 14, "#D1452F", 6)
            cross(c, 0, 0, 100, "#D1452F", 22, prog(t, C[1] + 0.9, 0.3))
        question(c, 800, 330, 150, "#D1452F", int(255 * pop(t, C[1] + 0.9, 0.4)), rot=12)

def cam_busy(t, d, C):
    return kf(t, [(0, 1.0, 540, 760), (2.5, 1.12, 560, 800), (C[1] + 0.3, 1.1, 480, 800), (C[1] + 1.4, 1.45, 700, 620), (d, 1.5, 720, 640)])

# ---------------------------------------------------------------- 6. ad banner + "how fast?"
def s_ad(c, t, d, C, m):
    bg(c, "#C4573A", "#8E2F1E"); rays(c, 540, 700, t, "#F6B39A", 45, speed=-5)
    dots(c, -100, -100, 1200, 2000, 100, 7, "#FFFFFF", 30)
    drop = ease_out(prog(t, 0.0, 0.7)); bounce = math.sin(prog(t, 0.5, 1.0) * math.pi * 3) * 10 * (1 - prog(t, 0.5, 1.0))
    sc2 = 1 - 0.35 * ease_io(prog(t, C[1] - 0.1, 0.5))
    by = 600 - (1 - drop) * 900 - 190 * ease_io(prog(t, C[1] - 0.1, 0.5)) + bounce
    with xform(c, 540, by, sc2, math.sin(t * 2) * 1.2):
        line(c, -320, -230, -280, -520, "#3A2412", 8); line(c, 320, -230, 280, -520, "#3A2412", 8)
        rect(c, -430 + 8, -200 + 14, 860, 400, "#000000", r=30, a=70, blur=10)
        rect(c, -430, -200, 860, 400, "#2B2118", r=30); rect(c, -410, -180, 820, 360, "#F4B942", r=22)
        rect(c, -392, -162, 784, 324, "#2B2118", r=14)
        draw_text(c, "দ্রুত ও নির্ভরযোগ্য", 0, -20, 84, "#F4B942"); draw_text(c, "মোবাইল সার্ভিস", 0, 100, 84, "#FFFFFF")
        for i in range(4): sparkle(c, -380 + i * 250 + 40 * math.sin(t * 3 + i), -210, 18, "#FFF3B0", 230)
    if t > C[1] - 0.1:
        p = pop(t, C[1] + 0.1, 0.6)
        with xform(c, 540, 1000, max(p, 0.01)):
            circ(c, 8, 16, 205, "#000000", 70, blur=12)
            circ(c, 0, 0, 200, "#2B2118"); circ(c, 0, 0, 170, "#FFF6E0"); rect(c, -26, -250, 52, 52, "#2B2118", r=12)
            for i in range(12):
                a = math.radians(i * 30); line(c, math.cos(a) * 140, math.sin(a) * 140, math.cos(a) * 160, math.sin(a) * 160, "#2B2118", 6)
            ang = (t * 140) % 360
            line(c, 0, 0, math.cos(math.radians(ang - 90)) * 120, math.sin(math.radians(ang - 90)) * 120, "#D1452F", 10)
            draw_text(c, "?", 0, 62, 190, "#2B2118", int(180 * (0.5 + 0.5 * math.sin(t * 5))))
        for i in range(5):
            q = pop(t, C[1] + 0.3 + i * 0.12, 0.4)
            question(c, 160 + i * 190, 1330 + 40 * math.sin(t * 4 + i), 100 * q, "#FFE9A8", 255, rot=-15 + i * 8)

def cam_ad(t, d, C):
    return kf(t, [(0, 1.0, 540, 600), (C[1] - 0.2, 1.25, 540, 560), (C[1] + 0.5, 1.15, 540, 960), (d, 1.3, 540, 980)])

# ---------------------------------------------------------------- 7. counter dialogue
def s_counter(c, t, d, C, m):
    bg(c, "#B3C294", "#7F9561")
    for i in range(-3, 14): rect(c, i * 120, -100, 56, 1500, "#FFFFFF", a=16)
    floor(c, 1290, "#8A6A45")
    shelf(c, 600, 480, 420, 4); shelf(c, 600, 640, 420, 4)
    wall_clock(c, 300, 340, 100, minute=(t * 6) % 360, hour=100, rim="#5A3E22")
    # big shop (far left)
    shop_front(c, -700, 1290, 800, sign="বড় মোবাইল শপ", wall="#EDE6D8", awning=("#2B2118", "#F4B942"), sign_col="#7A1F1F")
    # background walkers in chunk 0
    for k, (sh_, tt0) in enumerate((("#8C3B2E", 0.0), ("#6B8E4E", 0.5))):
        x = -250 + (t - tt0) * 430
        if tt0 <= t < C[1] + 0.8 and x < 1400:
            customer(c, x, 1215, 0.72, 1, shirt=sh_, walk=t * 11)
    # Zahid
    z_t = speak(m, t, C[2] + 0.95, C[2] + 1.55)
    sh_up = ease_io(prog(t, C[4], 0.4)) * (1 - ease_io(prog(t, C[5], 0.4)))
    zahid(c, 830, 1290, 1.12, facing=-1, mood="worried" if t > C[4] else "neutral", talk=z_t, t=t, sweat=(C[4] < t < C[5]),
          armF=(10 + 150 * sh_up, 5 - 40 * sh_up), armB=(-10 - 150 * sh_up, 5))
    counter_front(c, 560, 1180, 1070, 1400)
    # main customer
    arrive = ease_out(prog(t, 0.1, C[1] - 0.2))
    leave = ease_in(prog(t, C[5] + 0.6, 2.4))
    cx_ = lerp(-220, 320, arrive) - leave * 1100
    c_t = speak(m, t, C[1] + 1.5, C[1] + 2.8) + speak(m, t, C[3] + 1.5, C[3] + 2.05)
    raise_ = ease_io(prog(t, C[1] + 0.2, 0.5)) * 1.0
    walking = (arrive < 0.97) or leave > 0
    fc = -1 if leave > 0 else 1
    hx, hy = customer(c, cx_, 1290, 1.12, fc, mood="neutral", talk=min(1, c_t), t=t, walk=(t * 11 if walking else None),
                      armF=(20 + 80 * raise_, 10))
    if t > C[1]:
        phone(c, hx + fc * 22, hy - 40, 120, 230, rot=fc * 8, screen="cracked", s=0.9)
    # bubbles
    bubble(c, 330, 480, "ভাই, কতক্ষণ লাগবে?", prog(t, C[1] + 1.45, 0.3) * (1 - prog(t, C[2] + 0.05, 0.2)), 46, 430, tail=(-10, 175))
    bubble(c, 760, 500, "হয়ে যাবে।", prog(t, C[2] + 0.95, 0.3) * (1 - prog(t, C[3] + 0.1, 0.2)), 50, 420, tail=(80, 160))
    bubble(c, 330, 480, "কখন?", prog(t, C[3] + 1.5, 0.3) * (1 - prog(t, C[4] + 0.1, 0.2)), 56, 380, tail=(-10, 175))
    if C[4] < t < C[5] + 0.6:
        a = prog(t, C[4] + 0.3, 0.3) * (1 - prog(t, C[5], 0.4))
        bubble(c, 790, 480, "...", a, 70, 300, tail=(40, 160))
        for i in range(3): question(c, 520 + i * 90, 380 - 20 * math.sin(t * 4 + i), 90, "#D1452F", int(255 * a), rot=-10 + 10 * i)

def cam_counter(t, d, C):
    return kf(t, [(0, 1.05, 450, 760), (C[1], 1.15, 400, 760), (C[2], 1.1, 660, 740), (C[3], 1.15, 450, 760),
                  (C[4], 1.1, 660, 740), (C[5], 1.05, 560, 760), (C[5] + 0.5, 1.05, 480, 760), (C[5] + 3.2, 0.95, -250, 800)])

# ---------------------------------------------------------------- 8. girl arrives
def s_girl1(c, t, d, C, m):
    bg(c, "#F6BDA4", "#E58B6F")
    dots(c, -100, -100, 1200, 2000, 100, 8, "#FFFFFF", 45, ox=t * 8)
    floor(c, 1290, "#C4694B")
    arrive = ease_out(prog(t, 0.0, C[1] - 0.3))
    gx = lerp(-250, 330, arrive)
    hx, hy = girl(c, gx, 1290, 1.15, 1, mood="worried" if t > C[3] else "neutral", t=t, walk=(t * 11 if arrive < 0.97 else None),
                  armF=(20 + 80 * ease_io(prog(t, C[1] - 0.3, 0.5)), 10))
    if t > C[1] - 0.3:
        phone(c, hx + 22, hy - 40, 120, 230, rot=8, screen="cracked", s=0.9)
    # calendar
    if t > C[1] and t < C[2] + 0.5:
        p = pop(t, C[1] + 0.05, 0.5); out = ease_in(prog(t, C[2] - 0.1, 0.4))
        with xform(c, 790 + out * 700, 560, max(p, 0.01), 4 * math.sin(t * 3)):
            rect(c, -170 + 8, -190 + 14, 340, 380, "#000000", r=24, a=60, blur=10)
            rect(c, -170, -190, 340, 380, "#FFFFFF", r=24); rect(c, -170, -190, 340, 90, "#D1452F", r=24); rect(c, -170, -140, 340, 40, "#D1452F")
            draw_text(c, "কাল", 0, -112, 60, "#FFFFFF")
            draw_text(c, "পরীক্ষা", 0, 40, 84, "#2B2118")
            for i in range(3):
                circ(c, -90 + i * 90, 110, 12, "#CFC3A5")
            arc(c, 0, 12, 150, 0, 360 * prog(t, C[1] + 0.5, 0.5), "#D1452F", 10)
    # phone with all notes
    if t > C[2] - 0.1:
        p = pop(t, C[2] + 0.1, 0.5)
        shake = math.sin(t * 70) * 10 * (1 - prog(t, C[3], 0.5)) if t > C[3] else 0
        broken = t > C[3] + 0.05
        with xform(c, 790 + shake, 760, 1.55 * max(p, 0.01), -6):
            phone(c, 0, 0, 170, 330, screen="cracked" if broken else "notes", t=t)
        if not broken:
            for i in range(5):
                q = prog(t, C[2] + 0.2 + 0.12 * i, 0.5)
                x = lerp(1080 + 60 * i, 790, ease_in(q)) + 0; y = lerp(250 + i * 60, 760, ease_in(q))
                if 0 < q < 1:
                    with xform(c, x, y, 1 - 0.5 * q, 20 * i):
                        rect(c, -34, -44, 68, 88, ["#E4572E", "#6BA368", "#F4B942", "#C0574A", "#8A5A34"][i], r=8); rect(c, -28, -38, 8, 76, "#FFFFFF", a=140)
        else:
            f = 1 - prog(t, C[3], 0.35)
            if f > 0: rect(c, -2600, -2600, 6400, 6400, "#FFFFFF", a=int(150 * f))
            for i in range(8):
                a = i * 45 + 20; r = 240 * ease_out(prog(t, C[3], 0.4))
                line(c, 790 + math.cos(math.radians(a)) * 270, 760 + math.sin(math.radians(a)) * 270,
                     790 + math.cos(math.radians(a)) * (270 + r * 0.4), 760 + math.sin(math.radians(a)) * (270 + r * 0.4), "#2B2118", 8, int(255 * (1 - prog(t, C[3] + 0.2, 0.5))))

def cam_girl1(t, d, C):
    return kf(t, [(0, 1.0, 540, 760), (C[1], 1.1, 600, 740), (C[2], 1.2, 700, 740), (C[3] - 0.1, 1.2, 700, 740), (C[3] + 0.2, 1.4, 760, 740), (d, 1.5, 760, 760)])

# ---------------------------------------------------------------- 9. girl asks
def s_girl2(c, t, d, C, m):
    bg(c, "#40302A", "#1F1612")
    for i in range(-3, 14): rect(c, i * 120, -100, 56, 1500, "#FFFFFF", a=7)
    floor(c, 1290, "#4B3626")
    radial(c, 540, 330, 900, "#FFC864", "#FFC864", 105, 0)
    line(c, 540, -200, 540, 120, "#8A8F8C", 6); poly(c, [(450, 220), (630, 220), (590, 120), (490, 120)], "#E5C158"); oval(c, 540, 224, 90, 14, "#FFF1B0")
    circ(c, 920, 330, 90, "#F7E7B5"); circ(c, 950, 310, 82, "#40302A")
    wall_clock(c, 200, 420, 110, minute=(t * 6) % 360, hour=285, rim="#7A5A38")
    shelf(c, 700, 640, 380, 4)
    g_t = speak(m, t, C[0] + 1.3, C[0] + 3.1) + speak(m, t, C[2] + 2.25, C[2] + 6.2)
    z_t = speak(m, t, C[1] + 1.0, C[1] + 1.55)
    zahid(c, 830, 1290, 1.12, facing=-1, mood="worried" if t > C[2] else "neutral", talk=z_t, t=t, sweat=t > C[2] + 3)
    counter_front(c, 560, 1180, 1070, 1400)
    hx, hy = girl(c, 310, 1290, 1.12, 1, mood="neutral", talk=min(1, g_t), t=t, armF=(100, 10))
    phone(c, hx + 22, hy - 40, 120, 230, rot=8, screen="cracked", s=0.9)
    bubble(c, 330, 520, "ভাইয়া, আজ রাতের মধ্যে পাব?", prog(t, C[0] + 1.3, 0.3) * (1 - prog(t, C[1] + 0.1, 0.2)), 44, 460, tail=(-10, 150))
    bubble(c, 760, 560, "হয়ে যাবে।", prog(t, C[1] + 1.0, 0.3) * (1 - prog(t, C[2] + 0.1, 0.2)), 54, 420, tail=(80, 130))
    bubble(c, 400, 560, "হয়ে যাবে মানে কখন? আমি অপেক্ষা করব, নাকি অন্য দোকানে যাব?", prog(t, C[2] + 2.25, 0.3), 42, 560, tail=(-60, 150))
    tag(c, 230, 250, "অপেক্ষা করব?", 46, "#F4B942", "#2B2118", pop(t, C[2] + 3.9, 0.4), rot=-4)
    tag(c, 560, 150, "অন্য দোকানে যাব?", 46, "#E4572E", "#FFFFFF", pop(t, C[2] + 5.1, 0.4), rot=3)

def cam_girl2(t, d, C):
    return kf(t, [(0, 1.15, 420, 760), (C[1], 1.1, 650, 760), (C[2], 1.1, 600, 760), (C[2] + 2.0, 1.0, 560, 700), (d, 1.15, 560, 720)])

# ---------------------------------------------------------------- 10. realisation
def s_realize(c, t, d, C, m):
    bg(c, "#D1BF8C", "#A18C5C"); rays(c, 360, 800, t, "#FFF6D0", 28, speed=3)
    floor(c, 1320, "#7C6741")
    hx, hy = zahid(c, 330, 1330, 1.3, facing=1, mood="neutral" if t < C[2] else "surprised", t=t, armF=(14, 20), look=0.5)
    # cloud
    cp = pop(t, 0.2, 0.6)
    thought_cloud(c, 700, 560, 620, 440, cp, tail_to=(430, 840))
    def i0(lt):
        question(c, 700, 640, 260 * (0.9 + 0.1 * math.sin(lt * 4)), "#D1452F")
        phone(c, 520, 560, 120, 230, rot=-14, screen="off", s=0.8)
    def i1(lt):
        phone(c, 600, 560, 150, 290, screen="open", s=0.9)
        line(c, 720, 640, 820, 500, "#8A8F8C", 26); circ(c, 830, 490, 36, "#8A8F8C"); circ(c, 842, 478, 14, "#FFFFFF")
        cross(c, 700, 560, 130, "#D1452F", 24, prog(lt, 0.5, 0.35))
    def i2(lt):
        wall_clock(c, 560, 580, 120, minute=(lt * 90) % 360, shadow_on=False)
        phone(c, 830, 600, 120, 230, screen="good", s=0.85)
        curve(c, [(660, 440), (700, 380), (780, 400), (820, 470)], "#D1452F", 10)
        poly(c, [(826, 500), (790, 460), (846, 456)], "#D1452F")
        draw_text(c, "কখন?", 700, 330, 74, "#D1452F")
    ph(c, t, 0.6, C[1], i0); ph(c, t, C[1], C[2], i1); ph(c, t, C[2], d, i2)

def cam_realize(t, d, C):
    return kf(t, [(0, 1.0, 540, 800), (C[1], 1.15, 560, 700), (C[2], 1.25, 600, 700), (d, 1.4, 640, 700)])

SCENES_A = {
    "hook": (s_hook, cam_hook), "rent": (s_rent, cam_rent), "street": (s_street, cam_street), "inside": (s_inside, cam_inside),
    "busy": (s_busy, cam_busy), "ad": (s_ad, cam_ad), "counter": (s_counter, cam_counter), "girl1": (s_girl1, cam_girl1),
    "girl2": (s_girl2, cam_girl2), "realize": (s_realize, cam_realize),
}
