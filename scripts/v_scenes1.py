# Scenes part 1 (story opening -> the girl's broken phone). Each scene: f(c, lt, D, S)
import math
import skia
from v_lib import *
from v_props import *


# ------------------------------------------------------------ people presets
def zahid(c, x, y, t, **kw):
    kw.setdefault("shirt", "#6F8447")
    person(c, x, y, skin=SKIN["zahid"], hair="#1B1410", mustache=True, t=t, **kw)


def cust(c, x, y, t, kind=1, **kw):
    cfg = {1: dict(shirt="#9B3D2E", skin=SKIN["c1"], hair="#2A1A12", mustache=False),
           2: dict(shirt="#D6A23C", skin=SKIN["c2"], hair="#1B1410", mustache=True),
           3: dict(shirt="#8A8A80", skin=SKIN["c1"], hair="#3A2A1F", mustache=False),
           4: dict(shirt="#5E7A4A", skin=SKIN["c2"], hair="#1B1410", mustache=False),
           5: dict(shirt="#C7703A", skin=SKIN["c1"], hair="#1B1410", mustache=True),
           6: dict(shirt="#7A4E3A", skin=SKIN["c2"], hair="#2A1A12", mustache=False)}[kind]
    cfg.update(kw)
    person(c, x, y, t=t, **cfg)


def girl(c, x, y, t, **kw):
    kw.setdefault("shirt2", "#8E2D2D")
    person(c, x, y, skin=SKIN["girl"], shirt="#F7F1E3", hair="#1B1410", style="girl", t=t, **kw)


# ------------------------------------------------------------ shared backgrounds / props
def shop_interior(c, t, night=False, clock_min=10, extra_cover=True):
    wall1, wall2 = ("#D8B684", "#C9A56F") if not night else ("#3A2A20", "#2E211A")
    bg_solid(c, wall1)
    # wainscot
    rect(c, -300, 1000, W + 600, 700, fill("#7B4B2C" if not night else "#2A1B13"))
    line(c, -300, 1000, W + 300, 1000, "#4A2B15", 10)
    # shelves with phones
    for i, sy in enumerate((330, 600)):
        rect(c, 40, sy + 120, 480, 18, fill("#5B3A22"))
        for j in range(6):
            col_ = ["#2B2B2B", "#6F5A44", "#3C3C3C", "#8A5A3A", "#2B2B2B", "#4A4A44"][(j + i) % 6]
            rrect(c, 66 + j * 74, sy + 20, 50, 100, 8, fill(col_))
            rrect(c, 72 + j * 74, sy + 28, 38, 80, 5, fill("#E8B23A" if (j + i) % 3 == 0 else "#1E1B19", 0.9))
    wall_clock(c, 830, 330, 110, minutes=clock_min, t=t, hour_extra=300)
    # window
    rrect(c, 640, 520, 330, 330, 14, fill("#4A2B15"))
    rrect(c, 656, 536, 298, 298, 8, fill("#F2D9A0" if not night else "#2A1E18"))
    line(c, 805, 536, 805, 834, "#4A2B15", 8)
    line(c, 656, 685, 954, 685, "#4A2B15", 8)
    if night:
        moon(c, 740, 620, 36)
    if night:
        c.drawRect(skia.Rect.MakeXYWH(-300, -300, W + 600, 2400), rad_grad(540, 620, 900, [("#FFD08A", 0.22), ("#000000", 0.55)]))


def counter_front(c, night=False):
    counter(c, 540, 1140, 1500, 200, top="#9A683C" if not night else "#6B4A2C", front="#6B4226" if not night else "#4A2E1B")


def shop_front(c, x, y, w, t, shutter=0.0, sign="মোবাইল সার্ভিসিং", wall="#C98B5E", awn1="#A8402E", awn2="#F3E3C3", door_dark="#4A2E1F"):
    h = 560
    rect(c, x - w / 2, y - h, w, h, fill(wall))
    rect(c, x - w / 2 + 40, y - 360, w - 80, 360, fill(door_dark))
    # interior hint
    rect(c, x - w / 2 + 40, y - 360, w - 80, 360, rad_grad(x, y - 200, w * 0.5, [("#F2C36B", 0.55), ("#F2C36B", 0.0)]))
    rect(c, x - w / 2 + 60, y - 120, w - 120, 20, fill("#8A5A34"))
    # awning
    n = 8
    aw = (w + 40) / n
    for i in range(n):
        poly(c, [(x - w / 2 - 20 + i * aw, y - 400), (x - w / 2 - 20 + (i + 1) * aw, y - 400),
                 (x - w / 2 - 20 + (i + 1) * aw, y - 345), (x - w / 2 - 20 + i * aw, y - 345)], fill(awn1 if i % 2 == 0 else awn2))
    signboard(c, x, y - 465, w * 0.84, 100, sign, bg="#3F5E45", fg="#FFF3D6", size=56, border="#F2D16B")
    if shutter > 0:
        sh = 360 * shutter
        top = y - 360
        rect(c, x - w / 2 + 30, top, w - 60, sh, fill("#8C8B84"))
        k = 0
        while k < sh:
            line(c, x - w / 2 + 30, top + k, x + w / 2 - 30, top + k, "#6A6962", 4)
            k += 22
        rect(c, x - w / 2 + 30, top + sh - 10, w - 60, 14, fill("#5A5953"))


def skyline(c, y, seed=1, cols=("#9A6A4A", "#7F5238", "#B58560"), x0=-400, x1=1500):
    import random
    rnd = random.Random(seed)
    x = x0
    while x < x1:
        bw = rnd.randint(110, 220)
        bh = rnd.randint(250, 700)
        cc = cols[rnd.randint(0, len(cols) - 1)]
        rect(c, x, y - bh, bw, bh + 600, fill(cc))
        for wy in range(int(y - bh + 30), int(y - 30), 70):
            for wx in range(int(x + 20), int(x + bw - 40), 55):
                if rnd.random() < 0.65:
                    rect(c, wx, wy, 28, 38, fill("#F2D9A0", 0.85) if rnd.random() < 0.4 else fill("#3A2A20", 0.5))
        x += bw + rnd.randint(0, 14)


def banner_text(c, x, y, w, h, lines, size, t, reveal=1.0, bg="#F3E3C3", fg="#3A2A1E", frame="#A8402E", hl=None):
    # hanging banner on two ropes
    line(c, x - w * 0.38, y - h / 2 - 170, x - w * 0.38, y - h / 2 + 10, "#5A3A22", 8)
    line(c, x + w * 0.38, y - h / 2 - 170, x + w * 0.38, y - h / 2 + 10, "#5A3A22", 8)
    rrect(c, x - w / 2 + 12, y - h / 2 + 16, w, h, 18, fill("#000000", 0.25))
    rrect(c, x - w / 2, y - h / 2, w, h, 18, fill(bg))
    rrect(c, x - w / 2 + 14, y - h / 2 + 14, w - 28, h - 28, 10, stroke(frame, 8))
    c.save()
    c.clipRect(skia.Rect.MakeXYWH(x - w / 2, y - h / 2, w * reveal, h))
    lh = size * 1.3
    y0 = y - (len(lines) - 1) * lh / 2 + size * 0.34
    for i, l in enumerate(lines):
        if isinstance(l, tuple):
            draw_text(c, l[0], x, y0 + i * lh, size * l[2] if len(l) > 2 else size, l[1], "b")
        else:
            draw_text(c, l, x, y0 + i * lh, size, fg, "b")
    c.restore()


def crumpled_paper(c, x, y, w, h, rot, label, t=0.0):
    c.save(); c.translate(x, y); c.rotate(rot)
    rrect(c, -w / 2 + 6, -h / 2 + 8, w, h, 8, fill("#000000", 0.2))
    rrect(c, -w / 2, -h / 2, w, h, 8, fill("#F7F0DC"))
    for i in range(3):
        line(c, -w / 2 + 20, -h / 2 + 50 + i * 26, w / 2 - 20, -h / 2 + 50 + i * 26, "#A89B80", 4)
    draw_text(c, label, 0, -h / 2 + 38, 38, "#B9402E", "b")
    c.restore()


# ============================================================ SCENES
def sc_hook(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 880, 1.0), (D, 540, 820, 1.28)])
    bg_rays(c, 540, 820, "#E3A93B", "#F0C45F", lt)
    # phone: cracked -> replaced
    sw = prog(lt, 0.9, 1.5)
    shake = math.sin(lt * 40) * 6 * (1 - prog(lt, 0.9, 1.3)) if lt < 1.3 else 0
    state = "cracked" if lt < 1.1 else "on"
    pos_y = 840 + (1 - ease_out(prog(lt, 0.0, 0.6))) * -500
    phone(c, 540 + shake, pos_y, 380, 760, rot=-4 + shake * 0.2, state=state, t=lt, crack=prog(lt, 0.2, 0.7))
    if 1.05 < lt < 1.7:
        for i in range(8):
            a = i * math.pi / 4
            r = (lt - 1.05) * 700
            sparkle(c, 540 + math.cos(a) * r, 840 + math.sin(a) * r, 40 * (1 - prog(lt, 1.05, 1.7)), "#FFF3D6", lt * 200)
    # stopwatch
    sp = pop(lt, 0.5, 0.45)
    c.save(); c.translate(830, 470); c.scale(sp, sp)
    stopwatch(c, 0, 0, 120, sec=lt * 20, label="")
    c.restore()
    # big 50 minutes
    ps = pop(lt, 1.9, 0.5)
    c.save(); c.translate(540, 1340); c.scale(ps, ps)
    draw_text(c, "৫০ মিনিট", 0, 0, 190, "#FFF3D6", "b", outline="#4A2B15", ow=26)
    c.restore()
    c.restore()


def sc_shop_fortune(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 1000, 1.0), (D, 540, 760, 1.55)])
    bg_grad(c, "#F2B88A", "#E8D6A8")
    sun(c, 840, 500, 120, lt, "#F3A93B")
    skyline(c, 1250, seed=4, cols=("#B07A58", "#9A6244", "#C68F68"))
    rect(c, -300, 1250, W + 600, 800, fill("#7A5A40"))
    shop_front(c, 540, 1350, 640, lt)
    # arrow of fortune
    p = ease_out(prog(lt, 1.3, 2.4))
    if p > 0:
        a = fill("#4F7A3A")
        c.save(); c.translate(540, 420 - p * 60); c.scale(p, p)
        poly(c, [(-120, 60), (0, -90), (120, 60), (50, 60), (50, 200), (-50, 200), (-50, 60)], a)
        c.restore()
        for i in range(6):
            sparkle(c, 540 + math.cos(i * 1.05 + lt) * 230, 420 + math.sin(i * 1.05 + lt) * 150, 26 * p, "#FFF3D6", lt * 90)
    # "50 min" tag flying to sign
    tp = ease(prog(lt, 0.2, 1.3))
    if tp < 1:
        c.save(); c.translate(lerp(1000, 540, tp), lerp(300, 880, tp)); c.scale(1 - 0.3 * tp, 1 - 0.3 * tp)
        rrect(c, -170, -60, 340, 120, 30, fill("#FFF3D6")); rrect(c, -170, -60, 340, 120, 30, stroke("#4A2B15", 6))
        draw_text(c, "৫০ মিনিট", 0, 28, 72, "#B9402E", "b")
        c.restore()
    c.restore()


def sc_rent(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 900, 1.0), (S.w(2, 11), 500, 920, 1.25), (D, 540, 900, 1.1)])
    shop_interior(c, lt, night=True, clock_min=10)
    zahid(c, 420, 1190, lt, mouth="sad", brow=1.0, hl=(60, -140), hr=(-10, -170), look=(0, 0.6), sweat=True)
    counter_front(c, night=True)
    # bills falling onto counter
    for i in range(5):
        t0 = 0.25 + i * 0.45
        p = prog(lt, t0, t0 + 0.7)
        if p > 0:
            yy = lerp(-100, 1080 - i * 14, ease_out(p) if p < 1 else 1)
            crumpled_paper(c, 700 + (i - 2) * 85, yy, 180, 220, -0.3 + i * 0.18, "ভাড়া")
    c.restore()
    # shutter dropping over the screen
    sp = ease(prog(lt, S.w(2, 11), S.w(2, 13) + 0.2))
    if sp > 0:
        sh = H * sp
        rect(c, 0, 0, W, sh, fill("#8C8B84"))
        k = 0
        while k < sh:
            line(c, 0, k, W, k, "#6A6962", 5)
            k += 40
        rect(c, 0, sh - 18, W, 24, fill("#5A5953"))
        rrect(c, 490, sh - 90, 100, 36, 12, fill("#3A3934"))


def sc_mirpur(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 640, 1.0), (D, 540, 1180, 1.7)])
    bg_grad(c, "#E8A56E", "#F6D9A8")
    sun(c, 250, 450, 90, lt, "#F6B93B")
    skyline(c, 1000, seed=7, cols=("#A0694A", "#8A5638", "#B98560"))
    skyline(c, 1250, seed=11, cols=("#7C4E36", "#6A4230", "#8A5A40"))
    rect(c, -300, 1250, W + 600, 900, fill("#6B4A36"))
    shop_front(c, 540, 1420, 520, lt)
    # map pin
    p = pop(lt, 0.3, 0.5)
    c.save(); c.translate(540, 330 + math.sin(lt * 3) * 10); c.scale(p, p)
    pin = skia.Path(); pin.moveTo(0, 150); pin.cubicTo(-120, 30, -110, -110, 0, -110); pin.cubicTo(110, -110, 120, 30, 0, 150)
    c.drawPath(pin, fill("#B9402E")); circle(c, 0, -20, 42, fill("#FFF3D6"))
    c.restore()
    c.save(); c.translate(540, 560); c.scale(p, p)
    rrect(c, -200, -50, 400, 100, 26, fill("#FFF3D6")); draw_text(c, "মিরপুর", 0, 28, 72, "#3A2A1E", "b")
    c.restore()
    c.restore()


def sc_father(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 900, 1.0), (D, 540, 840, 1.45)])
    bg_dots(c, "#7A3B2E", "#6A3226", step=80, r=12)
    vignette(c, 0.5)
    # frame
    rrect(c, 250, 460, 580, 700, 20, fill("#000000", 0.3))
    rrect(c, 240, 440, 580, 700, 20, fill("#6A4526"))
    rrect(c, 275, 475, 510, 630, 8, fill("#E8D6AE"))
    c.save(); c.clipRect(skia.Rect.MakeXYWH(275, 475, 510, 630))
    bg_solid(c, "#D9C396", 0)
    person(c, 530, 1130, 1.05, skin=SKIN["old"], shirt="#EFE6D0", hair="#9A948A", style="cap", mustache=True, t=lt, mouth="smile")
    c.restore()
    c.drawRect(skia.Rect.MakeXYWH(275, 475, 510, 630), fill("#7A5A2A", 0.12))
    # key hanging
    kp = ease_out(prog(lt, 0.6, 1.4))
    c.save(); c.translate(530, 1150 + 0); c.rotate(math.sin(lt * 2.5) * 4)
    line(c, 0, 0, 0, 100 * kp, "#C9A24A", 8)
    circle(c, 0, 100 * kp + 30, 36 * kp, stroke("#E3B94D", 14))
    c.restore()
    sparkle(c, 640, 560, 34 * (0.6 + 0.4 * math.sin(lt * 5)), "#FFF3D6", lt * 60)
    c.restore()


def sc_clock_old(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 760, 1.0), (D, 540, 700, 1.5)])
    bg_solid(c, "#8C9A63")
    for i in range(14):
        circle(c, (i * 197) % 1200 - 60, (i * 331) % 1900, 70 + (i * 17) % 60, fill("#7A8854", 0.5))
    # cobweb
    for k in range(4):
        line(c, -20, -20, 260 - k * 10, 20 + k * 90, "#F2EDE0", 3, 0.7)
    wall_clock(c, 540, 760, 300, minutes=lt * 1.2 + 10, t=lt, hour_extra=300)
    # dust sparkles
    for i in range(10):
        circle(c, (i * 113 + lt * 20) % 1000 + 40, (i * 191 + lt * 14) % 1400 + 100, 5, fill("#F2EDE0", 0.5))
    c.restore()


def sc_tries(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 900, 1.0), (D, 540, 860, 1.12)])
    bg_stripes(c, "#C8643B", "#BB5A33", w=110)
    # floor
    rect(c, -300, 1230, W + 600, 700, fill("#6A3A24"))
    sw = math.sin(lt * 6) * 60
    zahid(c, 540, 1230, lt, mouth="open", mouth_open=0.7, hl=(-170 + sw, -190), hr=(170 - sw, -170), brow=0.6, sweat=True)
    items = [
        (3, 220, 560, "tag"), (4, 860, 520, "flyer"), (4.6, 180, 900, "banner"), (5.2, 880, 880, "tool")]
    gone = pop(lt, S.w(6, 6), 0.3)
    for (wi, x, y, kind) in items:
        tt = S.w(6, int(wi)) if wi == int(wi) else S.w(6, int(wi)) + 0.4
        p = pop(lt, tt, 0.4)
        out = ease(prog(lt, S.w(6, 6), S.w(6, 6) + 0.35))
        sc_ = p * (1 - out)
        if sc_ <= 0.01:
            continue
        c.save(); c.translate(x, y + math.sin(lt * 3 + x) * 12); c.scale(sc_, sc_)
        if kind == "tag":
            tag_price(c, 0, 0, 1.5, "৩০% ছাড়" if False else "ছাড়!", -12)
        elif kind == "flyer":
            c.rotate(0.15); rrect(c, -90, -120, 180, 240, 10, fill("#F7F0DC")); rect(c, -70, -95, 140, 70, fill("#E8B23A"))
            for i in range(4):
                line(c, -70, -10 + i * 28, 70 - (i % 2) * 30, -10 + i * 28, "#8A7A5E", 6)
        elif kind == "banner":
            rrect(c, -150, -60, 300, 120, 14, fill("#F3E3C3")); draw_text(c, "অফার", 0, 28, 80, "#B9402E", "b")
        else:
            c.rotate(-0.6); rrect(c, -14, -120, 28, 180, 8, fill("#C9A24A")); rrect(c, -22, 40, 44, 90, 10, fill("#3A2A1E"))
        c.restore()
    q = pop(lt, S.w(6, 6) + 0.2, 0.5)
    if lt > S.w(6, 6) + 0.2:
        c.save(); c.translate(540, 520); c.scale(q, q)
        circle(c, 0, -30, 150, fill("#FFF3D6", 0.95))
        draw_text(c, "?", 0, 80, 280, "#B9402E", "b")
        c.restore()
    c.restore()


def sc_untimed(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 940, 1.0), (D, 640, 900, 1.25)])
    bg_planks(c, "#7C6B3F", "#6A5A32", ph=150)
    rect(c, 0, 1240, W, 700, fill("#4A3A24"))
    # work bench
    rrect(c, 120, 1160, 840, 70, 12, fill("#9A7A44"))
    zahid(c, 480, 1240, lt, mouth="flat", hl=(60, -110), hr=(160, -120), look=(0, 0.8))
    phone(c, 640, 1090, 150, 300, rot=1.2, state="bare", scale=0.75)
    wall_clock(c, 840, 420, 100, minutes=lt, t=lt, hour_extra=60)
    p = pop(lt, S.w(7, 4), 0.45)
    c.save(); c.translate(230, 700); c.scale(p, p)
    stopwatch(c, 0, 0, 110, sec=0)
    cross_mark(c, 0, 0, 110, "#C0392B", prog(lt, S.w(7, 4) + 0.3, S.w(7, 4) + 0.8))
    c.restore()
    c.restore()


def sc_ad_old(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 880, 1.0), (D, 540, 840, 1.4)])
    bg_bricks(c, "#A8503A", "#6A3426", bw=170, bh=64)
    p = prog(lt, S.w(8, 4) - 0.1, S.w(8, 8) + 0.5)
    sw = math.sin(lt * 1.5) * 1.2
    c.save(); c.translate(540, 700); c.rotate(sw * math.pi / 180); c.translate(-540, -700)
    banner_text(c, 540, 860, 900, 520, [("দ্রুত ও", "#B9402E", 1.15), "নির্ভরযোগ্য", ("মোবাইল সার্ভিস", "#3F5E45", 1.0)], 110, lt, reveal=ease(p))
    c.restore()
    c.restore()


def sc_fast_q(c, lt, D, S):
    k = 1.0 + 0.1 * math.sin(lt * 2)
    c.save(); camera(c, lt, [(0, 540, 900, 1.25), (0.5, 540, 900, 1.0), (D, 540, 880, 1.2)])
    bg_rays(c, 540, 820, "#2E2A27", "#4A3A22", lt, n=24, speed=25)
    for i in range(10):
        yy = 450 + i * 90
        line(c, ((lt * 1500 + i * 311) % 1700) - 300, yy, ((lt * 1500 + i * 311) % 1700) + 180, yy, "#F2D16B", 8, 0.5)
    p = pop(lt, 0.1, 0.4)
    c.save(); c.translate(540, 840); c.scale(p, p); c.rotate(-0.05)
    draw_text(c, "দ্রুত", -80, 0, 300, "#F2D16B", "b", outline="#000000", ow=26)
    draw_text(c, "?", 330, 40, 430, "#E0583B", "b", outline="#000000", ow=26)
    c.restore()
    p2 = pop(lt, 0.9, 0.4)
    c.save(); c.translate(540, 1200); c.scale(p2, p2)
    stopwatch(c, 0, 0, 110, sec=lt * 90)
    c.restore()
    c.restore()


def sc_daily(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 900, 1.0), (D, 540, 900, 1.12)])
    shop_interior(c, lt)
    zahid(c, 330, 1180, lt, mouth="smile", hl=(-20, -120), hr=(-60, -80))
    counter_front(c)
    # queue of customers walking in
    for i in range(3):
        x = lerp(1500 + i * 300, 650 + i * 150, ease_out(prog(lt, 0.0, 1.5)))
        cust(c, x, 1300, lt, kind=1 + i, s=0.9, legs=False, mouth="flat")
    # calendar tick
    c.restore()


def sc_counter_talk(c, lt, D, S):
    """sentences 11-13 : customer asks, Zahid answers, customer asks again"""
    t11, t12, t13 = S.st(11), S.st(12), S.st(13)
    c.save()
    camera(c, lt, [(0, 540, 880, 1.0), (t11 + 0.6, 760, 800, 1.2), (t12, 360, 800, 1.2), (t13, 760, 820, 1.3), (D, 540, 880, 1.0)])
    shop_interior(c, lt)
    talking_z = t12 <= lt < t12 + 1.5
    talking_c = (t11 <= lt < t12 - 0.5) or (t13 <= lt < t13 + 1.5)
    zahid(c, 330, 1180, lt, mouth="talk" if talking_z else ("sad" if lt > t13 + 0.8 else "smile"), hl=(-20, -120), hr=(-60, -80), sweat=lt > t13 + 0.8, brow=0.9 if lt > t13 + 0.8 else 0, look=(1, 0))
    counter_front(c)
    cust(c, 790, 1290, lt, kind=1, mouth="talk" if talking_c else "flat", hl=(-150, -260), hr=(110, 20), look=(-1, 0))
    phone(c, 640, 960, 190, 380, rot=-0.15, state="cracked", scale=0.75, crack=1)
    if lt < t12 - 0.05:
        bubble(c, 750, 620, "ভাই, কতক্ষণ লাগবে?", t11 + 0.35, lt, size=60, tail=(0.3, 1), maxw=430)
    if lt >= t12 - 0.05 and lt < t13 - 0.1:
        bubble(c, 330, 620, "হয়ে যাবে।", t12, lt, size=64, tail=(0.3, 1), maxw=420, bg="#E7F0CF")
    if lt >= t13:
        bubble(c, 750, 680, "কখন?", t13 + 0.1, lt, size=90, tail=(-0.3, 1), maxw=500)
        qs = pop(lt, t13 + 0.5, 0.4)
        question_mark(c, 560, 450, 190 * qs, "#B9402E", -10)
    c.restore()


def sc_no_answer(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 1000, 1.0), (D, 540, 700, 1.7)])
    bg_solid(c, "#CFAE7E")
    bg_dots(c, "#CFAE7E", "#C29E6C", step=60, r=7)
    zahid(c, 540, 1280, lt, mouth="flat", brow=1.0, hl=(-40, -400), hr=(150, 0), look=(math.sin(lt * 2), -0.6), sweat=True)
    for i, (dx, dy) in enumerate(((-250, -80), (260, -140), (-170, 130))):
        qs = pop(lt, 0.2 + i * 0.3, 0.4)
        question_mark(c, 540 + dx, 650 + dy + math.sin(lt * 3 + i) * 10, 180 * qs, "#B9402E", (i - 1) * 14)
    bubble(c, 540, 380, "...", 0.3, lt, size=110, tail=(0, 1), maxw=300)
    c.restore()


def sc_leave(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 400, 1000, 1.05), (D * 0.35, 520, 1000, 1.0), (D, 1500, 1000, 1.05)])
    bg_grad(c, "#EBC089", "#F6E1B8")
    rect(c, -300, 1300, 2800, 900, fill("#7B6A55"))
    rect(c, -300, 1290, 2800, 18, fill("#B8A58A"))
    skyline(c, 1000, seed=21, cols=("#C49A70", "#B58A62", "#D0A97E"), x0=-400, x1=2500)
    shop_front(c, 300, 1330, 520, lt)
    zahid(c, 300, 1260, lt, s=0.55, mouth="sad", brow=0.8)
    # big shop
    shop_front(c, 1550, 1330, 800, lt, sign="বড় মোবাইল শপ", wall="#B7432F", awn1="#F2D16B", awn2="#FFF3D6")
    sparkle(c, 1250, 800, 40, "#FFF3D6", lt * 60); sparkle(c, 1830, 780, 40, "#FFF3D6", lt * 60 + 20)
    # customer walking
    p = ease(prog(lt, 0.4, D - 0.4))
    x = lerp(420, 1480, p)
    cust(c, x, 1180, lt, kind=1, s=0.62, legs=True, walk=lt * 9, mouth="flat", hr=(60, -60), hl=(-100, 30))
    phone(c, x + 50 * 0.62, 1080, 120, 240, state="cracked", scale=0.6, crack=1)
    c.restore()


def sc_girl_arrive(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 900, 1.0), (D, 640, 900, 1.2)])
    bg_grad(c, "#F0B27A", "#F7DDB0")
    sun(c, 900, 420, 100, lt, "#F4A63A")
    rect(c, -300, 1300, W + 600, 700, fill("#8A7058"))
    # shop door right
    rect(c, 700, 560, 380, 740, fill("#B7432F"))
    rect(c, 740, 700, 300, 600, fill("#4A2E1F"))
    rect(c, 740, 700, 300, 600, rad_grad(890, 1000, 260, [("#F2C36B", 0.5), ("#F2C36B", 0.0)]))
    signboard(c, 890, 620, 320, 80, "সার্ভিসিং", bg="#3F5E45", size=48)
    x = lerp(-150, 520, ease_out(prog(lt, 0.0, D * 0.9)))
    # bag
    rrect(c, x - 80, 940, 160, 220, 24, fill("#B9402E"))
    girl(c, x, 1230, lt, s=0.8, legs=True, walk=lt * 8, mouth="smile", hl=(-120, 40), hr=(120, 40))
    c.restore()


def sc_exam(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 880, 1.0), (D, 540, 820, 1.2)])
    bg_lines_paper(c)
    p = pop(lt, 0.1, 0.4)
    calendar(c, 400, 760, 520, 560, "কাল", marks=(), hl=(1, 1), rows=5)
    cx = 400 + 0
    # circled tomorrow
    cp = prog(lt, 0.4, 0.9)
    if cp > 0:
        pp = skia.Path(); pp.addOval(skia.Rect.MakeXYWH(400 - 150 + 3 * 68 - 44, 760 - 280 + 130 + 1 * 80 + 40 - 40, 90, 70))
        c.drawPath(pp, stroke("#B9402E", 10))
    c.save(); c.translate(790, 1000); c.rotate(0.12); c.scale(p, p)
    rrect(c, -170, -230, 340, 460, 14, fill("#FFFDF4")); rrect(c, -170, -230, 340, 460, 14, stroke("#3A2A1E", 5))
    draw_text(c, "পরীক্ষা", 0, -150, 70, "#B9402E", "b")
    for i in range(6):
        line(c, -120, -90 + i * 50, 120 - (i % 2) * 40, -90 + i * 50, "#8A7A5E", 6)
    c.restore()
    # alarm clock
    a = pop(lt, 0.6, 0.4)
    c.save(); c.translate(230, 1130); c.scale(a, a); c.rotate(math.sin(lt * 30) * 0.06)
    circle(c, -50, -85, 36, fill("#B9402E")); circle(c, 50, -85, 36, fill("#B9402E"))
    circle(c, 0, 0, 100, fill("#B9402E")); circle(c, 0, 0, 78, fill("#F6EDD8"))
    line(c, 0, 0, 0, -50, "#2A1A10", 8); line(c, 0, 0, 36, 10, "#2A1A10", 8)
    c.restore()
    c.restore()


def sc_notes(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 880, 1.0), (D, 540, 840, 1.25)])
    bg_solid(c, "#6F8447")
    bg_dots(c, "#6F8447", "#7C9453", step=64, r=8)
    phone(c, 540, 860, 420, 840, rot=0, state="notes", t=lt, title="পড়া")
    for i in range(5):
        p = ease_out(prog(lt, i * 0.12, i * 0.12 + 0.5))
        a = i * 2 * math.pi / 5 + 0.6
        x = lerp(540 + math.cos(a) * 700, 540 + math.cos(a) * 380, p)
        y = lerp(860 + math.sin(a) * 700, 860 + math.sin(a) * 420, p)
        c.save(); c.translate(x, y); c.rotate(a)
        rrect(c, -60, -44, 120, 88, 8, fill(["#B9402E", "#E8B23A", "#F3E3C3", "#C8643B", "#8A5A34"][i]))
        rect(c, -54, -38, 8, 76, fill("#000000", 0.2))
        c.restore()
    c.restore()


def sc_cracked(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 880, 0.95), (D, 600, 800, 1.7)])
    bg_solid(c, "#2E2A27")
    c.drawRect(skia.Rect.MakeXYWH(-300, -300, W + 600, 2400), rad_grad(540, 860, 700, [("#E8B070", 0.45), ("#000000", 0.0)]))
    phone(c, 540, 880, 460, 920, rot=-3, state="cracked", t=lt, crack=prog(lt, 0.0, 0.8))
    c.restore()
