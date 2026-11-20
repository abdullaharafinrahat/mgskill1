# Scenes part 2 (the girl's question -> Zahid's experiment -> new promise)
import math
import skia
from v_lib import *
from v_props import *
from v_scenes1 import *


def sc_girl_ask(c, lt, D, S):
    t20, t21 = S.st(20), S.st(21)
    c.save()
    camera(c, lt, [(0, 540, 900, 1.0), (t20 + 0.5, 780, 800, 1.2), (t21 - 0.1, 400, 800, 1.2), (D, 540, 880, 1.0)])
    shop_interior(c, lt, night=True, clock_min=45)
    talking_z = t21 <= lt < t21 + 1.3
    talking_g = t20 <= lt < t20 + 2.8
    zahid(c, 330, 1180, lt, mouth="talk" if talking_z else "smile", hl=(-20, -120), hr=(-60, -80))
    counter_front(c, night=True)
    girl(c, 790, 1290, lt, mouth="talk" if talking_g else "flat", hl=(-150, -250), hr=(110, 20), look=(-1, 0), s=0.95, brow=0.5)
    phone(c, 640, 960, 190, 380, rot=-0.15, state="cracked", scale=0.75)
    if lt < t21 - 0.05:
        bubble(c, 690, 580, "ভাইয়া, আজ রাতের মধ্যে পাব?", t20 + 0.3, lt, size=56, tail=(0.3, 1), maxw=430)
    if lt >= t21 - 0.05:
        bubble(c, 330, 620, "হয়ে যাবে।", t21, lt, size=64, tail=(0.3, 1), maxw=420, bg="#E7F0CF")
    c.restore()


def sc_girl_retort(c, lt, D, S):
    w = S.w
    c.save()
    camera(c, lt, [(0, 540, 760, 1.35), (w(22, 10) - 0.2, 540, 760, 1.3), (w(22, 11), 540, 880, 1.0), (D, 540, 880, 1.0)])
    bg_grad(c, "#E7C8A0", "#F2DFC0")
    bg_stripes(c, "#E7C8A0", "#E0BE92", w=120, tilt=8)
    girl(c, 540, 1120, lt, mouth="talk" if lt < w(22, 16) + 0.5 else "flat", brow=0.8, hl=(-110, -40), hr=(110, -40), look=(0, 0))
    phone(c, 700, 960, 150, 300, rot=0.3, state="cracked", scale=0.8)
    if lt < w(22, 10) - 0.3:
        bubble(c, 540, 260, "হয়ে যাবে মানে কখন?", 0.1, lt, size=76, tail=(0, 1), maxw=800)
    # two choices
    t1, t2 = w(22, 11), w(22, 14)
    p1 = pop(lt, t1, 0.4)
    c.save(); c.translate(250, 1420); c.scale(p1, p1)
    rrect(c, -210, -150, 420, 300, 30, fill("#6F8447")); rrect(c, -210, -150, 420, 300, 30, stroke("#3A4A22", 6))
    # chair
    rect(c, -50, -80, 20, 120, fill("#F3E3C3")); rect(c, -50, 10, 130, 20, fill("#F3E3C3")); rect(c, 60, 10, 20, 100, fill("#F3E3C3"))
    rect(c, -50, 30, 14, 80, fill("#F3E3C3"))
    draw_text(c, "অপেক্ষা", 0, 125, 64, "#FFF3D6", "b")
    c.restore()
    p2 = pop(lt, t2, 0.4)
    c.save(); c.translate(830, 1420); c.scale(p2, p2)
    rrect(c, -210, -150, 420, 300, 30, fill("#B9402E")); rrect(c, -210, -150, 420, 300, 30, stroke("#6A2418", 6))
    rect(c, -60, -100, 120, 180, fill("#FFF3D6")); rect(c, -48, -88, 96, 156, fill("#7A3B2E")); circle(c, 30, 0, 8, fill("#F2D16B"))
    draw_text(c, "অন্য দোকান", 0, 125, 56, "#FFF3D6", "b")
    c.restore()
    # swinging arrow between
    if lt > t2:
        p = ease(prog(lt, t2 + 0.3, t2 + 0.8))
        line(c, 540, 1270, 540 + 120 * p, 1270, "#B9402E", 14)
    c.restore()


def sc_zahid_think(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 930, 1.0), (D, 540, 700, 1.6)])
    bg_solid(c, "#3A2A20")
    c.drawRect(skia.Rect.MakeXYWH(-300, -300, W + 600, 2400), rad_grad(540, 700, 800, [("#F2B86B", 0.4), ("#000000", 0.5)]))
    zahid(c, 540, 1230, lt, mouth="flat", brow=0.5, hl=(-60, -170), hr=(60, 0), look=(0, 0.3))
    for i, x in enumerate((220, 860)):
        p = ease_out(prog(lt, 0.2 + i * 0.3, 1.4))
        c.save(); c.translate(x, 700 - p * 80)
        c.rotate(0)
        draw_text(c, "কখন?", 0, 0, 90, "#F6E7B4", "b", a=0.75 * p)
        c.restore()
    c.restore()


def sc_realize(c, lt, D, S):
    w = S.w
    c.save(); camera(c, lt, [(0, 540, 900, 1.0), (w(24, 5), 540, 760, 1.25), (D, 540, 820, 1.0)])
    bg_rays(c, 540, 600, "#E8B64A", "#F0CA6C", lt, n=16, speed=6)
    zahid(c, 540, 1230, lt, mouth="smile", brow=-0.4, hl=(-160, -230), hr=(150, 0), look=(0, -0.5))
    p = pop(lt, w(24, 4), 0.5)
    c.save(); c.translate(540, 470); c.scale(p, p)
    bulb(c, 0, 0, 90, 1.0)
    c.restore()
    # phone + wrench crossed out
    q = pop(lt, w(24, 8), 0.4)
    if lt > w(24, 8):
        c.save(); c.translate(250, 1380); c.scale(q, q)
        rrect(c, -110, -110, 220, 220, 30, fill("#FFF3D6")); rrect(c, -110, -110, 220, 220, 30, stroke("#3A2A1E", 6))
        phone(c, -35, 0, 80, 150, state="cracked", scale=0.9)
        c.save(); c.rotate(0.7); rrect(c, 28, -70, 22, 130, 8, fill("#7A7A72")); circle(c, 39, -76, 26, fill("#7A7A72")); c.restore()
        cross_mark(c, 0, 0, 100, "#C0392B", prog(lt, w(24, 9), w(24, 11)))
        c.restore()
    c.restore()


def sc_want_back(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 900, 1.0), (D, 540, 840, 1.2)])
    bg_grad(c, "#F3B896", "#F8E0BE")
    bg_dots(c, "#F3B896", "#EEA982", step=76, r=10, a=0.6)
    cust(c, 540, 1230, lt, kind=2, mouth="smile", brow=0.4, hl=(-120, -40), hr=(130, -40), look=(0, -0.6))
    # thought bubble
    p = pop(lt, 0.3, 0.5)
    c.save(); c.translate(540, 420); c.scale(p, p)
    for r_, x_, y_ in ((50, -150, 330), (34, -110, 400)):
        circle(c, x_ + 100, y_ - 200 + 60, r_ * 0.4, fill("#FFF8E7"))
    circle(c, -50, 300 - 160, 20, fill("#FFF8E7")); circle(c, -10, 240 - 150, 30, fill("#FFF8E7"))
    oval(c, 0, 0, 340, 200, fill("#FFF8E7")); oval(c, 0, 0, 340, 200, stroke("#3A2A1E", 6))
    phone(c, -150, 0, 110, 220, state="on", scale=0.8)
    # arrow back to hand
    ap = ease(prog(lt, 1.0, 1.7))
    line(c, -60, 0, -60 + 120 * ap, 0, "#B9402E", 12)
    if ap > 0.7:
        poly(c, [(80, -26), (115, 0), (80, 26)], fill("#B9402E"))
    wall_clock(c, 190, 0, 100, minutes=lt * 14, t=lt, hour_extra=300)
    c.restore()
    c.restore()


def sc_night_clock(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 1000, 1.0), (D * 0.4, 540, 1000, 1.05), (D * 0.75, 700, 500, 1.2), (D, 800, 380, 2.2)])
    shop_interior(c, lt, night=True, clock_min=10)
    zahid(c, 330, 1180, lt, mouth="smile", hl=(-20, -120), hr=(-60, -80), look=(0.6, -0.8 * ease(prog(lt, 1.5, 2.5))), tilt=0)
    counter_front(c, night=True)
    # lamp
    circle(c, 150, 330, 240, rad_grad(150, 330, 240, [("#FFD08A", 0.4), ("#FFD08A", 0.0)]))
    line(c, 150, -100, 150, 280, "#2A1A10", 6)
    c.drawPath(skia.Path().addCircle(150, 300, 38), fill("#FFD966"))
    # shutter half down at the front
    sh = ease(prog(lt, 0.2, 1.6)) * 0.55
    c.restore()
    # overlay shutter (screen space) dropping then staying half
    sp = ease(prog(lt, 0.1, 1.4)) * 0.28
    if lt < D * 0.7:
        hh = H * sp
        rect(c, 0, 0, W, hh, fill("#8C8B84"))
        k = 0
        while k < hh:
            line(c, 0, k, W, k, "#6A6962", 5)
            k += 40
        rect(c, 0, hh - 16, W, 20, fill("#5A5953"))


def sc_ten_phones(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 880, 1.0), (D, 540, 860, 1.15)])
    bg_planks(c, "#8A6A3E", "#7A5A32", ph=160)
    rect(c, 40, 1000, 1000, 40, fill("#5A3A22"))
    n = 10
    for i in range(n):
        col_, row = i % 5, i // 5
        x = 140 + col_ * 200
        y = 560 + row * 400
        t0 = 0.2 + i * 0.22
        st = "on" if lt > t0 + 0.25 else "cracked"
        p = pop(lt, t0 - 0.2, 0.3)
        phone(c, x, y, 150, 300, state=st, t=lt, scale=p, crack=1)
        if t0 + 0.25 < lt < t0 + 0.6:
            sparkle(c, x, y, 36 * (1 - prog(lt, t0 + 0.25, t0 + 0.6)), "#FFF3D6", lt * 100)
    done = sum(1 for i in range(n) if lt > 0.2 + i * 0.22 + 0.25)
    c.save(); c.translate(540, 1240)
    rrect(c, -220, -80, 440, 160, 40, fill("#FFF3D6")); rrect(c, -220, -80, 440, 160, 40, stroke("#4A2B15", 6))
    draw_text(c, bn(done) + "/১০ ফোন", 0, 30, 84, "#B9402E", "b")
    c.restore()
    c.restore()


def sc_notebook(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 760, 1.0), (D, 540, 1000, 1.25)])
    bg_planks(c, "#9A7040", "#8A6234", ph=170)
    c.save(); c.translate(540, 1000); c.rotate(-0.03)
    rrect(c, -430 + 12, -760 + 16, 860, 1520, 24, fill("#000000", 0.25))
    rrect(c, -430, -760, 860, 1520, 24, fill("#FAF3DC"))
    rect(c, -430, -760, 70, 1520, fill("#B9402E"))
    draw_text(c, "শুরু", -110, -640, 70, "#3A2A1E", "b")
    draw_text(c, "শেষ", 190, -640, 70, "#3A2A1E", "b")
    line(c, -330, -590, 400, -590, "#3A2A1E", 6)
    starts = ["১০:০০", "১১:০০", "১২:১৫", "০১:০০", "০২:০০", "০২:৪৫", "০৩:৩০", "০৪:০০", "০৪:৫০", "০৫:৩০"]
    ends = ["১০:৪৬", "১১:৪২", "১৩:০৫", "০১:৪৪", "০২:৪৮", "০৩:৩০", "০৪:১০", "০৪:৪০", "০৫:৩৭", "০৬:১৩"]
    for i in range(10):
        yy = -520 + i * 118
        line(c, -330, yy + 40, 400, yy + 40, "#B6A98A", 3)
        t0 = 0.2 + i * 0.28
        p = prog(lt, t0, t0 + 0.25)
        q = prog(lt, t0 + 0.2, t0 + 0.5)
        if p > 0:
            c.save(); c.clipRect(skia.Rect.MakeXYWH(-330, yy - 60, 330 * 1 + 0, 120)); c.restore()
            draw_text(c, starts[i], -110, yy + 22, 58, "#3A2A1E", "m", a=p)
        if q > 0:
            draw_text(c, ends[i], 190, yy + 22, 58, "#B9402E", "m", a=q)
    c.restore()
    # pen
    i = min(9, max(0, int((lt - 0.2) / 0.28)))
    py = 1000 - 520 + i * 118
    c.save(); c.translate(900 - 40 * math.sin(lt * 9), py - 200 * 0 + 40)
    c.rotate(0.9); rrect(c, -14, -260, 28, 300, 10, fill("#3A2A1E")); poly(c, [(-14, 40), (14, 40), (0, 80)], fill("#E8B23A"))
    c.restore()
    c.restore()


def sc_chart(c, lt, D, S):
    w = S.w
    c.save()
    camera(c, lt, [(0, 540, 880, 1.0), (w(29, 9) - 0.3, 540, 880, 1.0), (w(29, 9) + 0.3, 420, 760, 1.35), (S.st(30) - 0.1, 420, 760, 1.35), (S.st(30) + 0.4, 790, 900, 1.35), (D, 540, 880, 1.0)])
    bg_lines_paper(c, "#F3EBD2", "#B7A98A")
    draw_text(c, "মিনিট", 90, 330, 54, "#6A5A44", "m", "l")
    vals = [46, 42, 50, 44, 48, 41, 45, 40, 47, 43]
    base = 1330
    for k in range(5):
        yy = base - k * 140
        line(c, 120, yy, 1000, yy, "#B7A98A", 3)
        draw_text(c, bn(k * 10 + 10 if False else 10 * k), 90, yy + 16, 36, "#6A5A44", "m", "r") if False else None
    bw = 70
    for i, v in enumerate(vals):
        x = 150 + i * 88
        gp = ease_out(prog(lt, 0.1 + i * 0.12, 0.9 + i * 0.12))
        h = (v / 50.0) * 800 * gp
        cc = "#C8A15A"
        if i == 2 and lt > w(29, 9):
            cc = "#B9402E"
        if i == 7 and lt > S.st(30) + 0.2:
            cc = "#4F7A3A"
        rrect(c, x, base - h, bw, h, 10, fill(cc))
        draw_text(c, bn(i + 1), x + bw / 2, base + 50, 36, "#6A5A44", "m")
    # labels
    p = pop(lt, w(29, 9), 0.4)
    if lt > w(29, 9):
        c.save(); c.translate(260, base - 800 - 90); c.scale(p, p)
        rrect(c, -150, -60, 300, 110, 28, fill("#B9402E")); draw_text(c, "৫০ মিনিট", 0, 26, 66, "#FFF3D6", "b")
        c.restore()
    p2 = pop(lt, S.st(30) + 0.2, 0.4)
    if lt > S.st(30) + 0.2:
        c.save(); c.translate(150 + 7 * 88 + 35, base - 640 - 90); c.scale(p2, p2)
        rrect(c, -150, -60, 300, 110, 28, fill("#4F7A3A")); draw_text(c, "৪০ মিনিট", 0, 26, 66, "#FFF3D6", "b")
        c.restore()
    c.restore()


def sc_strike(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 900, 1.0), (D, 540, 840, 1.3)])
    bg_grad(c, "#F8DE9A", "#F3C46A")
    sun(c, 180, 330, 110, lt, "#F29A2E")
    for k in range(5):
        circle(c, 740 + k * 60, 300 + (k % 2) * 40, 70, fill("#FFF3D6", 0.7))
    rect(c, -300, 1200, W + 600, 800, fill("#8A6A4A"))
    rect(c, 40, 440, 1000, 760, fill("#E0B27E"))
    banner_text(c, 540, 820, 860, 460, ["দ্রুত ও", "নির্ভরযোগ্য", "মোবাইল সার্ভিস"], 100, lt)
    p = ease(prog(lt, 0.5, 1.5))
    # red strike
    line(c, 130, 640, 130 + 820 * p, 1000, "#C0392B", 22)
    # marker
    mx, my = 130 + 820 * p, 640 + (1000 - 640) * p
    c.save(); c.translate(mx + 30, my + 30); c.rotate(-0.6)
    rrect(c, -22, 0, 44, 220, 10, fill("#3A2A1E")); rrect(c, -22, -30, 44, 50, 6, fill("#C0392B"))
    c.restore()
    c.restore()


def sc_new_banner(c, lt, D, S):
    w = S.w
    c.save(); camera(c, lt, [(0, 540, 880, 1.0), (S.st(33), 540, 880, 1.05), (w(33, 4), 540, 880, 1.45), (w(33, 6), 540, 960, 1.25), (D, 540, 900, 1.1)])
    bg_bricks(c, "#8A9A5B", "#5E6C3E", bw=170, bh=64)
    rp = ease(prog(lt, S.st(33) + 0.0, S.st(33) + 3.2))
    banner_text(c, 540, 880, 940, 640, [("সাধারণ মডেলের", "#3A2A1E", 0.72), ("স্ক্রিন বদলান", "#3A2A1E", 0.9), ("৫০ মিনিটে।", "#B9402E", 1.5), ("না পারলে চার্জ অর্ধেক", "#3F5E45", 0.78)], 90, lt, reveal=rp,
                bg="#FFF8E7", frame="#3F5E45")
    # marker writing
    if lt < S.st(33) + 3.3:
        c.save(); c.translate(100 + 840 * rp, 600 + 520 * (0.5 + 0.5 * math.sin(lt * 4)) * 0.5)
        c.rotate(-0.6); rrect(c, -20, 0, 40, 200, 10, fill("#3A2A1E")); rrect(c, -20, -26, 40, 44, 6, fill("#B9402E"))
        c.restore()
    c.restore()
    # first beat: fresh blank title
    if lt < S.st(33) - 0.2:
        pass


def sc_six(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 900, 1.0), (D, 540, 860, 1.12)])
    shop_interior(c, lt, clock_min=0)
    banner_text(c, 540, 330, 520, 150, [("৫০ মিনিটে", "#B9402E", 0.9)], 80, lt, bg="#FFF8E7", frame="#3F5E45") if False else None
    zahid(c, 220, 1180, lt, s=0.9, mouth="smile", hl=(-20, -120), hr=(-60, -80))
    counter_front(c)
    for i in range(6):
        t0 = 0.2 + i * 0.25
        p = pop(lt, t0, 0.35)
        x = 420 + (i % 3) * 210 + (i // 3) * 100
        y = 1300 + (i // 3) * 40 - 0
        c.save(); c.translate(x, y); c.scale(p, p); c.translate(-x, -y)
        cust(c, x, y, lt, kind=i % 6 + 1, s=0.62, mouth="smile")
        c.restore()
    done = sum(1 for i in range(6) if lt > 0.2 + i * 0.25)
    c.save(); c.translate(870, 500)
    circle(c, 0, 0, 120, fill("#F2D16B")); circle(c, 0, 0, 120, stroke("#4A2B15", 8))
    draw_text(c, bn(done), 0, 50, 150, "#B9402E", "b")
    c.restore()
    c.restore()


def sc_no_price(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 900, 1.0), (D, 540, 840, 1.2)])
    bg_grad(c, "#E7B07A", "#F4DDB0")
    cust(c, 540, 1230, lt, kind=3, mouth="flat", hl=(-120, -30), hr=(130, -30), look=(0, -0.4))
    p = pop(lt, 0.2, 0.4)
    c.save(); c.translate(540, 520); c.scale(p, p)
    tag_price(c, 0, 0, 2.4, "দাম?", -6)
    cross_mark(c, 0, 0, 190, "#C0392B", prog(lt, 0.8, 1.4))
    c.restore()
    c.restore()


def sc_wait_clock(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 960, 1.0), (D, 540, 600, 1.25)])
    shop_interior(c, lt, clock_min=lt * 4)
    counter_front(c)
    for i, k in enumerate((1, 3, 4)):
        cust(c, 250 + i * 290, 1330, lt, kind=k, s=0.7, mouth="flat", look=((0.6, 0.0, -0.6)[i], -1), hl=(-100, 10), hr=(100, 10))
    c.save(); c.translate(540, 560)
    stopwatch(c, 0, 0, 125, sec=lt * 6)
    c.restore()
    c.restore()


def sc_week3(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 880, 1.0), (D, 540, 840, 1.3)])
    bg_solid(c, "#B9402E")
    bg_dots(c, "#B9402E", "#A53A29", step=70, r=9)
    calendar(c, 540, 840, 840, 900, "৩য় সপ্তাহ", hl=(2, 2), rows=5, col1="#3F5E45")
    p = pop(lt, 0.8, 0.45)
    c.save(); c.translate(700, 1130); c.rotate(-0.2); c.scale(p, p)
    rrect(c, -230, -80, 460, 160, 20, stroke("#B9402E", 12)); draw_text(c, "পরীক্ষা", 0, 36, 110, "#B9402E", "b")
    c.restore()
    c.restore()


def sc_rare(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 900, 1.0), (D, 640, 800, 1.35)])
    bg_grad(c, "#E8C48A", "#F6E3B8")
    bg_dots(c, "#E8C48A", "#E0B87A", step=70, r=10, a=0.6)
    zahid(c, 300, 1280, lt, s=0.95, mouth="open", mouth_open=0.6, brow=0.9, hl=(60, -170), hr=(-40, -20), look=(1, 0))
    cust(c, 790, 1280, lt, kind=5, s=0.95, mouth="smile", hl=(-140, -200), hr=(100, 20), look=(-1, 0))
    p = pop(lt, 0.3, 0.5)
    c.save(); c.translate(540, 900); c.scale(p * 0.72, p * 0.72); c.rotate(-0.1 + math.sin(lt * 2) * 0.03)
    # foldable phone (rare model)
    rrect(c, -190 + 8, -250 + 10, 190, 500, 40, fill("#000000", 0.25)); 
    for sgn in (-1, 1):
        rrect(c, sgn * 4 + (-190 if sgn < 0 else 0), -250, 188, 500, 36, fill("#2B2B2B"))
        rrect(c, sgn * 4 + (-182 if sgn < 0 else 8), -240, 172, 480, 28, fill("#E0803F" if sgn < 0 else "#F2C36B"))
    # gem
    poly(c, [(0, -60), (60, -10), (0, 70), (-60, -10)], fill("#B9402E")); poly(c, [(0, -60), (60, -10), (0, 10), (-60, -10)], fill("#E0583B"))
    c.restore()
    for i in range(5):
        sparkle(c, 540 + math.cos(i * 1.3 + lt * 2) * 260, 880 + math.sin(i * 1.3 + lt * 2) * 330, 30 + 12 * math.sin(lt * 5 + i), "#FFF3D6", lt * 80)
    c.restore()
    bp = pop(lt, 0.7, 0.4)
    c.save(); c.translate(540, 420); c.scale(bp, bp)
    rrect(c, -190, -64, 380, 128, 36, fill("#FFF3D6")); rrect(c, -190, -64, 380, 128, 36, stroke("#4A2B15", 6))
    draw_text(c, "বিরল মডেল", 0, 30, 78, "#B9402E", "b")
    c.restore()


def sc_seventy(c, lt, D, S):
    c.save(); camera(c, lt, [(0, 540, 860, 1.0), (D, 540, 840, 1.15)])
    bg_grad(c, "#E0A94A", "#F0CC7A")
    bg_rays(c, 540, 820, "#E0A94A", "#EDBD62", lt, n=14, speed=20)
    # minutes spin 0 -> 70
    m = ease(prog(lt, 0.0, D - 0.15)) * 70
    wall_clock(c, 540, 820, 330, minutes=m, t=lt, hour_extra=300, tick=False)
    p = pop(lt, 0.35, 0.4)
    c.save(); c.translate(540, 1280); c.scale(p, p)
    draw_text(c, "৭০ মিনিট", 0, 0, 150, "#FFF3D6", "b", outline="#4A2B15", ow=24)
    c.restore()
    c.restore()
