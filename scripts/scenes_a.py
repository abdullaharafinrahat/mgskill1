"""Script 4b: scenes 1-12 (audio 0s - 51s)."""
from sets import *

# 1 HOOK ------------------------------------------------------------
@scene(0.0)
def hook(c, k):
    t, g = k.t, k.g
    world(c, vgrad(hexc("#5A1F1A"), hexc("#2A100E"), -200, 1900)); rays(c, 540, 700, 18, (1, .55, .25, .10), g * .08)
    glow(c, 540, 700, 700, hexc("#FF8A3D"), .35)
    sh = 2.5 + 38 * math.exp(-max(0, t - .35) * 7) * (1 if t > .35 else 0)
    c.save(); cam(c, t, [(0, 540, 880, 1.28, 0), (3.5, 540, 820, 1.02, 0)], g, sh)
    wall_clock(c, 150, 600, 100, 600 + t * 4, g, hand_speed=90)
    rect(c, 700, 130, 330, 400, None, 0)
    c.save(); c.translate(870, 480); c.rotate(math.sin(g * 2.2) * .06 + .08)
    rect(c, -140, -20, 280, 300, hexc("#FFF7E8"), 8, hexc("#2b2118"), 4); rect(c, -140, -20, 280, 70, hexc("#C2432F"), 8)
    text(c, "ভাড়া বাকি!", 0, 15, 46, (1, 1, 1), "bold"); text(c, "শেষ নোটিশ", 0, 130, 52, hexc("#2b2118"), "bold"); c.restore()
    person(c, 540, 1500, 2.35, **Z, mouth="frown", brow="worry", sweat=(g * .7) % 1, hl=(-84, -318), hr=(84, -318), look=.9, blink=blinkamt(g, .5), lean=math.sin(g * 1.3) * .015, bob=math.sin(g * 2) * 3)
    c.restore()
    p = e_back(prog(t, .25, .7)) if t > .25 else 0
    if p > 0:
        c.save(); c.translate(540, 250 + (1 - e_out(prog(t, .25, .55))) * -60); c.scale(p * (1 + .04 * math.sin(g * 8)), p * (1 + .04 * math.sin(g * 8)))
        text(c, "৫০ মিনিট", 0, 0, 170, hexc("#FFE9B8"), "bold", stroke=hexc("#7a1f12"), sw=14, rot=-.05); c.restore()
    vignette(c, .55)

# 2 luck turns ------------------------------------------------------
@scene(3.5, "iris", ix=540, iy=800)
def luck(c, k):
    t, g = k.t, k.g
    world(c, vgrad(hexc("#F4C95D"), hexc("#E58A3A"), -200, 1900)); rays(c, 540, 760, 20, (1, .95, .7, .22), g * .15)
    c.save(); cam(c, t, [(0, 540, 900, 1.35, 3), (3.8, 540, 960, 1.0, 0)], g, 2)
    stopwatch(c, 540, 600, 260, 50 * e_io(prog(t, .2, 3.2)))
    p = e_back(prog(t, .5, 1.1)); c.save(); c.translate(540, 965); c.scale(p, p); text(c, "৫০ মিনিট", 0, 0, 120, hexc("#FFF8E6"), "bold", stroke=hexc("#8a3d12"), sw=12); c.restore()
    for i in range(16):
        tt = t - 1.4 - i * .12
        if tt > 0:
            ang = -math.pi / 2 + (rnd(i) - .5) * 2.2; v = 700 + rnd(i, 4) * 300; xx = 540 + math.cos(ang) * v * tt * .7; yy = 600 + math.sin(ang) * v * tt + 900 * tt * tt
            coin(c, xx, yy, 34, g * 8 + i)
    person(c, 540, 1560, 1.15, **Z, mouth="big", brow="up", hl=(-120, -330), hr=(120, -330), blink=blinkamt(g), bob=abs(math.sin(g * 5)) * 6)
    c.restore(); vignette(c, .25)

# 3 rent / shutter --------------------------------------------------
@scene(7.5, "push_l")
def rent(c, k):
    t, g = k.t, k.g
    world(c, hexc("#8C7B5E")); pattern(c, "tiles", "#5a4a32", y0=-200, y1=1330, a=.13); rect(c, -800, 1330, 3400, 900, hexc("#5A4A38"))
    c.save(); cam(c, t, [(0, 540, 520, 1.25, 0), (1.6, 540, 520, 1.25, 0), (3.1, 540, 900, 1.05, 0), (5.2, 540, 940, 1.35, 0)], g, 2)
    n = prog(t, .0, 1.5); pg = int(n * 11)
    for i in range(6):
        pp = (n * 11 - i * 1.0) if True else 0
        if 0 < pp < 1.0: calendar(c, 540 - e_in(pp) * 900, 330 - pp * 120, 440, 470, "জানুয়ারি", bn(12 - i), "", -pp * .8)
    calendar(c, 540, 330, 440, 470, "এক বছর", "আগে" if False else bn(1), "বছর আগে" if n >= 1 else "")
    rect(c, -300, 1150, 1700, 400, hexc("#6B4226")); rect(c, -300, 1150, 1700, 24, hexc("#8A5A36"))
    if t > 1.75:  # rent notice slam
        pp = e_back(prog(t, 1.75, 2.1)); c.save(); c.translate(780, 640); c.rotate(.12); c.scale(pp, pp)
        rect(c, -150, -130, 300, 260, hexc("#FFF7E8"), 8, hexc("#2b2118"), 4); rect(c, -150, -130, 300, 62, hexc("#C2432F"), 8); text(c, "ভাড়া বাকি", 0, -98, 42, (1, 1, 1), "bold")
        for i in range(3): rect(c, -110, -30 + i * 38, 220, 12, hexc("#bdb298"), 6)
        c.restore()
    person(c, 400, 1260, 1.5, **Z, mouth="frown", brow="worry", sweat=(g * .6) % 1 if t > 2 else 0, look=.5, hl=(-80, -250), hr=(100, -240), lean=.02 * math.sin(g * 2))
    if t > 3.6:  # thought cloud with shutter
        p = e_back(prog(t, 3.6, 4.1)); c.save(); c.translate(560, 1010); c.scale(p, p)
        for (cx_, cy_, r_) in ((-110, 0, 100), (0, -40, 120), (110, 0, 100), (-40, 40, 100), (60, 40, 100)): circ(c, cx_, cy_, r_, hexc("#FFF9EC"), hexc("#2b2118"), 0)
        c.save(); c.new_path(); c.rectangle(-150, -100, 300, 160); c.clip(); rect(c, -150, -100, 300, 160, hexc("#d9cdb0")); 
        for yy in range(-100, int(-100 + 160 * e_io(prog(t, 4.2, 5.3))), 22): rect(c, -150, yy, 300, 20, hexc("#7E7B72")); 
        c.restore(); c.restore()
    c.restore()
    shutter(c, e_in(prog(t, 5.25, 6.05)) if t > 5.25 else 0)
    if t > 5.7: 
        p = e_back(prog(t, 5.7, 6.05)); c.save(); c.translate(540, 900); c.scale(p, p); rect(c, -70, -10, 140, 110, hexc("#E0A526"), 14, hexc("#7a5a10"), 6); c.new_path(); c.arc(0, -10, 44, math.pi, 2 * math.pi); setc(c, hexc("#7a7a74")); c.set_line_width(16); c.stroke(); circ(c, 0, 45, 12, hexc("#4a3a10")); c.restore()
    vignette(c, .4)

# 4 street ----------------------------------------------------------
@scene(13.55, "cut")
def street_s(c, k):
    t, g = k.t, k.g
    c.save(); cam(c, t, [(0, 300, 960, 1.0, 0), (2.9, 700, 1000, 1.5, 0)], g, 2.5)
    street(c, g, seed=3)
    for i, (sp, col) in enumerate(((120, "#C2432F"), (-90, "#E6B13A"))): rickshaw(c, ((g * sp + i * 900) % 3200) - 500, 1620 - i * 40, 1.0, col, g)
    # tiny shop between tall buildings
    rect(c, 480, 820, 560, 560, hexc("#A9835A")); rect(c, 520, 1040, 480, 290, hexc("#3a2e24")); rect(c, 540, 1060, 440, 240, hexc("#F1CE8A"), 6)
    phone(c, 640, 1170, 70, 130, state="on"); phone(c, 760, 1170, 70, 130, state="cracked"); phone(c, 880, 1170, 70, 130, state="on")
    rect(c, 470, 880, 580, 130, hexc("#2F5D3A"), 12, hexc("#F4E7C5"), 6); text(c, "জাহিদ মোবাইল সার্ভিসিং", 760, 945, 46, hexc("#FFF4DC"), "bold")
    poly(c, [(470, 1040), (1050, 1040), (1010, 1000), (510, 1000)], hexc("#C2432F"))
    c.restore()
    if t > .3:
        p = e_back(prog(t, .3, .8)); c.save(); c.translate(260, 250); c.scale(p, p); rect(c, -230, -48, 460, 96, hexc("#FFF7E8"), 48, hexc("#2b2118"), 5); circ(c, -170, 0, 22, hexc("#C2432F")); text(c, "মিরপুর, ঢাকা", 30, 0, 50, hexc("#2b2118"), "bold"); c.restore()
    shutter(c, 1 - e_out(prog(t, .0, .75)))
    vignette(c, .25)

# 5 father ----------------------------------------------------------
@scene(16.4, "wipe")
def father(c, k):
    t, g = k.t, k.g
    world(c, hexc("#7A4B2C")); pattern(c, "stripes", "#4b2a16", y0=-300, y1=1900, a=.25)
    c.save(); cam(c, t, [(0, 540, 820, 1.0, -1.5), (2.3, 540, 760, 1.3, 1)], g, 2)
    glow(c, 540, 740, 650, hexc("#FFD58A"), .55)
    rect(c, 255, 380, 570, 700, hexc("#4A2B14"), 18); rect(c, 285, 410, 510, 640, hexc("#E8D3A6"), 8); rect(c, 285, 410, 510, 640, vgrad(hexc("#E6C98A"), hexc("#C9A66B"), 410, 1050), 8)
    c.save(); c.new_path(); c.rectangle(285, 410, 510, 640); c.clip(); person(c, 540, 1180, 1.6, **FATHER, mouth="smile", brow="flat", blink=blinkamt(g)); c.restore()
    rect(c, 285, 410, 510, 640, None, 8, hexc("#2b1a0e"), 10)
    for i in range(14):  # fairy lights
        a = i / 13; xx = 160 + a * 760; yy = 300 + math.sin(a * math.pi) * 70; circ(c, xx, yy, 9, hexc("#FFD36A")); glow(c, xx, yy, 40, hexc("#FFD36A"), .5 + .3 * math.sin(g * 4 + i))
    line(c, 160, 300, 920, 300, 3, hexc("#2a1a0e")) if False else None
    c.save(); c.translate(540, 1210 + math.sin(g * 2) * 6); c.rotate(math.sin(g * 1.8) * .05)  # key
    glow(c, 0, 20, 200, hexc("#FFE08A"), .5); line(c, 0, -90, 0, 40, 8, hexc("#E0A526")); circ(c, 0, -110, 42, None, hexc("#E0A526"), 14); rect(c, 0, 10, 40, 12, hexc("#E0A526"), 4); rect(c, 0, 34, 28, 12, hexc("#E0A526"), 4); c.restore()
    for i in range(7): star(c, 540 + (rnd(i) - .5) * 700, 700 + (rnd(i, 2) - .5) * 700, 10 + 10 * rnd(i, 3) * (.5 + .5 * math.sin(g * 3 + i)), hexc("#FFF1C2"), g)
    c.restore(); vignette(c, .55)

# 6 old clock -------------------------------------------------------
@scene(18.7, "zoom")
def oldclock(c, k):
    t, g = k.t, k.g
    world(c, hexc("#3B4630")); pattern(c, "bricks", "#1f281a", y0=-300, y1=1900, a=.5)
    glow(c, 540, 800, 800, hexc("#E8D49A"), .45)
    c.save(); cam(c, t, [(0, 540, 800, 1.0, 0), (2.0, 540, 790, 1.55, 0)], g, 3)
    wall_clock(c, 540, 800, 330, 590 + t * 2, g, old=True)
    for i in range(6): line(c, 330 + 0, 470 + i * 0, 330 + i * 28, 470 + i * 24, 2, (1, 1, 1, .5)) if False else None
    for i in range(7): line(c, 320 + 12 * i, 470, 540 + (i - 3) * 20, 560 + i * 8 - abs(i - 3) * 8, 1.6, (1, 1, 1, .45))
    c.restore(); dust(c, g, 36, (1, .95, .8, .5), 10, 6); vignette(c, .6)

# 7 he tried so many things ------------------------------------------
@scene(20.7, "push_u")
def tried(c, k):
    t, g = k.t, k.g
    world(c, hexc("#D88B3A")); pattern(c, "dots", "#8a4a12", y0=-300, y1=2000, a=.22, step=100)
    c.save(); cam(c, t, [(0, 540, 800, 1.0, 0), (4.8, 540, 780, 1.07, 0)], g, 2)
    cards = [(120, "#D9683A"), (560, "#7C9A5B"), (1000, "#3B2F2A")]
    for i, (yy, col) in enumerate(cards):
        t0 = i * 1.2; e = e_back(prog(t, t0, t0 + .5))
        if e <= 0: continue
        c.save(); c.translate((1 - e) * (1400 if i % 2 == 0 else -1400), 0)
        rect(c, 50, yy, 980, 400, hexc(col), 36, hexc("#2b2118"), 6); c.save(); c.new_path(); rrect_path(c, 50, yy, 980, 400, 36); c.clip()
        if i == 0:
            rect(c, 50, yy, 980, 400, hexc("#E8925A")); rays(c, 780, yy + 200, 14, (1, 1, 1, .1), g * .3, 0, 900)
            person(c, 330, yy + 470, .95, **Z, mouth="big", brow="up", hl=(-90, -300), hr=(70, -420), talk=talkamt(g, 0, 99) * .5)
            c.save(); c.translate(760, yy + 200 + math.sin(g * 4) * 8); c.rotate(math.sin(g * 4) * .08); rect(c, -190, -110, 380, 220, hexc("#FFF4DC"), 16, hexc("#C2432F"), 8); text(c, "সেল!", 0, -40, 80, hexc("#C2432F"), "bold"); text(c, "৩০% ছাড়", 0, 45, 70, hexc("#2b2118"), "bold"); c.restore()
        elif i == 1:
            rect(c, 50, yy, 980, 400, hexc("#9DB37C")); rect(c, 50, yy + 330, 980, 70, hexc("#6B7A55"))
            person(c, 300, yy + 470, .95, **Z, mouth="smile", brow="flat", hr=(150, -260), look=.8)
            for j in range(6):
                pp = ((g * .9 + j / 6) % 1); fx = 420 + pp * 520; fy = yy + 180 - math.sin(pp * math.pi) * 90 + pp * 80
                c.save(); c.translate(fx, fy); c.rotate(pp * 6 + j); rect(c, -34, -44, 68, 88, hexc("#FFF9EC"), 6, hexc("#7a6a52"), 3); rect(c, -22, -26, 44, 8, hexc("#C2432F"), 3); rect(c, -22, -8, 44, 6, hexc("#9a8a6a"), 3); c.restore()
            for j in range(3): person(c, 800 + j * 90, yy + 520, .5, **CROWD[j + 1], mouth="smile")
        else:
            rect(c, 50, yy, 980, 400, hexc("#3B2F2A")); glow(c, 560, yy + 40, 420, hexc("#FFC76B"), .55)
            c.new_path(); c.arc(880, yy + 110, 50, 0, 2 * math.pi); setc(c, hexc("#F3E3BF")); c.fill(); circ(c, 902, yy + 98, 44, hexc("#3B2F2A"))
            rect(c, 120, yy + 20, 12, 120, hexc("#8a8a84")); poly(c, [(80, yy + 60), (180, yy + 60), (150, yy + 20), (110, yy + 20)], hexc("#E0A526"))
            person(c, 500, yy + 470, .95, **Z, mouth="flat", brow="worry", blink=.5 + .5 * math.sin(g * 1.5) * .5, tilt=.12 + .03 * math.sin(g * 2), hl=(-60, -90), hr=(70, -80))
            rect(c, 380, yy + 330, 330, 60, hexc("#6B4226"), 8); phone(c, 540, yy + 300, 110, 70, rot=1.57, state="open")
            text(c, "রাত ২টা", 830, yy + 260, 54, hexc("#F3E3BF"), "bold"); text(c, "z z z", 700, yy + 70 - (g % 2) * 20, 40, (1, 1, 1, .6), "bold")
        c.restore(); c.restore()
    c.restore(); vignette(c, .3)

# 8 never timed his work --------------------------------------------
@scene(25.5, "iris", ix=380, iy=900)
def nevertimed(c, k):
    t, g = k.t, k.g
    world(c, hexc("#BFA77E")); pattern(c, "tiles", "#7a6440", y0=-300, y1=1330, a=.16); rect(c, -800, 1330, 3400, 700, hexc("#6E5539"))
    c.save(); cam(c, t, [(0, 380, 900, 1.0, 0), (1.2, 380, 900, 1.1, 0), (2.3, 700, 720, 1.5, 0)], g, 2)
    wall_clock(c, 780, 600, 190, 600 + t, g)
    rect(c, -300, 1060, 1100, 300, hexc("#6B4226")); rect(c, -300, 1060, 1100, 30, hexc("#8A5A36"))
    person(c, 380, 1170, 1.4, **Z, mouth="flat", brow="angry", look=-.3, tilt=.14, hl=(-40, -80), hr=(110, -90), blink=blinkamt(g, 1), lean=.02)
    phone(c, 520, 1010, 240, 120, rot=0, state="open", g=g); 
    if t > .9:
        p = e_back(prog(t, .9, 1.3)); c.save(); c.translate(540, 330); c.scale(p, p)
        stopwatch(c, 0, 0, 110, 20, g); line(c, -150, -150, 150, 150, 26, hexc("#C2432F")); line(c, 150, -150, -150, 150, 26, hexc("#C2432F")); c.restore()
    c.restore(); vignette(c, .35)

# 9 ad claim banner -------------------------------------------------
@scene(27.9, "wipe")
def adclaim(c, k):
    t, g = k.t, k.g
    world(c, hexc("#B5654A")); pattern(c, "bricks", "#6b2f1e", y0=-300, y1=1330, a=.28); rect(c, -800, 1330, 3400, 700, hexc("#7C7566"))
    c.save(); cam(c, t, [(0, 540, 800, 1.0, 1), (4.1, 560, 700, 1.3, 0)], g, 2)
    rect(c, -200, 160, 1500, 90, hexc("#4A3A28")); rect(c, 80, 1000, 920, 330, hexc("#3a2e24")); rect(c, 100, 1020, 880, 290, hexc("#F1CE8A"), 6)
    drop = e_out(prog(t, 1.45, 2.0)) if t > 1.4 else 0; yb = -300 + drop * 880 + (math.sin((t - 1.9) * 14) * 12 * math.exp(-(t - 1.9) * 4) if t > 1.9 else 0)
    line(c, 150, 250, 190, yb - 130, 5, hexc("#4A3A28")); line(c, 930, 250, 890, yb - 130, 5, hexc("#4A3A28"))
    banner(c, 540, yb, 840, 330, "দ্রুত ও নির্ভরযোগ্য", "মোবাইল সার্ভিস", g, sz=68)
    if t > 2.0:
        for i in range(5): star(c, 330 + rnd(i) * 200, yb - 70 + (rnd(i, 1) - .5) * 80, 14 * (.5 + .5 * math.sin(g * 6 + i)), hexc("#E0A526"), g)
    person(c, 175, 1330, 1.15, **Z, mouth="smile", brow="up", hl=(-30, -420), hr=(100, -20), look=.8, talk=talkamt(g, 28.1, 29.3) * 0.0)
    c.restore(); vignette(c, .35)

# 10 how fast is fast? ---------------------------------------------
@scene(32.1, "flash")
def howfast(c, k):
    t, g = k.t, k.g
    world(c, vgrad(hexc("#2F2A24"), hexc("#1C1814"), -200, 1900)); rays(c, 540, 760, 16, (.95, .45, .2, .12), g * .12)
    c.save(); cam(c, t, [(0, 540, 960, 1.0, -3), (2.5, 540, 860, 1.25, 3)], g, 3)
    c.save(); c.translate(540, 760); 
    circ(c, 0, 0, 470, None, (1, 1, 1, .12), 10)
    for i in range(12): a = i * math.pi / 6; line(c, 400 * math.cos(a), 400 * math.sin(a), 450 * math.cos(a), 450 * math.sin(a), 8, (1, 1, 1, .2))
    line(c, 0, 0, 380 * math.cos(g * 7), 380 * math.sin(g * 7), 10, (1, .6, .3, .45)); line(c, 0, 0, 260 * math.cos(g * -3), 260 * math.sin(g * -3), 14, (1, 1, 1, .3)); c.restore()
    p = e_back(prog(t, 0, .4)); c.save(); c.translate(540, 700); c.scale(p, p); text(c, "দ্রুত", 0, 0, 300, hexc("#FFE9B8"), "bold", stroke=hexc("#7a1f12"), sw=14); c.restore()
    if t > .8:
        p = e_back(prog(t, .8, 1.2)); c.save(); c.translate(540, 1000); c.scale(p, p); text(c, "কত দ্রুত?", 0, 0, 130, hexc("#FF9F4A"), "bold", stroke=hexc("#2a1008"), sw=10); c.restore()
    for i, (qx, qy) in enumerate(((150, 400), (930, 1050), (900, 380), (170, 1100))):
        if t > .5 + i * .25: text(c, "?", qx, qy + math.sin(g * 3 + i) * 15, 190, (1, .85, .6, .55), "bold", rot=(i - 1.5) * .3, sx=1 + .1 * math.sin(g * 5 + i))
    c.restore(); vignette(c, .5)

# 11 customer dialogue ----------------------------------------------
@scene(34.6, "iris", ix=700, iy=900)
def customers(c, k):
    t, g = k.t, k.g
    c.save(); cam(c, t, [(0, 540, 960, 1.0, 0), (2.4, 640, 960, 1.05, 0), (3.2, 760, 860, 1.5, 0), (5.7, 360, 780, 1.55, 0), (8.5, 360, 780, 1.65, 0), (8.9, 760, 840, 1.7, 2), (10, 700, 860, 1.45, 0)], g, 2.5)
    interior(c, g, tmin=605 + t * .1)
    ztalk = talkamt(g, 40.73, 41.25)
    person(c, 340, 1090, 1.15, **Z, mouth="smile" if g < 43.4 else "worry", talk=ztalk, brow="flat" if g < 42.5 else "worry", look=.5, sweat=((g - 43.5) * .6 % 1) if g > 43.5 else 0, blink=blinkamt(g), hr=(100, -150) if g < 39 else (160, -280 if 40.7 < g < 41.3 else -120))
    counter(c, g)
    cx = clamp(-250 + (t / 1.9) * 1010, -250, 760) if True else 760; walking = t < 1.9 + .2; wk = g * 9
    ctalk = max(talkamt(g, 37.9, 39.1), talkamt(g, 43.48, 43.95))
    person(c, cx, 1060, 1.12, **CUST1, legs=True, walk=wk if walking else 0, bob=abs(math.sin(wk)) * 7 if walking else 0, flip=True, look=-.5, talk=ctalk,
           mouth="flat", brow="up" if g > 43.4 else "flat", hl=(-100, -20) if g < 36.6 else (-170, -250), hr=(120, -10), blink=blinkamt(g, 1.2),
           hold_l=(lambda cc: phone(cc, -10, -60, 80, 150, rot=.1, state="cracked")) if g > 36.6 else None)
    bubble(c, g, 37.9, 700, 560, "ভাই, কতক্ষণ লাগবে?", tail=(760, 700), t1=40.0)
    bubble(c, g, 40.73, 330, 560, "হয়ে যাবে।", tail=(340, 700), t1=42.6)
    bubble(c, g, 43.48, 760, 560, "কখন?", tail=(780, 700), size=70)
    c.restore(); vignette(c, .3)

# 12 no answer, customer leaves to the big shop ----------------------
@scene(44.3, "cut")
def leaves(c, k):
    t, g = k.t, k.g
    c.save(); cam(c, t, [(0, 560, 900, 1.35, 0), (2.4, 540, 960, 1.0, 0), (3.2, 700, 960, 1.0, 0), (5.3, 1500, 960, 1.05, 0), (6.9, 1680, 900, 1.25, 0)], g, 2.5)
    interior(c, g, tmin=608 + t * .1)
    c.save(); c.new_path(); c.rectangle(-900, -400, 1980, 2400); c.clip(); c.restore()
    # street to the right of the door
    c.save(); c.translate(1080, 0); c.new_path(); c.rectangle(0, -400, 2200, 2400); c.clip(); c.translate(-1080, 0)
    c.save(); c.translate(1080, 0); street(c, g, seed=7); c.restore()
    # big shop
    rect(c, 1500, 560, 1100, 800, hexc("#F2E6CF")); rect(c, 1500, 560, 1100, 130, hexc("#C2432F")); text(c, "স্মার্ট মোবাইল সেন্টার", 2050, 625, 66, (1, 1, 1), "bold")
    rect(c, 1560, 760, 420, 470, hexc("#FFF2C9"), 10, hexc("#5a4a32"), 8); rect(c, 2060, 760, 480, 570, hexc("#FFF2C9"), 10, hexc("#5a4a32"), 8)
    for i in range(3): phone(c, 1640 + i * 130, 1000, 70, 140, state="on")
    for i in range(3): person(c, 2150 + i * 130, 1250, .5, **CROWD[i], mouth="smile")
    glow(c, 2050, 700, 600, hexc("#FFE9A8"), .3)
    c.restore()
    rect(c, 1040, -400, 80, 2400, hexc("#4a2f1b"))
    # Zahid left, shrugging
    zs = prog(t, 0, 1.0)
    person(c, 340, 1090, 1.15, **Z, mouth="o" if g < 47 else "frown", brow="worry", hl=(-200, -190), hr=(200, -190), sweat=(g * .5) % 1, look=.6, blink=blinkamt(g, .4), lean=.03 * math.sin(g * 3))
    counter(c, g, x1=1060)
    qmarks(c, g, 340, 560, 3, 100)
    cx = 760 + e_io(prog(t, 2.6, 6.6)) * 1190; back = t > 3.3
    wk = g * 9; moving = 2.6 < t < 6.6
    person(c, cx, 1060, 1.12, **CUST1, legs=True, walk=wk if moving else 0, bob=abs(math.sin(wk)) * 7 if moving else 0, back=back, flip=True, mouth="flat",
           hl=(-120, -20), hr=(120, -10), hold_l=(lambda cc: phone(cc, -10, -60, 80, 150, rot=.1, state="cracked")) if True else None)
    c.restore(); vignette(c, .28)
