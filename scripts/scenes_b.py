"""Script 5: scenes 13-25 (audio 51s - 125s)."""
from sets import *

def rare_phone(c, x, y, s=1.0, rot=0):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    rect(c, -150, -120, 300, 240, hexc("#2b2622"), 26); rect(c, -140, -110, 135, 220, hexc("#F3D58B"), 18); rect(c, 5, -110, 135, 220, hexc("#E7A94E"), 18)
    line(c, 0, -120, 0, 120, 8, hexc("#1a1612")); circ(c, 100, -75, 26, hexc("#1a1612")); circ(c, 100, -75, 12, hexc("#6a5a4a")); circ(c, 100, -20, 14, hexc("#1a1612"))
    text(c, "?", -70, 0, 110, hexc("#8a5a1c"), "bold"); c.restore()

# 13 schoolgirl arrives ------------------------------------------------
@scene(51.2, "wipe")
def girl_in(c, k):
    t, g = k.t, k.g
    c.save(); cam(c, t, [(0, 540, 960, 1.0, 0), (1.8, 700, 960, 1.08, 0), (2.4, 330, 700, 1.5, 0), (3.5, 650, 900, 1.3, 0)], g, 2.5)
    interior(c, g, wall="#E0894A", pat="diag", pcol="#B8622A", floor="#6B3F25", poster=False, clock_at=(840, 330), tmin=17 * 60 + 20 + t * .2, pa=.2)
    rect(c, 60, 140, 300, 130, hexc("#E7B04E"), 12, hexc("#4a2f1b"), 6) if False else None
    if g > 53.2:
        p = e_back(prog(g, 53.2, 53.6)); c.save(); c.translate(260, 360); c.rotate(-.04); c.scale(p, p)
        rect(c, -190, -140, 380, 280, hexc("#2F3A2C"), 12, hexc("#8A5A36"), 14); text(c, "কাল\nপরীক্ষা!", 0, 0, 78, hexc("#F5F1E6"), "bold"); line(c, -140, 100, 140, 100, 6, hexc("#E0A526")); c.restore()
    person(c, 340, 1090, 1.15, **Z, mouth="flat", brow="flat", look=.6, blink=blinkamt(g, .3), hr=(110, -150))
    counter(c, g)
    cx = clamp(-260 + t / 1.7 * 1020, -260, 760); mv = t < 1.75; wk = g * 9
    c.save(); rect(c, cx - 112, 1060 - 245 * 1.1, 224, 270, hexc("#B6452E"), 36); c.restore() if False else None
    c.save(); c.translate(cx, 1060); rect(c, -118, -265, 236, 260, hexc("#9C3B26"), 40); c.restore()
    person(c, cx, 1060, 1.1, **GIRL, legs=True, walk=wk if mv else 0, bob=abs(math.sin(wk)) * 7 if mv else 0, flip=True, mouth="flat", brow="worry", look=-.6, blink=blinkamt(g, .9), hl=(-100, -40), hr=(100, -40))
    c.restore(); vignette(c, .3)

# 14 phone with all lessons, crack ---------------------------------------
@scene(54.6, "zoom")
def crack(c, k):
    t, g = k.t, k.g
    world(c, vgrad(hexc("#2E3A26"), hexc("#171D12"), -200, 1900)); glow(c, 540, 760, 700, hexc("#FFE9B8"), .25)
    sh = 2.5 + (45 * math.exp(-(t - 1.5) * 6) if t > 1.5 else 0)
    c.save(); cam(c, t, [(0, 540, 800, 1.0, 0), (2.7, 540, 760, 1.18, 0)], g, sh)
    cr = t > 1.5
    phone(c, 540, 760, 500, 960, rot=math.sin(g * 1.5) * .02, state="cracked" if cr else "notes", glowing=True)
    for i, (lab, col) in enumerate((("গণিত", "#C2432F"), ("বিজ্ঞান", "#5E7F4A"), ("ইংরেজি", "#C8892B"), ("ইতিহাস", "#8E3B33"))):
        a = g * .9 + i * 1.57; fall = prog(t, 1.5, 2.6) ** 2 * 900 if cr else 0
        px = 540 + 420 * math.cos(a); py = 500 + 120 * math.sin(a) * .8 + i * 120 + fall
        if t > .15 * (i + 1): rect(c, px - 100, py - 34, 200, 68, hexc(col), 34, hexc("#FFF4DC"), 4); text(c, lab, px, py, 40, (1, 1, 1), "bold")
    c.restore()
    caption_flash(c, .7 * math.exp(-(t - 1.5) * 12) if t > 1.5 else 0); vignette(c, .45)

# 15 "will I get it tonight?" ----------------------------------------------
@scene(57.3, "iris", ix=760, iy=900)
def girl_asks(c, k):
    t, g = k.t, k.g
    c.save(); cam(c, t, [(0, 540, 960, 1.0, 0), (.9, 760, 860, 1.6, 0), (3.6, 760, 860, 1.7, 0), (4.0, 360, 800, 1.6, 0), (6.5, 360, 800, 1.75, 0)], g, 2.5)
    interior(c, g, wall="#4B3626", pat="stripes", pcol="#2c1e14", floor="#2b1d14", poster=False, tmin=21 * 60 + 10 + t * .3, pa=.35, phones_on=False)
    glow(c, 540, 300, 900, hexc("#FFC76B"), .38)
    zt = talkamt(g, 62.52, 62.98)
    person(c, 340, 1090, 1.15, **Z, mouth="flat" if g < 62.5 else "smile", talk=zt, brow="worry", look=.6, sweat=(g * .5) % 1 if g > 61.3 else 0, blink=blinkamt(g, 2))
    counter(c, g, ctop="#4a2f1b", cfront="#5F3D26")
    gt = max(talkamt(g, 57.55, 59.3), talkamt(g, 59.52, 60.65))
    person(c, 760, 1060, 1.1, **GIRL, legs=True, flip=True, mouth="flat", talk=gt, brow="worry", look=-.6, hl=(-30, -150), hr=(30, -150), blink=blinkamt(g, .6), bob=math.sin(g * 2) * 2)
    bubble(c, g, 58.0, 700, 540, "ভাইয়া, আজ রাতের মধ্যে\nপাব?", tail=(760, 690), t1=61.2, size=50)
    bubble(c, g, 62.52, 330, 560, "হয়ে যাবে।", tail=(340, 700), size=54)
    c.restore(); vignette(c, .55)

# 16 silence, then "when exactly?" ------------------------------------------
@scene(63.8, "cut")
def silence(c, k):
    t, g = k.t, k.g
    world(c, vgrad(hexc("#3A3326"), hexc("#1E1A12"), -200, 1900)); glow(c, 540, 700, 800, hexc("#E7B96B"), .25)
    c.save(); cam(c, t, [(0, 540, 1000, 1.0, 0), (1.6, 540, 850, 1.35, 0), (4.0, 540, 880, 1.3, 0), (4.7, 540, 760, 1.0, 0)], g, 2.5)
    gt = max(talkamt(g, 66.39, 67.57), talkamt(g, 68.02, 68.96), talkamt(g, 69.25, 70.33))
    person(c, 540, 1480, 2.0, **GIRL, mouth="flat", talk=gt, brow="worry", look=-.6 if g < 66.3 else 0, blink=blinkamt(g, .2) or (.7 if 64.5 < g < 64.7 else 0), hl=(-40, -140), hr=(40, -150), tilt=.04 * math.sin(g))
    if 64.2 < g < 66.35:
        c.save(); c.translate(540, 470); rect(c, -140, -60, 280, 120, hexc("#FFF9EC"), 60, hexc("#2b2118"), 5); poly(c, [(-20, 58), (20, 58), (0, 120)], hexc("#FFF9EC"), hexc("#2b2118"), 5) if False else None
        for i in range(3): circ(c, (i - 1) * 70, math.sin(g * 6 - i) * 12, 18, hexc("#2b2118"))
        c.restore()
    bubble(c, g, 66.39, 540, 400, "হয়ে যাবে মানে কখন?", tail=(540, 620), t1=68.0, size=58)
    for i, (t0, lab, ic, x0) in enumerate(((68.02, "অপেক্ষা করব", "hour", 280), (69.25, "অন্য দোকানে\\nযাব", "shop", 800))):
        p = e_back(prog(g, t0, t0 + .3))
        if p <= 0.02: continue
        c.save(); c.translate(x0, 380); c.scale(p, p); rect(c, -230, -170, 460, 340, hexc("#F3E3BF"), 36, hexc("#2b2118"), 6)
        if ic == "hour":
            poly(c, [(-45, -150 + 10), (45, -150 + 10), (0, -70)], hexc("#C8892B")); poly(c, [(0, -70), (-45, -10), (45, -10)], hexc("#C8892B")); rect(c, -55, -160, 110, 12, hexc("#4a2f1b"), 5); rect(c, -55, -14, 110, 12, hexc("#4a2f1b"), 5)
            for q in range(3): circ(c, 0, -40 + (g * 30 + q * 7) % 20 * .4, 3, hexc("#4a2f1b"))
        else:
            rect(c, -60, -150, 120, 100, hexc("#B5654A"), 6); poly(c, [(-70, -150), (70, -150), (50, -180), (-50, -180)], hexc("#C2432F")); line(c, -100, -100 + math.sin(g * 5) * 4, 100, -100, 0, hexc("#2b2118")) if False else None
            line(c, 70, -100, 150, -100, 12, hexc("#C2432F")); poly(c, [(150, -130), (180, -100), (150, -70)], hexc("#C2432F"))
        text(c, lab.replace("\\n", "\n"), 0, 90, 48, hexc("#2b2118"), "bold"); c.restore()
    c.restore(); vignette(c, .55)

# 17 realization (3 acts) -------------------------------------------------
def _real1(c, k):
    t, g = k.t, k.g
    world(c, hexc("#F3DFA6")); rays(c, 540, 700, 20, (1, .8, .4, .22), g * .1)
    c.save(); cam(c, t, [(0, 540, 960, 1.0, 0), (3.6, 540, 850, 1.22, 0)], g, 2.5)
    pop = e_back(prog(t, 3.8, 4.2)) if t > 3.8 else 0
    person(c, 540, 1300, 1.8, **Z, mouth="o" if pop else "flat", brow="up" if pop else "worry", look=.0 if pop else -.5, hl=(-90, -80), hr=(90, -80), blink=blinkamt(g, .5))
    if pop: c.save(); c.translate(540, 330); c.scale(pop, pop); bulb(c, 0, 0, 70, g); c.restore()
    c.restore(); caption_flash(c, .8 * math.exp(-(t - 3.8) * 9) if t > 3.8 else 0)
def _real2(c, k):
    t, g = k.t, k.g
    world(c, hexc("#C9D3A2")); pattern(c, "dots", "#7A8F55", y0=-300, y1=2000, a=.25, step=110)
    c.save(); cam(c, t, [(0, 540, 960, 1.0, 0), (2.5, 540, 940, 1.1, 0)], g, 2)
    phone(c, 330, 700, 280, 560, state="on", glowing=True); wrench(c, 740, 560, 1.7, .6)
    q = e_back(prog(t, .3, .7)); c.save(); c.translate(540, 700); c.scale(q, q)
    circ(c, 0, 0, 380, None, hexc("#C2432F"), 40); line(c, -270, -270, 270, 270, 40, hexc("#C2432F")); c.restore()
    c.restore()
def _real3(c, k):
    t, g = k.t, k.g
    world(c, hexc("#F0C9A0")); rays(c, 540, 700, 22, (1, 1, 1, .14), -g * .08)
    c.save(); cam(c, t, [(0, 540, 960, 1.15, 0), (2.8, 540, 960, 1.0, 0)], g, 2)
    for i in range(6):
        col, row = i % 3, i // 3; x = 190 + col * 350; y = 760 + row * 470; t0 = .2 + i * .33
        if t < t0: continue
        person(c, x, y, .66, **CROWD[i], mouth="flat", brow="worry", look=0, blink=blinkamt(g, i))
        bubble(c, g, t0 + .2, x, y - 330, "কখন?", tail=(x, y - 235), size=46, t1=None)
    c.restore()
@scene(71.2, "cut")
def realize(c, k):
    acts(c, k, [(0, _real1), (4.3, _real2), (6.75, _real3)]); vignette(c, .3)

# 18 night, looks at the clock ---------------------------------------------
@scene(81.0, "iris", ix=780, iy=520)
def night(c, k):
    t, g = k.t, k.g
    world(c, hexc("#2A1E16")); pattern(c, "stripes", "#150e09", y0=-300, y1=1330, a=.4); rect(c, -800, 1330, 3400, 700, hexc("#1A110B"))
    c.save(); cam(c, t, [(0, 540, 960, 1.0, 0), (2.3, 560, 900, 1.1, 0), (4.6, 770, 540, 2.4, 0)], g, 2.2)
    wall_clock(c, 780, 520, 210, 22 * 60 + 40, g)
    person(c, 330, 1090, 1.15, **Z, mouth="flat", brow="flat" if g < 83.2 else "up", look=.2 if g < 83.2 else 1.0, tilt=0 if g < 83.2 else -.1, blink=blinkamt(g, .5))
    counter(c, g, ctop="#3a2410", cfront="#4a2f1b")
    c.restore()
    shutter(c, .26 - .0, "#5d5a53"); glow(c, 780, 520, 760, hexc("#FFC76B"), .22); vignette(c, .75)

# 19 ten phones + notebook ------------------------------------------------
def _ten(c, k):
    t, g = k.t, k.g
    world(c, hexc("#B98A55")); pattern(c, "stripes", "#7a5028", y0=-300, y1=1330, x1=2400, a=.2); rect(c, -800, 1330, 3600, 700, hexc("#6B4226"))
    c.save(); cam(c, t, [(0, 400, 900, 1.0, 0), (3.0, 1500, 900, 1.0, 0)], g, 2)
    rect(c, -200, 880, 2600, 40, hexc("#8A5A36")); rect(c, -200, 920, 2600, 420, hexc("#7A4B2A"))
    n = 0
    for i in range(10):
        ti = .3 + i * .26; on = t > ti; n += on
        fl = max(0, 1 - (t - ti) * 4) if on else 0
        phone(c, 200 + i * 205, 700, 135, 270, state="on" if on else "cracked", glowing=on and fl > 0)
        if on: text(c, bn(i + 1), 200 + i * 205, 520, 52, hexc("#FFF4DC"), "bold", stroke=hexc("#3a2418"), sw=6)
    person(c, 90, 1180, 1.0, **Z, mouth="flat", brow="angry", look=.8, hr=(160, -120), lean=.04 * math.sin(g * 6))
    c.restore()
    rect(c, 290, 80, 500, 100, hexc("#FFF7E8"), 50, hexc("#2b2118"), 5); stopwatch(c, 350, 130, 32, (t * 20) % 60)
    text(c, "ফোন " + bn(int(n)) + "/১০", 580, 130, 52, hexc("#2b2118"), "bold")
def _book(c, k):
    t, g = k.t, k.g
    world(c, hexc("#8A5A36")); pattern(c, "stripes", "#5a3418", y0=-300, y1=2000, a=.25, step=120)
    c.save(); cam(c, t, [(0, 540, 800, 1.1, 0), (3.2, 540, 700, 1.0, 0)], g, 2)
    rect(c, 60, 120, 960, 1160, hexc("#FFF2D4"), 14, hexc("#3a2418"), 8); rect(c, 140, 120, 8, 1160, hexc("#E08070"))
    for i in range(1, 15): line(c, 170, 120 + i * 78, 990, 120 + i * 78, 2, hexc("#CFE0E0") if False else (.55, .6, .65, .6))
    text(c, "সময়ের খাতা", 560, 215, 64, hexc("#C2432F"), "serif")
    st = 600; pen = None
    for i, d in enumerate(DUR):
        e0 = .35 + i * .27; r = prog(t, e0, e0 + .25); y = 330 + i * 86
        s_, e_ = st, st + d; st = e_ + 18
        fm = lambda m: bn("%02d:%02d" % (m // 60, m % 60))
        if r > 0:
            c.save(); c.new_path(); c.rectangle(160, y - 40, 860 * r, 80); c.clip()
            text(c, f"{bn(i + 1)}.", 200, y, 46, hexc("#2b2118"), "serif", anchor="l"); text(c, f"{fm(s_)} – {fm(e_)}", 290, y, 46, hexc("#2b2118"), "serif", anchor="l")
            text(c, f"{bn(d)} মি.", 820, y, 48, hexc("#C2432F"), "bold", anchor="l"); c.restore()
            if r < 1: pen = (160 + 860 * r, y)
    if pen:
        c.save(); c.translate(*pen); c.rotate(.9); rect(c, -8, -150, 16, 140, hexc("#E0A526"), 4); poly(c, [(-8, -10), (8, -10), (0, 18)], hexc("#e8c9a0")); c.restore()
    c.restore()
@scene(86.0, "wipe")
def tenphones(c, k):
    acts(c, k, [(0, _ten), (3.05, _book)]); vignette(c, .3)

# 20 bar chart ----------------------------------------------------------------
@scene(92.4, "cut")
def chart(c, k):
    t, g = k.t, k.g
    world(c, hexc("#2F3B2C")); pattern(c, "diag", "#ffffff", y0=-300, y1=2000, a=.03, step=70)
    c.save(); cam(c, t, [(0, 540, 800, 1.0, 0), (2.8, 540, 800, 1.0, 0), (3.5, 330, 640, 1.8, 0), (5.4, 330, 640, 1.8, 0), (6.1, 610, 800, 1.7, 0), (7.8, 540, 800, 1.05, 0)], g, 2)
    rect(c, 30, 40, 1020, 1300, None, 16, hexc("#8A5A36"), 22)
    text(c, "সাধারণ মডেল: স্ক্রিন বদল (মিনিট)", 540, 140, 46, hexc("#F5F1E6"), "bold")
    for v in (10, 20, 30, 40, 50):
        y = 1200 - v * 17; line(c, 90, y, 1000, y, 2, (1, 1, 1, .2)); text(c, bn(v), 70, y, 28, (1, 1, 1, .5), "bold", anchor="r")
    line(c, 90, 1200, 1000, 1200, 5, (1, 1, 1, .7))
    for i, d in enumerate(DUR):
        gr = e_out(prog(t, .2 + i * .13, .9 + i * .13)); h = d * 17 * gr; x = 120 + i * 88
        col = "#E0A526"
        if i == 2 and g > 95.6: col = "#D9482B"
        if i == 5 and g > 98.0: col = "#7FB069"
        rect(c, x, 1200 - h, 66, h, hexc(col), 8)
        if gr > .95: text(c, bn(d), x + 33, 1200 - h - 26, 34, hexc("#FFF4DC"), "bold")
    if g > 95.6:
        p = e_back(prog(g, 95.6, 95.95)); c.save(); c.translate(330, 250); c.scale(p, p); text(c, "সর্বোচ্চ\n৫০ মিনিট", 0, 0, 44, hexc("#FF9F7A"), "bold", stroke=hexc("#2F3B2C"), sw=6); c.restore()
    if g > 98.0:
        p = e_back(prog(g, 98.0, 98.35)); c.save(); c.translate(560, 980); c.scale(p, p); text(c, "সর্বনিম্ন\n৪০ মিনিট", 0, 0, 50, hexc("#A8E08A"), "bold", stroke=hexc("#2F3B2C"), sw=6); c.restore()
    c.restore(); vignette(c, .4)

# 21 morning, strike out old line --------------------------------------------
@scene(100.2, "flash")
def strike(c, k):
    t, g = k.t, k.g
    world(c, vgrad(hexc("#F6C453"), hexc("#F2A24B"), -200, 1500)); sun_y = 1100 - e_out(prog(t, 0, 2.5)) * 500
    rays(c, 540, sun_y, 18, (1, 1, 1, .16), g * .1); circ(c, 540, sun_y, 200, hexc("#FFF0C0")); glow(c, 540, sun_y, 600, hexc("#FFF0C0"), .5)
    c.save(); cam(c, t, [(0, 540, 1250, 1.1, 0), (2.8, 540, 800, 1.5, 0)], g, 2)
    rect(c, -300, 280, 1700, 1100, hexc("#C98F5B")); pattern(c, "bricks", "#8a5a30", y0=280, y1=1380, a=.3); rect(c, -300, 1330, 1700, 500, hexc("#8F8777"))
    banner(c, 540, 780, 900, 360, "দ্রুত ও নির্ভরযোগ্য", "মোবাইল সার্ভিস", g, sz=72)
    r = e_io(prog(t, 1.0, 2.2)); 
    if r > 0:
        line(c, 110, 800, 110 + 860 * r, 760, 26, hexc("#D9302B"), cairo.LINE_CAP_ROUND)
        c.save(); c.translate(110 + 860 * r, 760 - 0 * r); c.rotate(.8); rect(c, -10, -160, 20, 150, hexc("#2b2118"), 6); rect(c, -10, -160, 20, 40, hexc("#D9302B"), 6); c.restore()
    person(c, 150, 1480, 1.3, **Z, mouth="grit" if r < 1 else "smile", brow="angry" if r < 1 else "up", hr=(200, -420), look=.8)
    c.restore(); vignette(c, .25)

# 22 new banner ----------------------------------------------------------------
@scene(103.0, "wipe")
def newbanner(c, k):
    t, g = k.t, k.g
    world(c, hexc("#F3E3BF")); pattern(c, "diag", "#E8C47A", y0=-300, y1=2000, a=.35, step=110)
    c.save(); sh = 2 + (30 * math.exp(-(t - 4.6) * 8) if t > 4.6 else 0); cam(c, t, [(0, 540, 640, 1.7, 0), (3.5, 540, 700, 1.45, 0), (5.0, 540, 860, 1.05, 0)], g, sh)
    r1 = prog(t, 1.62, 3.2); r2 = prog(t, 3.3, 4.2)
    banner(c, 540, 640, 960, 480, "সাধারণ মডেলের স্ক্রিন বদলান", "৫০ মিনিটে।", g, r1, r2, bg="#FFF8E6", sz=68)
    tip = None
    if 0 < r1 < 1: tip = (50 + 940 * r1, 590)
    elif 0 < r2 < 1: tip = (150 + 700 * r2, 735)
    if tip: c.save(); c.translate(*tip); c.rotate(.8); rect(c, -9, -170, 18, 160, hexc("#2b2118"), 6); rect(c, -9, -170, 18, 40, hexc("#C2432F"), 6); c.restore()
    if t > 4.6:
        p = e_out(prog(t, 4.6, 4.9)); sc = lerp(2.6, 1.0, p)
        c.save(); c.translate(500, 1060); c.rotate(-.1); c.scale(sc, sc); c.set_source_rgba(0, 0, 0, 0)
        rect(c, -330, -110, 660, 220, hexc("#FFF2D8", .96), 30, hexc("#C2432F"), 10); rect(c, -310, -90, 620, 180, None, 22, hexc("#C2432F"), 3)
        text(c, "না পারলে\nচার্জ অর্ধেক", -60, 0, 64, hexc("#C2432F"), "bold")
        c.save(); c.translate(240, 0); circ(c, 0, 0, 62, hexc("#E0A526"), hexc("#A6720F"), 6); c.new_path(); c.rectangle(0, -70, 80, 140); setc(c, hexc("#FFF2D8")); c.fill(); text(c, "১/২", 0, 0, 44, hexc("#7a4a0c"), "bold"); c.restore()
        c.restore()
        for i in range(8): star(c, 500 + math.cos(i) * 380 * p, 1060 + math.sin(i * 1.7) * 160 * p, 16 * (1 - p * .6), hexc("#E0A526"), g)
    c.restore(); vignette(c, .22)

# 23 six customers wait ---------------------------------------------------------
@scene(109.6, "push_l")
def six(c, k):
    t, g = k.t, k.g
    c.save(); cam(c, t, [(0, 480, 960, 1.0, 0), (4.6, 540, 960, 1.0, 0), (6.6, 800, 640, 1.55, 0)], g, 2.5)
    rem = int(max(0, 3000 - max(0, t - 4.7) * 60)); 
    interior(c, g, wall="#B9C89A", pat="dots", pcol="#7A8F55", floor="#6E5A3C", clock_r=130, tmin=600 + t * .1, pa=.2)
    if t > 4.8:
        rect(c, 700, 500, 280, 84, hexc("#2b2118"), 14); text(c, bn("%02d:%02d" % (rem // 60, rem % 60)), 840, 542, 56, hexc("#FFB347"), "bold")
    person(c, 960, 1090, 1.0, **Z, mouth="smile", brow="flat", look=-.5, hr=(110, -150), blink=blinkamt(g, 1))
    counter(c, g)
    for i in range(6):
        t0 = .3 + i * .55
        if t < t0: continue
        tx = 120 + i * 135; x = clamp(-200 + (t - t0) / .9 * (tx + 200), -200, tx); mv = (t - t0) < .95; wk = g * 9
        ti = prog(t, 4.7, 5.0)
        person(c, x, 1090, .8, **CROWD[i], legs=True, walk=wk + i if mv else 0, bob=abs(math.sin(wk + i)) * 5 if mv else 0, mouth="flat", brow="up" if ti > 0 else "flat", look=.9 if ti > 0 else 0, blink=blinkamt(g, i))
        if not mv:
            p = e_back(prog(t - t0, .9, 1.25)); c.save(); c.translate(x, 1090 - 345 * .8 - 120 - (1 - p) * 40); c.scale(p, p); circ(c, 0, 0, 36, hexc("#E0A526"), hexc("#2b2118"), 4); text(c, bn(i + 1), 0, 0, 44, hexc("#2b2118"), "bold"); c.restore()
    if 2.3 < t < 4.5:
        bubble(c, g, 112.0, 460, 470, "দাম কত?", tail=(420, 620), size=50)
        if g > 112.5: line(c, 330, 410, 590, 540, 18, hexc("#D9302B")); line(c, 590, 410, 330, 540, 18, hexc("#D9302B"))
    c.restore(); vignette(c, .25)

# 24 week three ------------------------------------------------------------------
@scene(116.9, "flash")
def week3(c, k):
    t, g = k.t, k.g
    world(c, vgrad(hexc("#4A2A22"), hexc("#2A1511"), -200, 1900)); rays(c, 540, 800, 14, (.9, .3, .2, .1), g * .1)
    c.save(); cam(c, t, [(0, 540, 960, 1.0, -2), (2.9, 540, 800, 1.4, 2)], g, 2.5)
    text(c, "তৃতীয় সপ্তাহ", 540, 250, 110, hexc("#FFE9B8"), "bold", stroke=hexc("#7a1f12"), sw=10)
    for r in range(4):
        for col in range(7):
            x = 90 + col * 130; y = 420 + r * 190; n = r * 7 + col + 1
            hl = r == 2 and t > 1.2
            rect(c, x, y, 118, 160, hexc("#FFF4DC") if not hl else hexc("#FFD9C9"), 12, hexc("#7a1f12") if hl else None, 6)
            text(c, bn(n), x + 59, y + 100, 40, hexc("#4a2a22"), "bold")
            if r < 2 and t > r * .5 + col * .06:
                pp = e_back(prog(t, r * .5 + col * .06, r * .5 + col * .06 + .2)); c.save(); c.translate(x + 59, y + 50); c.scale(pp, pp); checkmark(c, 0, 0, 56, hexc("#4F8A3C"), 12); c.restore()
    if t > 1.2:
        pulse = 1 + .06 * math.sin(g * 9); rect(c, 70, 780 - 10, 910 * pulse - 0, 180, None, 20, hexc("#FF5A3C"), 8)
        text(c, "?", 540, 870, 200, (1, .35, .25, .5 + .3 * math.sin(g * 9)), "bold")
    c.restore(); vignette(c, .6, (.2, .02, .02))

# 25 the rare phone ---------------------------------------------------------------
@scene(119.8, "cut")
def rare(c, k):
    t, g = k.t, k.g
    c.save(); sh = 2.5 + (35 * math.exp(-(t - 3.6) * 7) if t > 3.6 else 0)
    cam(c, t, [(0, 540, 960, 1.0, 0), (2.6, 600, 900, 1.3, 0), (3.5, 540, 760, 1.15, 0), (6.1, 540, 820, 1.2, 0)], g, sh)
    interior(c, g, wall="#D8C7A8", pat="tiles", pcol="#8a7550", floor="#7A5A3A", clock=False, pa=.18)
    wob = 0
    person(c, 340, 1090, 1.15, **Z, mouth="o" if g < 123.3 else "frown", brow="worry", look=.5, sweat=(g * .5) % 1 if t > 2 else 0, hl=(-60, -200),
           hr=(150, -250), blink=blinkamt(g, .7), hold_r=lambda cc: (circ(cc, 0, -50, 46, (.9, .95, 1, .35), hexc("#4a3a28"), 9), line(cc, 30, -18, 60, 30, 12, hexc("#4a3a28"))))
    counter(c, g)
    rare_phone(c, 560, 970, .75, math.sin(g * 3) * .02) if t > 1.9 else None
    cx = clamp(-250 + t / 1.8 * 1010, -250, 760); mv = t < 1.85; wk = g * 9
    person(c, cx, 1060, 1.1, **KURTA, legs=True, walk=wk if mv else 0, bob=abs(math.sin(wk)) * 7 if mv else 0, flip=True, mouth="smile", brow="flat", look=-.6, hl=(-100, -20), hr=(130, -20) if t > 1.9 else (150, -250),
           hold_r=None if t > 1.9 else (lambda cc: rare_phone(cc, 10, -70, .45, .1)), blink=blinkamt(g, 1.3))
    if t > 1.9:
        stopwatch(c, 190, 400, 120, (t - 2.0) * 38 % 60)
    if t > 3.6:
        p = e_back(prog(t, 3.6, 3.95)); c.save(); c.translate(540, 560); c.rotate(-.06); c.scale(p, p)
        text(c, "৭০ মিনিট", 0, 0, 190, hexc("#D9302B"), "bold", stroke=hexc("#FFF4DC"), sw=16); c.restore()
    c.restore()
    if t > 3.6: vignette(c, .5 + .2 * math.sin(g * 8), (.5, .02, .02))
    else: vignette(c, .3)
