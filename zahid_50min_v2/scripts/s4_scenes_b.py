"""Script 4b: scenes 11-14 (night notebook, new sign, six customers, rare phone)."""
import math
from s2_lib import *
from s4_scenes_a import (bg, floor, kf, ph, speak, zahid, customer, girl, counter_front, shelf, thought_cloud, ZS, ZA, SHOP)

# ---------------------------------------------------------------- 11. night: measure ten phones
BAR_V = [46, 48, 44, 50, 42, 47, 45, 40, 49, 43]
ROWS = [("৯:০০", "৯:৪৬"), ("১০:০০", "১০:৪৮"), ("১১:০০", "১১:৪৪"), ("১২:০০", "১২:৫০"), ("২:০০", "২:৪২"),
        ("৩:০০", "৩:৪৭"), ("৪:০০", "৪:৪৫"), ("৫:০০", "৫:৪০")]

def s_night(c, t, d, C, m):
    bg(c, "#3A2A20", "#17100C")
    radial(c, 540, 500, 1000, "#FFC864", "#FFC864", 70, 0)
    dots(c, -100, -100, 1200, 2000, 120, 4, "#FFD58A", 25, oy=t * 4)

    def A(lt):
        floor(c, 1300, "#2B1D14")
        circ(c, 160, 330, 90, "#F7E7B5"); circ(c, 195, 308, 82, "#3A2A20")
        # shutter coming down on the door
        rect(c, 760, 560, 260, 740, "#1B120D")
        rect(c, 760, 560, 260, 740 * ease_io(prog(lt, 0.2, 2.2)), "#8A8F8C")
        for k in range(int(740 * ease_io(prog(lt, 0.2, 2.2)) // 24)): line(c, 760, 575 + k * 24, 1020, 575 + k * 24, "#6C716E", 3)
        glow = 0.5 + 0.5 * math.sin(lt * 3)
        radial(c, 540, 520, 380, "#FFE9A8", "#FFE9A8", int(70 + 40 * glow), 0)
        wall_clock(c, 540, 520, 220, minute=(lt * 12) % 360 + 20, hour=250, rim="#5A3A1E")
        bench_y = 1130
        rect(c, 120, bench_y, 520, 36, "#6B4326", r=8); rect(c, 150, bench_y + 36, 36, 200, "#4E301A"); rect(c, 560, bench_y + 36, 36, 200, "#4E301A")
        zahid(c, 330, 1300, 1.15, facing=1, mood="neutral", t=lt, armF=(25, 15), look=1)
        # gaze lines
        for k in range(6):
            q = (lt * 1.4 + k / 6) % 1.0
            circ(c, lerp(380, 520, q), lerp(840, 560, q), 5, "#FFE9A8", int(220 * (1 - q)))
    ph(c, t, 0, C[1], A, fade=0.4)

    def B(lt):
        draw_text(c, "১০টি ফোন", 540, 330, 90, "#F4B942")
        for i in range(10):
            x = 160 + (i % 5) * 190; y = 620 + (i // 5) * 400
            t0 = 0.1 + 0.2 * i
            p = pop(lt, t0, 0.4)
            scr = "cracked" if lt < t0 + 0.45 else "good"
            if p > 0.01:
                phone(c, x, y, 130, 250, rot=(-4 if i % 2 else 4), screen=scr, s=p)
            if lt > t0 + 0.45:
                check(c, x + 56, y - 150, 54, "#6BC17A", 14, prog(lt, t0 + 0.45, 0.25))
        # screwdriver spinning
        k = (lt * 8) % 1
    ph(c, t, C[1], C[2], B, fade=0.4)

    def Cc(lt):
        nb_p = pop(lt, 0.0, 0.5)
        cx_, cy_, w_, h_ = 540, 760, 780, 900
        with xform(c, 0, 0, 1):
            notebook(c, cx_, cy_, w_, h_ * nb_p, 0)
        draw_text(c, "শুরু", cx_ - 120, cy_ - 360, 56, "#7A3E2B"); draw_text(c, "শেষ", cx_ + 210, cy_ - 360, 56, "#C0574A")
        line(c, cx_ + 40, cy_ - 400, cx_ + 40, cy_ + 400, "#D9CDB2", 3)
        per = (d_c := (C[2] - C[1])) / (len(ROWS) + 1)
        for i, (a_, b_) in enumerate(ROWS):
            ty = 0.5 + i * (per * 0.9)
            yy = cy_ - 270 + i * 98
            if lt > ty:
                q = prog(lt, ty, 0.35)
                with alpha_layer(c, q):
                    draw_text(c, a_, cx_ - 120, yy, 52, "#2B2118"); draw_text(c, b_, cx_ + 210, yy, 52, "#B3361F")
        # pen
        k = min(len(ROWS) - 1, max(0, int((lt - 0.5) / (per * 0.9))))
        px, py = cx_ + 280 + 10 * math.sin(lt * 14), cy_ - 270 + k * 98 - 20
        with xform(c, px, py, 1, 35):
            rect(c, -10, -150, 20, 140, "#D1452F", r=8); poly(c, [(-10, -10), (10, -10), (0, 24)], "#2B2118")
    ph(c, t, C[2], C[3], Cc, fade=0.4)

    def D(lt):
        base = 1250; x0 = 140
        draw_text(c, "সময় (মিনিট)", 540, 330, 66, "#F4B942")
        line(c, 90, base + 6, 990, base + 6, "#E9DCC0", 8)
        for i, v in enumerate(BAR_V):
            hgt = (v - 30) * 30 * ease_out(prog(lt, 0.1 * i, 0.5))
            colr = "#F4B942"
            if i == 3 and lt > 2.7: colr = "#E4572E"
            if i == 7 and lt > C[4] - C[3] + 0.3: colr = "#6BC17A"
            rect(c, x0 + i * 85, base - hgt, 62, hgt, colr, r=10)
        if lt > 2.7:
            tag(c, x0 + 3 * 85 + 31, base - 20 * 30 - 90, "৫০ মিনিট", 52, "#E4572E", "#FFFFFF", pop(lt, 2.7, 0.4))
        if lt > C[4] - C[3] + 0.3:
            tag(c, x0 + 7 * 85 + 31, base - 10 * 30 - 90, "৪০ মিনিট", 52, "#3F9B54", "#FFFFFF", pop(lt, C[4] - C[3] + 0.3, 0.4))
    ph(c, t, C[3], d, D, fade=0.4)

def cam_night(t, d, C):
    return kf(t, [(0, 1.0, 540, 800), (2.6, 1.05, 500, 780), (C[1] - 0.3, 1.4, 540, 600), (C[1] + 0.5, 1.0, 540, 800),
                  (C[2] - 0.3, 1.0, 540, 800), (C[2] + 0.6, 1.15, 540, 780), (C[3] - 0.3, 1.2, 540, 780),
                  (C[3] + 0.6, 1.0, 540, 800), (d, 1.18, 540, 820)])

# ---------------------------------------------------------------- 12. new sign
def s_sign(c, t, d, C, m):
    bg(c, "#FAE0A0", "#F08A4B")
    rays(c, 540, 1000, t, "#FFFFFF", 40, speed=4)
    circ(c, 540, 1020, 330, "#FFF3C9", 220); circ(c, 540, 1020, 420, "#FFF3C9", 60)
    floor(c, 1300, "#B8763F")
    line(c, 200, 880, 200, 1300, "#6B4326", 36); line(c, 880, 880, 880, 1300, "#6B4326", 36)
    bx, by, bw, bh = 540, 640, 880, 520
    # old board / new board flip
    flip_out = ease_in(prog(t, C[1] + 0.05, 0.4)); flip_in = ease_out(prog(t, C[1] + 0.45, 0.45))
    if flip_out < 1:
        with xform(c, bx, by, 1, 0, sx=max(1 - flip_out, 0.01), sy=1):
            rect(c, -bw / 2 + 10, -bh / 2 + 16, bw, bh, "#000000", r=30, a=70, blur=12)
            rect(c, -bw / 2, -bh / 2, bw, bh, "#2B2118", r=30); rect(c, -bw / 2 + 24, -bh / 2 + 24, bw - 48, bh - 48, "#F4B942", r=20, stroke=6)
            draw_text(c, "দ্রুত ও নির্ভরযোগ্য", 0, -20, 74, "#F4B942"); draw_text(c, "মোবাইল সার্ভিস", 0, 90, 74, "#FFFFFF")
            for k_, (x1, x2, yy) in enumerate(((-380, 380, -50), (-300, 300, 62))):
                q = prog(t, 1.2 + 0.6 * k_, 0.5)
                if q > 0: line(c, x1, yy, lerp(x1, x2, q), yy - 8 * q, "#E4572E", 16)
    if flip_in > 0.01:
        with xform(c, bx, by, 1, 0, sx=max(flip_in, 0.01), sy=1):
            rect(c, -bw / 2 + 10, -bh / 2 + 16, bw, bh, "#000000", r=30, a=70, blur=12)
            rect(c, -bw / 2, -bh / 2, bw, bh, "#FFF8E6", r=30); rect(c, -bw / 2 + 24, -bh / 2 + 24, bw - 48, bh - 48, "#2B2118", r=20, stroke=6)
            def reveal(x, y, w_, h_, p):
                c.save(); c.clipRect(skia.Rect.MakeXYWH(x, y, w_ * p, h_))
            t2 = t - C[2]
            p1 = prog(t2, 0.1, 2.3)
            reveal(-bw / 2, -200, bw, 120, p1); draw_text(c, "সাধারণ মডেলের স্ক্রিন বদলান", 0, -120, 58, "#2B2118"); c.restore()
            reveal(-bw / 2, -110, bw, 190, p1); draw_text(c, "৫০ মিনিটে", 0, 40, 130, "#D1452F"); c.restore()
            p2 = prog(t2, 3.0, 1.3)
            reveal(-bw / 2, 90, bw, 120, p2); draw_text(c, "না পারলে চার্জ অর্ধেক।", 0, 170, 62, "#2F6B3A"); c.restore()
    if t > C[2] + 4.4:
        for i in range(6):
            sparkle(c, bx - 380 + i * 150, by - 280 + 30 * math.sin(t * 4 + i), 24 * pop(t, C[2] + 4.4 + 0.08 * i, 0.4), "#FFFFFF", 255)
    # Zahid with marker
    wr = 150 + 8 * math.sin(t * 6) if t > C[1] else 20
    hx, hy = zahid(c, 940, 1320, 0.85, facing=-1, mood="happy" if t > C[2] + 3 else "neutral", t=t,
                   armF=(wr * ease_io(prog(t, C[1] - 0.3, 0.5)) + 20, -10), look=-1)
    if t > C[1] - 0.2:
        with xform(c, hx, hy, 1, 30):
            rect(c, -7, -50, 14, 60, "#D1452F", r=5)

def cam_sign(t, d, C):
    return kf(t, [(0, 1.0, 560, 800), (C[1], 1.1, 600, 720), (C[2], 1.2, 650, 700), (d, 1.3, 650, 700)])

# ---------------------------------------------------------------- 13. six customers watch the clock
def s_six(c, t, d, C, m):
    bg(c, "#DDE7B4", "#A5C078"); rays(c, 540, 460, t, "#FFFFFF", 45, speed=-3)
    floor(c, 1300, "#8C7A52")
    rect(c, -2600, 1300, 6400, 14, "#6F5F3E")
    # clock
    ck = 1.0 if t > 0.1 else 0.01
    wt = ease_io(prog(t, C[2], d - C[2])) * 300
    wall_clock(c, 540, 480, 240, minute=(t * 30) % 360 if t < C[2] else (t * 70) % 360, hour=t * 3, rim="#5A3A1E",
               wedge_to=wt if t > C[2] else None, wedge_col="#E4572E")
    shirts = ["#8C3B2E", "#F1EBDD", "#D6A23A", "#6B8E4E", "#C0574A", "#E9C7A0"]
    for i in range(6):
        x = 150 + i * 155; t0 = 0.15 + 0.3 * i
        p = pop(t, t0, 0.45)
        if p < 0.01: continue
        look_up = t > C[2]
        with xform(c, x, 1290, p):
            if i % 2 == 0:
                customer(c, 0, 0, 0.64, 1, shirt=shirts[i], mood="neutral" if not look_up else "neutral", t=t + i, armF=(8, 5))
            else:
                person(c, 0, 0, 0.64, skin="#C28A5E" if i != 3 else "#A66B43", shirt=shirts[i], pants="#4A4038", hair="#1E1612",
                       style="short", facing=1, t=t + i, armF=(8, 5))
        badge = pop(t, t0 + 0.2, 0.35)
        with xform(c, x, 940, max(badge, 0.01)):
            circ(c, 0, 0, 40, "#2B2118"); circ(c, 0, 0, 33, "#F4B942")
            draw_text(c, "০১২৩৪৫৬৭৮৯"[i + 1], 0, 18, 50, "#2B2118")
        if look_up:
            q = prog(t, C[2] + 0.2 + 0.1 * i, 0.4)
            for k in range(8):
                f = (k / 8 + t * 0.6) % 1.0
                circ(c, lerp(x, 540, f * q), lerp(840, 520, f * q), 5, "#2B2118", int(200 * q * (1 - f * 0.4)))
    # price question
    if C[1] - 0.1 < t < C[2] + 0.2:
        a = prog(t, C[1], 0.3) * (1 - prog(t, C[2] - 0.2, 0.3))
        with alpha_layer(c, a):
            with xform(c, 540, 760, 1.1 * back_out(prog(t, C[1], 0.45)), math.sin(t * 20) * 3 * (1 - prog(t, C[1], 1.2))):
                price_tag(c, 0, 0, "৳ দাম?", 1.9, 0)
                cross(c, 0, 0, 150, "#D1452F", 28, prog(t, C[1] + 0.6, 0.3))

def cam_six(t, d, C):
    return kf(t, [(0, 1.05, 540, 950), (1.8, 1.25, 300, 1100), (C[1] + 0.3, 1.1, 540, 800), (C[2] + 0.2, 1.0, 540, 700), (d, 1.22, 540, 560)])

# ---------------------------------------------------------------- 14. third week, rare model, 70 minutes
def rare_phone(c, x, y, s=1.0, rot=0.0, t=0.0):
    with xform(c, x, y, s, rot):
        for sx_ in (-1, 1):
            rect(c, sx_ * 66 - 62 + 5, -140 + 10, 124, 280, "#000000", r=22, a=60, blur=8)
        for sx_ in (-1, 1):
            rect(c, sx_ * 66 - 62, -140, 124, 280, "#2B2118", r=22)
            grad(c, sx_ * 66 - 54, -132, 108, 264, "#FFE08A", "#E4572E")
        rect(c, -6, -150, 12, 300, "#C9A227", r=5)
        sparkle(c, 0, 0, 56 + 8 * math.sin(t * 6), "#FFFFFF", 240)
        for k in range(4):
            sparkle(c, math.cos(k * 1.6 + t * 2) * 130, math.sin(k * 1.6 + t * 2) * 150, 16, "#FFF3B0", 230)

def s_rare(c, t, d, C, m):
    bg(c, "#B7503A", "#7A281C"); dots(c, -100, -100, 1200, 2000, 100, 6, "#FFFFFF", 30, ox=t * 6)
    rays(c, 540, 700, t, "#FFB89A", 28, speed=4)
    # calendar
    def cal(lt):
        out = ease_in(prog(t, C[1] - 0.1, 0.5))
        with xform(c, 540, 700 - out * 1500, max(pop(lt, 0.0, 0.5), 0.01)):
            rect(c, -300 + 10, -330 + 16, 600, 700, "#000000", r=30, a=70, blur=12)
            rect(c, -300, -330, 600, 700, "#FFFFFF", r=30); rect(c, -300, -330, 600, 110, "#D1452F", r=30)
            rect(c, -300, -270, 600, 50, "#D1452F")
            draw_text(c, "সপ্তাহ", 0, -240, 70, "#FFFFFF")
            for r, lab in enumerate(["১ম", "২য়", "৩য়", "৪র্থ"]):
                y = -130 + r * 125
                hi = prog(lt, 1.3, 0.4) if r == 2 else 0
                if hi > 0: rect(c, -285, y - 52, 570, 104, "#FFD36B", r=24, a=int(255 * hi))
                draw_text(c, lab, -215, y + 16, 46, "#2B2118")
                for k in range(7):
                    circ(c, -105 + k * 60, y, 20, "#D1452F" if (r == 2 and k == 3 and hi > 0.5) else "#E5DCC0")
            draw_text(c, "৩য় সপ্তাহ", 0, 335, 78 * (0.3 + 0.7 * pop(lt, 1.3, 0.5)), "#D1452F")
    if t < C[1] + 0.6: cal(t)
    # scene with characters
    floor(c, 1300, "#5E2218") if t > C[1] else None
    p1 = ease_out(prog(t, C[1] + 0.2, 1.4))
    if t > C[1] + 0.1:
        with alpha_layer(c, prog(t, C[1] + 0.1, 0.4)):
            zahid(c, 830, 1290, 1.12, facing=-1, mood="neutral", t=t, talk=0)
            counter_front(c, 560, 1180, 1070, 1400)
            cx_ = lerp(-200, 320, p1)
            hx, hy = customer(c, cx_, 1290, 1.12, 1, shirt="#E9C7A0", mood="happy", t=t, walk=(t * 11 if p1 < 0.97 else None), armF=(70, 20))
            rare_phone(c, hx + 40, hy - 70, 0.55, 8, t)
    if C[1] + 1.1 < t < C[2] - 0.05:
        q = pop(t, C[1] + 1.1, 0.6)
        with xform(c, 540, 430, max(q, 0.01) * (1 + 0.04 * math.sin(t * 4))):
            radial(c, 0, 0, 330, "#FFE9A8", "#FFE9A8", 120, 0)
            rare_phone(c, 0, 0, 1.15, -6, t)
        tag(c, 540, 700, "বিরল মডেল", 56, "#2B2118", "#F4B942", pop(t, C[1] + 1.5, 0.4))
    if t > C[2] - 0.05:
        q = pop(t, C[2] - 0.05, 0.4)
        with alpha_layer(c, min(1, q)):
            rect(c, -2600, -2600, 6400, 6400, "#000000", a=int(70 * q))
        mn = 420 * ease_io(prog(t, C[2], 0.9))
        with xform(c, 540, 480, max(q, 0.01)):
            wall_clock(c, 0, 0, 230, minute=mn % 360, hour=mn / 12, wedge_to=min(mn, 359), wedge_col="#E4572E")
        tag(c, 540, 820, "৭০ মিনিট", 84, "#D1452F", "#FFFFFF", pop(t, C[2] + 0.2, 0.35), rot=-3)

def cam_rare(t, d, C):
    return kf(t, [(0, 1.0, 540, 800), (C[1] - 0.2, 1.15, 540, 760), (C[1] + 0.6, 1.0, 540, 760), (C[2], 1.12, 540, 740), (d, 1.3, 540, 700)])

SCENES_B = {"night": (s_night, cam_night), "sign": (s_sign, cam_sign), "six": (s_six, cam_six), "rare": (s_rare, cam_rare)}
