"""Script 4a: shared sets/backdrops/props, scene registry and in-scene act transitions."""
import json, math
from lib2d import *
TL = json.load(open("/tmp/work/timeline.json")); UN = TL["units"]; END = TL["end"]
def U(i): return UN[i]["start"]
SCENES = []
class K:
    def __init__(s, t, g, d): s.t, s.g, s.d = t, g, d
def scene(start, trans="cut", td=.45, **kw):
    def deco(fn): SCENES.append(dict(start=start, fn=fn, trans=trans, td=td, kw=kw)); return fn
    return deco
def acts(c, k, lst, td=.45):
    """lst=[(t0, fn)]: push transition between acts inside a scene. fn(c, k)"""
    i = max([j for j, (t0, _) in enumerate(lst) if k.t >= t0] or [0])
    if i > 0 and k.t < lst[i][0] + td:
        e = e_io(prog(k.t, lst[i][0], lst[i][0] + td))
        c.save(); c.translate(-e * W, 0); lst[i - 1][1](c, K(k.t - lst[i - 1][0], k.g, 99)); c.restore()
        c.save(); c.translate((1 - e) * W, 0); c.rectangle(0, 0, W, H); c.clip(); c.new_path(); lst[i][1](c, K(k.t - lst[i][0], k.g, 99)); c.restore()
    else: lst[i][1](c, K(k.t - lst[i][0], k.g, 99))

# --- people presets
Z = dict(skin=SKIN["a"], hair="#1b1411", shirt="#5E7F4A", pants="#3a2e27", beard="stubble")
CUST1 = dict(skin=SKIN["b"], hair="#241a14", shirt="#9A5B45", pants="#4a4036", beard="stubble")
GIRL = dict(skin=SKIN["c"], hair="#1a1210", style="braid", outfit="uniform")
KURTA = dict(skin=SKIN["d"], hair="#2a2420", style="topi", outfit="kurta", shirt="#8E3B33", beard="full")
FATHER = dict(skin=SKIN["a"], hair="#A39D92", style="bald", shirt="#7B5B3E", beard="mustache", glasses=True)
BROTHER = dict(skin=SKIN["b"], hair="#1d1612", shirt="#4F8A5B", pants="#3a3a33")
CROWD = [dict(skin=SKIN["a"], hair="#1b1411", shirt="#9A5B45"), dict(skin=SKIN["c"], hair="#2a1d16", shirt="#C8892B", style="braid"),
         dict(skin=SKIN["d"], hair="#241a14", shirt="#6B7A3A", style="topi", beard="full"), dict(skin=SKIN["b"], hair="#1d1612", shirt="#B4573B"),
         dict(skin=SKIN["a"], hair="#3a2a20", shirt="#4A4F3A", glasses=True), dict(skin=SKIN["c"], hair="#1a1210", shirt="#D6A24A", style="braid")]

# --- patterns & backdrops
def pattern(c, kind, col, x0=-800, x1=1900, y0=-300, y1=1330, step=90, a=.12):
    col = alpha(hexc(col) if isinstance(col, str) else col, a)
    if kind == "stripes":
        for x in range(x0, x1, step * 2): rect(c, x, y0, step, y1 - y0, col)
    elif kind == "dots":
        for j, yy in enumerate(range(y0, y1, step)):
            for xx in range(x0, x1, step): circ(c, xx + (j % 2) * step / 2, yy, step * .13, col)
    elif kind == "tiles":
        for xx in range(x0, x1, step): line(c, xx, y0, xx, y1, 3, col)
        for yy in range(y0, y1, step): line(c, x0, yy, x1, yy, 3, col)
    elif kind == "bricks":
        for j, yy in enumerate(range(y0, y1, 50)):
            for xx in range(x0 - 100, x1, 130): rect(c, xx + (j % 2) * 65 + 3, yy + 3, 124, 44, col, 4)
    elif kind == "diag":
        for xx in range(x0 - 1400, x1, step * 2): poly(c, [(xx, y1), (xx + step, y1), (xx + step + 1400, y0), (xx + 1400, y0)], col)
def planks(c, y0=1330, col="#000", a=.12):
    for i in range(-8, 30): line(c, i * 160, y0, i * 160 - 120 + (i % 3) * 20, y0 + 800, 4, (0, 0, 0, a))
    for yy in (y0 + 90, y0 + 230, y0 + 420): line(c, -800, yy, 2900, yy, 3, (0, 0, 0, a * .8))
def interior(c, g, wall="#DCC9A0", pat="stripes", pcol="#B89A63", floor="#8B5E3C", clock=True, clock_at=(840, 330), clock_r=120,
             tmin=600, old=False, shelves=True, poster=True, phones_on=True, pa=.14):
    world(c, hexc(wall)); pattern(c, pat, pcol, a=pa)
    rect(c, -800, 1330, 3400, 900, hexc(floor)); planks(c); rect(c, -800, 1308, 3400, 24, shade(hexc(wall), .72))
    if shelves:
        for sx, sy in ((50, 560), (700, 700)):
            rect(c, sx, sy, 330, 20, hexc("#5a3b22"), 4); rect(c, sx + 20, sy + 20, 16, 30, hexc("#4a2f1b")); rect(c, sx + 290, sy + 20, 16, 30, hexc("#4a2f1b"))
            for i in range(4):
                phone(c, sx + 50 + i * 75, sy - 54, 52, 104, state=("on" if (i % 2 == 0 and phones_on) else "off"), scr=hexc(["#F0D9A6", "#E6B96B", "#D9C9A0", "#F3E3BF"][i]))
    if poster:
        rect(c, 60, 130, 270, 340, hexc("#E1B04A"), 10, hexc("#3a2418"), 6); text(c, "ফোন\nসার্ভিস", 195, 270, 66, hexc("#3a2418"), "bold"); phone(c, 195, 395, 60, 90, state="cracked")
    if clock: wall_clock(c, clock_at[0], clock_at[1], clock_r, tmin, g, old=old)
def counter(c, g, ctop="#6B4226", cfront="#8A5A36", y=1000, x0=-800, x1=1900):
    rect(c, x0, y + 34, x1 - x0, 300, hexc(cfront)); 
    for xx in range(x0, x1, 150): line(c, xx, y + 40, xx, y + 330, 4, (0, 0, 0, .13))
    rect(c, x0, y, x1 - x0, 38, hexc(ctop)); rect(c, x0, y, x1 - x0, 8, shade(hexc(ctop), 1.3))
def street(c, g, sky=("#F5B98A", "#FBE6C4"), ground="#8F8777", road="#4B443C", seed=1, sun=True, bld=("#B5654A", "#8A7A52", "#C99A5B", "#7C5B44", "#A9835A")):
    world(c, vgrad(hexc(sky[0]), hexc(sky[1]), -300, 1300))
    if sun: glow(c, 300, 500, 520, hexc("#FFE2A8"), .8); circ(c, 300, 500, 90, hexc("#FFF1CF"))
    for i in range(-3, 9):  # far buildings
        h = 300 + rnd(i, seed) * 380; x = i * 260 - 100; col = shade(hexc(bld[i % 5]), .8)
        rect(c, x, 1350 - h, 250, h + 100, col)
        for wy in range(int(1350 - h + 30), 1330, 70):
            for wx in range(x + 24, x + 220, 60): rect(c, wx, wy, 32, 38, hexc("#F4DDA0") if rnd(wx + wy, i) > .65 else shade(col, .75), 4)
    rect(c, -800, 1330, 3600, 700, hexc(ground)); rect(c, -800, 1330, 3600, 14, shade(hexc(ground), 1.25))
    for i in range(-4, 16): rect(c, i * 220, 1700, 110, 14, (1, 1, 1, .35))
    for i in range(7): line(c, -300 + i * 560, 100 - (i % 2) * 60, -300 + i * 560 + 560, 160 + (i % 2) * 60, 3, (0.15, 0.1, 0.08, .55))
def rickshaw(c, x, y, s=1.0, col="#C2432F", g=0.0):
    c.save(); c.translate(x, y); c.scale(s, s); b = math.sin(g * 9) * 3
    for wx in (-90, 120):
        circ(c, wx, 0, 62, None, hexc("#2b2118"), 10)
        for i in range(8):
            a = i * math.pi / 4 + g * 6; line(c, wx, 0, wx + 58 * math.cos(a), 58 * math.sin(a), 2.5, hexc("#2b2118"))
    poly(c, [(-130, -90 + b), (60, -90 + b), (60, -190 + b), (-130, -130 + b)], hexc(col)); poly(c, [(-130, -130 + b), (60, -190 + b), (60, -230 + b), (-150, -150 + b)], hexc("#E6B13A"))
    rect(c, -100, -70 + b, 190, 20, hexc("#2b2118"), 6); circ(c, 150, -90 + b, 20, hexc("#C99A5B")); rect(c, 130, -70 + b, 20, 50, hexc("#2b2118"), 6)
    c.restore()
def shutter(c, p, col="#7E7B72", y_off=0):
    if p <= 0: return
    ye = p * (H + 80) - 80 + y_off
    rect(c, -50, -50, W + 100, ye + 50, hexc(col))
    for yy in range(-40, int(ye), 56): line(c, -50, yy, W + 50, yy, 5, (0, 0, 0, .25)); line(c, -50, yy + 5, W + 50, yy + 5, 3, (1, 1, 1, .12))
    rect(c, -50, ye - 8, W + 100, 36, hexc("#4d4a44"), 8); rect(c, W / 2 - 60, ye + 6, 120, 20, hexc("#2a2825"), 8)
def banner(c, x, y, w, h, l1, l2, g=0, r1=1.0, r2=1.0, bg="#F4E7C5", fg="#3a2418", acc="#C2432F", sz=64):
    rect(c, x - w / 2 + 8, y - h / 2 + 12, w, h, (0, 0, 0, .22), 18); rect(c, x - w / 2, y - h / 2, w, h, hexc(bg), 18, hexc(acc), 10)
    rect(c, x - w / 2 + 22, y - h / 2 + 22, w - 44, h - 44, None, 14, hexc(fg), 3)
    for sx in (-1, 1):
        for sy in (-1, 1): circ(c, x + sx * (w / 2 - 20), y + sy * (h / 2 - 20), 7, hexc("#8a7a5a"))
    for ln, rv, yy in ((l1, r1, y - (sz * .75 if l2 else 0)), (l2, r2, y + sz * .75)):
        if not ln or rv <= 0: continue
        c.save(); c.rectangle(x - w / 2, yy - sz, w * .5 + (w * rv) - w * .5 if False else w * rv + (x - w / 2) - (x - w / 2), sz * 2); c.restore()
        c.save(); c.new_path(); c.rectangle(x - w / 2 + 10, yy - sz, (w - 20) * rv, sz * 2); c.clip(); text(c, ln, x, yy, sz, hexc(fg), "bold"); c.restore()
def calendar(c, x, y, w, h, top, big, sub="", rot=0, a=1.0):
    c.save(); c.translate(x, y); c.rotate(rot)
    rect(c, -w / 2 + 10, -h / 2 + 14, w, h, (0, 0, 0, .25 * a), 20); rect(c, -w / 2, -h / 2, w, h, hexc("#FBF6E8"), 20); rect(c, -w / 2, -h / 2, w, h * .24, hexc("#C2432F"), 20)
    rect(c, -w / 2, -h / 2 + h * .12, w, h * .12, hexc("#C2432F"))
    for i in range(-2, 3): rect(c, i * w * .2 - 8, -h / 2 - 22, 16, 48, hexc("#3a3a38"), 8)
    text(c, top, 0, -h / 2 + h * .125, h * .12, hexc("#FFF4DC"), "bold"); text(c, big, 0, h * .06, h * .42, hexc("#3a2418"), "bold")
    if sub: text(c, sub, 0, h * .36, h * .1, hexc("#7a6a52"), "bold")
    c.restore()
DUR = [45, 48, 50, 42, 47, 40, 46, 49, 44, 43]
def wrench(c, x, y, s=1.0, rot=0.6, col="#6E685C"):
    c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s)
    line(c, 0, 20, 0, 230, 40, hexc(col)); arc_stroke(c, 0, -30, 48, math.radians(-60), math.radians(240), 34, hexc(col)); c.restore()
def bulb(c, x, y, r, g):
    glow(c, x, y, r * 3, hexc("#FFE08A"), .6); circ(c, x, y, r, hexc("#FFE27A"), hexc("#B8860B"), 5); rect(c, x - r * .5, y + r * .85, r, r * .6, hexc("#8a8a84"), 5)
    for i in range(8):
        a = i * math.pi / 4 + g; line(c, x + r * 1.4 * math.cos(a), y + r * 1.4 * math.sin(a), x + r * 1.9 * math.cos(a), y + r * 1.9 * math.sin(a), 6, hexc("#E0A526"))
def qmarks(c, g, x, y, n=3, size=90, col="#C2432F", spread=110):
    for i in range(n):
        p = (g * .8 + i / n) % 1; text(c, "?", x + (i - (n - 1) / 2) * spread + math.sin(g * 3 + i) * 12, y - p * 130, size * (.6 + .6 * math.sin(p * math.pi)), hexc(col), "bold", a=math.sin(p * math.pi), rot=(i - 1) * .25)
def caption_flash(c, a):
    if a > 0: rect(c, -50, -50, W + 100, H + 100, (1, 1, 1, a))

def checkmark(c, x, y, s, col, w=12):
    c.new_path(); c.move_to(x - s * .5, y); c.line_to(x - s * .12, y + s * .4); c.line_to(x + s * .55, y - s * .45); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_width(w); setc(c, col); c.stroke()
def heart(c, x, y, s, col):
    c.save(); c.translate(x, y); c.scale(s, s); c.new_path(); c.move_to(0, 30); c.curve_to(-70, -20, -40, -70, 0, -30); c.curve_to(40, -70, 70, -20, 0, 30); c.close_path(); setc(c, col); c.fill(); c.restore()
def shopfront(c, g, x=480, y=820):
    rect(c, x, y, 560, 560, hexc("#A9835A")); rect(c, x + 40, y + 220, 480, 290, hexc("#3a2e24")); rect(c, x + 60, y + 240, 440, 240, hexc("#F1CE8A"), 6)
    phone(c, x + 160, y + 350, 70, 130, state="on"); phone(c, x + 280, y + 350, 70, 130, state="on"); phone(c, x + 400, y + 350, 70, 130, state="on")
    rect(c, x - 10, y + 60, 580, 130, hexc("#2F5D3A"), 12, hexc("#F4E7C5"), 6); text(c, "জাহিদ মোবাইল সার্ভিসিং", x + 280, y + 125, 46, hexc("#FFF4DC"), "bold")
    poly(c, [(x - 10, y + 220), (x + 570, y + 220), (x + 530, y + 180), (x + 30, y + 180)], hexc("#C2432F"))
