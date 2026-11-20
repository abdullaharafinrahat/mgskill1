"""Script 6: scenes 26-35 - the rest of the script (after the audio file ends), driven by reading-pace timeline."""
from sets import *

def E1(): return 125.9
@scene(125.9, "cut")
def handover(c, k):
    t, g = k.t, k.g
    c.save(); cam(c, t, [(0, 540, 960, 1.0, 0), (2.5, 540, 900, 1.15, 0), (2.9, 340, 800, 1.5, 0), (5.3, 340, 800, 1.5, 0), (5.5, 540, 900, 1.3, 0), (7.6, 650, 850, 1.35, 0)], g, 2.5)
    interior(c, g, wall="#F0D9A6", pat="stripes", pcol="#D2A94E", floor="#8B5E3C", poster=True, tmin=11 * 60 + 5 + t * .1)
    q = e_io(prog(g, 126.5, 128.3)); 
    person(c, 340, 1090, 1.15, **Z, mouth="smile", talk=max(talkamt(g, 128.7, 130.9), talkamt(g, 131.2, 133.3)), brow="flat", look=.6, hr=(190 - 40 * q, -200), blink=blinkamt(g, .4))
    counter(c, g)
    person(c, 760, 1060, 1.1, **KURTA, legs=True, flip=True, mouth="smile" if g < 135 else "big", look=-.6, hl=(-120 * q - 80, -20 - 200 * q), hr=(120, -10), blink=blinkamt(g, 1))
    px = lerp(480, 640, q); py = lerp(870, 800, q) + math.sin(q * math.pi) * -20
    phone(c, px, py, 90, 170, rot=lerp(.5, -.2, q), state="on", glowing=True)
    bubble(c, g, 128.7, 330, 520, "ভাই, আমার কথা\nরাখতে পারিনি।", tail=(340, 690), t1=131.1, size=50)
    bubble(c, g, 131.2, 330, 520, "তাই শ্রমের চার্জ\nঅর্ধেক দিন।", tail=(340, 690), size=50)
    if g > 131.8:
        p = e_back(prog(g, 131.8, 132.2)); sp = e_io(prog(g, 132.6, 133.4)) * 120
        c.save(); c.translate(560, 800 - sp * .5); c.scale(p, p)
        for sd in (-1, 1):
            c.save(); c.translate(sd * sp * .6, sd * -sp * .15); c.rotate(sd * sp * .002); c.new_path(); c.rectangle(-2 if sd > 0 else -100, -100, 102 if sd < 0 else 100, 200); c.clip(); circ(c, 0, 0, 66, hexc("#E0A526"), hexc("#A6720F"), 8); text(c, "৳", 0, 0, 70, hexc("#A6720F"), "bold"); c.restore()
        c.restore()
    c.restore(); vignette(c, .25)

@scene(U(64) - .25, "wipe")
def surprise(c, k):
    def a1(c, k):
        t, g = k.t, k.g
        world(c, hexc("#E9B58F")); pattern(c, "dots", "#B8744A", y0=-300, y1=2000, a=.25, step=110); rays(c, 540, 700, 18, (1, .9, .7, .18), g * .1)
        c.save(); cam(c, t, [(0, 540, 960, 1.0, 0), (4.3, 540, 880, 1.15, 0)], g, 2.5)
        sh = e_back(prog(g, 134.0, 134.4))
        person(c, 540, 1300, 1.8, **KURTA, mouth="shock" if g < 135.7 else "o", talk=talkamt(g, 135.8, 137.9, 11) , brow="up", look=.0, blink=blinkamt(g, .3), hl=(-130, -150), hr=(130, -150))
        if sh > .02: c.save(); c.translate(820, 460); c.scale(sh, sh); text(c, "!", 0, 0, 260, hexc("#D9302B"), "bold", stroke=hexc("#FFF4DC"), sw=12, rot=.2); c.restore()
        bubble(c, g, 135.8, 540, 280, "আপনি নিজে থেকেই\nকমাচ্ছেন?", tail=(540, 540), size=56)
        c.restore()
    def a2(c, k):
        t, g = k.t, k.g
        world(c, hexc("#CFDDA8")); rays(c, 540, 700, 18, (1, 1, 1, .2), -g * .1)
        c.save(); cam(c, t, [(0, 540, 960, 1.15, 0), (2.0, 540, 900, 1.0, 0)], g, 2.5)
        person(c, 540, 1300, 1.8, **Z, mouth="smile", brow="up", tilt=.1 * math.sin(g * 6) if g > 138.4 else 0, blink=blinkamt(g), hl=(-120, -100), hr=(120, -100), bob=abs(math.sin(g * 6)) * 5 if g > 138.4 else 0)
        c.restore()
    acts(c, k, [(0, a1), (4.3, a2)]); vignette(c, .25)

@scene(U(67) - .25, "push_l")
def brother(c, k):
    t, g = k.t, k.g
    c.save(); cam(c, t, [(0, 420, 960, 1.1, 0), (3.5, 720, 960, 1.0, 0)], g, 2.5)
    street(c, g, sky=("#F8D49A", "#FDEFD0"), seed=5); shopfront(c, g, 480, 820)
    rect(c, 640, 1210, 240, 80, hexc("#FFF7E8"), 10, hexc("#C2432F"), 5); text(c, "৫০ মিনিটে", 760, 1250, 42, hexc("#C2432F"), "bold")
    for i in range(3): person(c, 960 + i * 110, 1190, .55, **CROWD[i + 2], mouth="smile", look=-.8)
    wk = g * 8; x1 = -200 + e_out(prog(t, 0, 3.4)) * 900; mv = t < 3.3
    person(c, x1 - 190, 1160, .95, **BROTHER, legs=True, walk=wk + 1 if mv else 0, bob=abs(math.sin(wk + 1)) * 6 if mv else 0, mouth="big", brow="up", look=.7, hl=(-90, -20), hr=(150, -150))
    person(c, x1, 1160, .95, **KURTA, legs=True, walk=wk if mv else 0, bob=abs(math.sin(wk)) * 6 if mv else 0, mouth="big", look=.9, hl=(-150, -150), hr=(120, -20))
    c.restore()
    p = e_back(prog(t, .2, .6)); c.save(); c.translate(300, 260); c.scale(p, p); rect(c, -260, -60, 520, 120, hexc("#FFF7E8"), 60, hexc("#2b2118"), 5); text(c, "পরের সপ্তাহে", 0, 0, 56, hexc("#2b2118"), "bold"); c.restore()
    vignette(c, .2)

@scene(U(68) - .25, "iris", ix=540, iy=700)
def lesson(c, k):
    def a1(c, k):
        t, g = k.t, k.g
        world(c, hexc("#E7D8B0")); rays(c, 540, 650, 18, (1, .8, .4, .2), g * .1)
        c.save(); cam(c, t, [(0, 540, 900, 1.15, 0), (3.6, 540, 900, 1.0, 0)], g, 2.5)
        for i in range(8): line(c, 60 + rnd(i) * 200, 380 + i * 80, 260 + rnd(i) * 200 + (g * 400 + i * 90) % 400, 380 + i * 80, 8, (.35, .25, .15, .35))
        stopwatch(c, 560, 650, 250, (g * 25) % 60)
        p = e_back(prog(t, 1.4, 1.8)); c.save(); c.translate(540, 1100); c.scale(p, p); text(c, "শুধু দ্রুত কাজ", 0, 0, 80, hexc("#4a2a12"), "bold"); line(c, -330, 0, 330, 0, 14, hexc("#D9302B")); c.restore()
        c.restore()
    def a2(c, k):
        t, g = k.t, k.g
        world(c, hexc("#D9A76A")); pattern(c, "diag", "#ffffff", y0=-300, y1=2000, a=.1, step=90); glow(c, 540, 700, 700, hexc("#FFF0C0"), .5)
        c.save(); cam(c, t, [(0, 540, 800, 1.2, 0), (2.8, 540, 820, 1.0, 0)], g, 2)
        pp = e_back(prog(t, .1, .6)); c.save(); c.translate(540, 700); c.scale(pp, pp); c.rotate(-.03)
        ell(c, -350, 0, 30, 280, hexc("#E8D3A6"), 0, hexc("#7a5a30"), 4); ell(c, 350, 0, 30, 280, hexc("#E8D3A6"), 0, hexc("#7a5a30"), 4)
        rect(c, -350, -280, 700, 560, hexc("#FFF2D4"), 6, hexc("#7a5a30"), 4); text(c, "প্রতিশ্রুতি", 0, -150, 100, hexc("#7a1f12"), "bold", kind="serif") if False else text(c, "প্রতিশ্রুতি", 0, -150, 100, hexc("#7a1f12"), "serif")
        for i in range(3): line(c, -250, -40 + i * 60, 250 - i * 40, -40 + i * 60, 6, hexc("#b8a27a"))
        sp = e_back(prog(t, 1.2, 1.6)) * (1 + .05 * math.sin(g * 6)); c.save(); c.translate(190, 190); c.scale(sp, sp); circ(c, 0, 0, 80, hexc("#C2432F"), hexc("#7a1f12"), 8); star(c, 0, 0, 46, hexc("#FFD58A"), g * .2); c.restore(); c.restore()
        c.restore()
    acts(c, k, [(0, a1), (3.95, a2)]); vignette(c, .25)

@scene(U(70) - .25, "zoom")
def book(c, k):
    t, g = k.t, k.g
    world(c, vgrad(hexc("#6B2E22"), hexc("#35150F"), -200, 1900)); glow(c, 540, 700, 800, hexc("#FFD58A"), .35)
    c.save(); cam(c, t, [(0, 540, 760, 1.0, 0), (5.7, 540, 700, 1.22, 0)], g, 2)
    e = e_back(prog(t, .1, .9)); c.save(); c.translate(540, 760 + (1 - e) * 1200 + math.sin(g * 1.6) * 8); c.rotate((1 - e) * .5 + math.sin(g) * .015)
    rect(c, -320, -430, 640, 860, (0, 0, 0, .3), 14); rect(c, -330, -440, 650, 870, hexc("#F3E3BF"), 14, hexc("#3a2418"), 8); rect(c, -330, -440, 60, 870, hexc("#8E3B33"), 14)
    rect(c, -250, -380, 530, 360, hexc("#8E3B33"), 10, hexc("#E0A526"), 6); text(c, "TESTED\nADVERTISING\nMETHODS", 15, -200, 66, hexc("#FFE9B0"), "serif")
    line(c, -200, 0, 240, 0, 5, hexc("#E0A526")); text(c, "JOHN CAPLES", 15, 100, 62, hexc("#3a2418"), "serif"); text(c, "জন ক্যাপলস", 15, 210, 70, hexc("#8E3B33"), "bold")
    for i in range(3): star(c, 250 - i * 50, 330, 14, hexc("#E0A526"), g)
    c.restore()
    for i in range(8):
        pp = ((g * .4 + i / 8) % 1); star(c, 120 + rnd(i) * 840, 1200 - pp * 1000, 8 + 12 * rnd(i, 1), (1, .9, .6, math.sin(pp * math.pi)), g * 2 + i)
    c.restore(); vignette(c, .45)

@scene(U(71) - .25, "wipe")
def claims(c, k):
    def a1(c, k):
        t, g = k.t, k.g
        world(c, vgrad(hexc("#CFD8B0"), hexc("#E9E2C0"), -200, 1900)); pattern(c, "dots", "#8FA070", y0=-300, y1=2000, a=.2, step=110)
        c.save(); cam(c, t, [(0, 540, 960, 1.0, 0), (3.6, 540, 900, 1.08, 0)], g, 2)
        for i, (lab, col, tp) in enumerate((("ভালো", "#E0A526", 158.0), ("সেরা", "#C2432F", 158.7), ("দ্রুত", "#5E7F4A", 159.3))):
            bx = 220 + i * 320; by = 700 + math.sin(g * 1.5 + i) * 30 - i % 2 * 80
            if g < tp:
                line(c, bx, by + 150, bx + math.sin(g * 2 + i) * 20, by + 420, 4, hexc("#6a5a40")); ell(c, bx, by, 130, 160, hexc(col), 0, hexc("#2b2118"), 5); poly(c, [(bx - 14, by + 160), (bx + 14, by + 160), (bx, by + 185)], hexc(col))
                text(c, lab, bx, by - 10, 66, (1, 1, 1), "bold"); ell(c, bx - 45, by - 70, 20, 36, (1, 1, 1, .35), .5)
            else:
                pp = prog(g, tp, tp + .5)
                for j in range(10): a = j * math.pi / 5; circ(c, bx + math.cos(a) * 190 * pp, by + math.sin(a) * 190 * pp, 14 * (1 - pp), hexc(col))
                text(c, lab, bx, by + 330 * pp, 60, (.35, .3, .25, 1 - pp * .5), "bold")
        if g > 159.4:
            p = e_back(prog(g, 159.4, 159.8)); c.save(); c.translate(540, 1150); c.rotate(-.05); c.scale(p, p); rect(c, -260, -80, 520, 160, hexc("#FFF4DC"), 24, hexc("#C2432F"), 10); text(c, "শুধু দাবি", 0, 0, 100, hexc("#C2432F"), "bold"); c.restore()
        c.restore()
    def a2(c, k):
        t, g = k.t, k.g
        world(c, hexc("#F1D9A0")); rays(c, 540, 600, 20, (1, 1, 1, .25), g * .1)
        c.save(); cam(c, t, [(0, 540, 940, 1.15, 0), (4.3, 540, 900, 1.0, 0)], g, 2)
        p = e_back(prog(t, .1, .6)); c.save(); c.translate(540, 560); c.scale(p, p); text(c, "৫০", 0, 0, 420, hexc("#7a1f12"), "bold", stroke=hexc("#FFF4DC"), sw=18); text(c, "মিনিট", 0, 270, 130, hexc("#3a2418"), "bold"); c.restore()
        tp = e_out(prog(t, .6, 1.6)); rect(c, 60, 1020, 960 * tp, 120, hexc("#E6C23A"), 10, hexc("#6a5a10"), 5)
        for i in range(0, int(60 * tp)): line(c, 60 + i * 16, 1020, 60 + i * 16, 1020 + (50 if i % 5 == 0 else 28), 4, hexc("#3a2a08"))
        if g > 162.6:
            q = e_back(prog(g, 162.6, 163.0)); c.save(); c.translate(860, 330); c.scale(q, q); circ(c, 0, 0, 100, hexc("#4F8A3C"), hexc("#FFF4DC"), 10); checkmark(c, 0, 5, 100, (1, 1, 1), 22); c.restore()
        c.restore()
    acts(c, k, [(0, a1), (3.9, a2)]); vignette(c, .22)

@scene(U(73) - .25, "push_u")
def takeaway(c, k):
    def a1(c, k):
        t, g = k.t, k.g
        world(c, hexc("#E5A15E")); pattern(c, "stripes", "#B8691F", y0=-300, y1=2000, a=.18, step=100)
        c.save(); cam(c, t, [(0, 540, 960, 1.0, 0), (6, 540, 900, 1.1, 0)], g, 2)
        e = e_back(prog(t, .1, .6)); c.save(); c.translate(540, 300); c.scale(e, e); rect(c, -400, -70, 800, 140, hexc("#3a2418"), 70); text(c, "Practical takeaway", 0, 0, 62, hexc("#FFE9B0"), "serif"); c.restore()
        person(c, 330, 1330, 1.35, **Z, mouth="flat", brow="worry", look=-.6, hl=(-90, -120), hr=(60, -290), tilt=.06 * math.sin(g), blink=blinkamt(g))
        pp = e_back(prog(t, 1.2, 1.7)); c.save(); c.translate(770, 760); c.rotate(.06); c.scale(pp, pp)
        rect(c, -230, -310, 460, 620, hexc("#FFF7E8"), 12, hexc("#3a2418"), 6); rect(c, -190, -270, 380, 90, hexc("#C2432F"), 8); text(c, "আমার\nবিজ্ঞাপন", 0, -225, 40, (1, 1, 1), "bold")
        for i in range(5): line(c, -170, -90 + i * 70, 170 - (i % 2) * 70, -90 + i * 70, 10, hexc("#cdbf9a"))
        c.restore()
        if g > 168.0: qmarks(c, g, 330, 560, 3, 130)
        c.restore()
    def a2(c, k):
        t, g = k.t, k.g
        world(c, hexc("#F3E3BF")); pattern(c, "dots", "#E0A526", y0=-300, y1=2000, a=.2, step=110)
        c.save(); cam(c, t, [(0, 540, 800, 1.2, 0), (3.2, 540, 880, 1.0, 0)], g, 2)
        banner(c, 540, 420, 900, 300, "৫০ মিনিটে স্ক্রিন বদল", "", g, bg="#FFF8E6", sz=66)
        stopwatch(c, 540, 1000, 230, 50 * e_io(prog(t, .4, 2.4)))
        if g > 173.2:
            q = e_back(prog(g, 173.2, 173.6)); c.save(); c.translate(840, 780); c.rotate(-.1); c.scale(q, q); rect(c, -190, -70, 380, 140, hexc("#4F8A3C"), 24, hexc("#FFF4DC"), 8); text(c, "মিলেছে", 0, 0, 80, (1, 1, 1), "bold"); c.restore()
        c.restore()
    acts(c, k, [(0, a1), (6.15, a2)]); vignette(c, .22)

@scene(U(76) - .25, "iris", ix=840, iy=330)
def endshot(c, k):
    t, g = k.t, k.g
    c.save(); cam(c, t, [(0, 840, 340, 1.8, 0), (3.2, 600, 900, 1.0, 0), (7.5, 440, 880, 1.2, 0)], g, 2.5)
    interior(c, g, wall="#F0B96B", pat="diag", pcol="#D98F3A", floor="#7A4B2A", clock_r=130, tmin=11 * 60 + 50 + t * .1, pa=.3)
    glow(c, 840, 330, 600, hexc("#FFF0C0"), .5)
    person(c, 340, 1090, 1.15, **Z, mouth="smile" if g < 179.8 else "big", brow="up", look=.9 if g < 180 else 0, tilt=-.08 if g < 180 else 0, blink=blinkamt(g, .5), hr=(110, -150) if g < 179.8 else (150, -330))
    counter(c, g)
    person(c, 780, 1060, 1.05, **CUST1, legs=True, flip=True, mouth="smile", look=-.6, hl=(-100, -20), hr=(120, -10), blink=blinkamt(g, 1.4))
    person(c, 960, 1070, .9, **CROWD[3], legs=True, mouth="big", look=-.8)
    c.restore(); vignette(c, .3)

@scene(U(79) - .25, "flash")
def balance(c, k):
    t, g = k.t, k.g
    world(c, vgrad(hexc("#33261E"), hexc("#1C130E"), -200, 1900)); glow(c, 540, 700, 800, hexc("#FFD58A"), .3)
    c.save(); cam(c, t, [(0, 540, 800, 1.1, 0), (5, 540, 760, 1.0, 0)], g, 2)
    th = lerp(-.12, .3, e_io(prog(g, 185.0, 186.0))) + math.sin(g * 3) * .01 * (1 - prog(g, 185, 186.6))
    px, py, L = 540, 450, 360
    rect(c, px - 20, py, 40, 700, hexc("#8A5A36"), 10); rect(c, px - 160, py + 690, 320, 50, hexc("#6B4226"), 14); circ(c, px, py, 34, hexc("#E0A526"))
    lx, ly = px - L * math.cos(th), py - L * math.sin(th); rx, ry = px + L * math.cos(th), py + L * math.sin(th)
    line(c, lx, ly, rx, ry, 22, hexc("#E0A526"))
    for (x, y) in ((lx, ly), (rx, ry)):
        line(c, x, y, x - 130, y + 300, 4, hexc("#c9b080")); line(c, x, y, x + 130, y + 300, 4, hexc("#c9b080")); ell(c, x, y + 305, 170, 30, hexc("#C99A5B"), 0, hexc("#6a4a20"), 4)
    if g > 182.6:
        e = e_back(prog(g, 182.6, 183.0)); c.save(); c.translate(lx, ly + 150); c.scale(e, e); 
        for (ox, oy, r) in ((-60, 0, 70), (0, -30, 85), (60, 0, 70)): circ(c, ox, oy, r, (1, 1, 1, .55), hexc("#FFF4DC"), 5)
        text(c, "দ্রুত", 0, -5, 64, hexc("#7a6a52"), "bold"); c.restore()
    if g > 184.7:
        dy = (1 - e_out(prog(g, 184.7, 185.2))) * -600; c.save(); c.translate(rx, ry + 200 + dy)
        rect(c, -150, -95, 300, 190, hexc("#E0A526"), 18, hexc("#7a4a0c"), 8); rect(c, -150, -95, 300, 50, hexc("#F6CF62"), 18); text(c, "৫০\nমিনিট", 0, 5, 56, hexc("#5a3408"), "bold"); c.restore()
    if g > 183.0:
        e = e_back(prog(g, 183.0, 183.5)); c.save(); c.translate(lx, 1120); c.scale(e, e); text(c, "দাবি", 0, 0, 100, hexc("#C9B8A0"), "bold", stroke=hexc("#1C130E"), sw=8); c.restore()
    if g > 185.6:
        e = e_back(prog(g, 185.6, 186.0)); c.save(); c.translate(rx, 1120); c.scale(e, e); text(c, "প্রতিশ্রুতি", 0, 0, 90, hexc("#FFD25A"), "bold", stroke=hexc("#1C130E"), sw=8); c.restore()
    c.restore(); vignette(c, .45)

@scene(U(81) - .25, "wipe")
def cta(c, k):
    t, g = k.t, k.g
    world(c, vgrad(hexc("#D9482B"), hexc("#8E2A18"), -200, 1900)); rays(c, 540, 800, 20, (1, .8, .5, .12), g * .12)
    c.save(); cam(c, t, [(0, 540, 960, 1.1, 0), (4.4, 540, 940, 1.0, 0)], g, 2)
    text(c, "এমন আরও\npractical গল্পের জন্য", 540, 330, 74, hexc("#FFF4DC"), "bold", stroke=hexc("#5a1a0e"), sw=8)
    tap = prog(g, 189.4, 189.6); pul = 1 + .04 * math.sin(g * 6) - .1 * math.sin(tap * math.pi)
    c.save(); c.translate(540, 760); c.scale(pul, pul); rect(c, -300, -90, 600, 180, hexc("#FFF4DC") if g < 189.5 else hexc("#4F8A3C"), 90, hexc("#2b2118"), 8)
    text(c, "Follow করুন" if g < 189.5 else "ফলো করা হয়েছে", 0, 0, 74 if g < 189.5 else 56, hexc("#C2432F") if g < 189.5 else (1, 1, 1), "bold"); c.restore()
    fx = lerp(900, 640, e_out(prog(g, 188.4, 189.4))); fy = lerp(1100, 800, e_out(prog(g, 188.4, 189.4)))
    c.save(); c.translate(fx, fy); c.rotate(-.4); rect(c, -26, -20, 52, 150, hexc("#E6B68A"), 24, hexc("#2b2118"), 4); circ(c, 0, -20, 26, hexc("#E6B68A"), hexc("#2b2118"), 4); c.restore()
    if g > 189.5:
        for i in range(10):
            pp = prog(g, 189.5, 191.5); a = i * math.pi / 5 + .3
            heart(c, 540 + math.cos(a) * 420 * pp, 760 + math.sin(a) * 300 * pp - pp * 100, .9 * (1 - pp * .5), hexc("#FFD58A" if i % 2 else "#FFF4DC"))
    person(c, 540, 1560, 1.0, **Z, mouth="big", brow="up", hr=(150, -330 + math.sin(g * 7) * 40), hl=(-120, -20), blink=blinkamt(g))
    c.restore(); vignette(c, .35)
