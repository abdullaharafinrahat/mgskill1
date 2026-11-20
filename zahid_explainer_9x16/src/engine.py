import numpy as np, json, math, os, re
from collections import OrderedDict
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter
W, H, FPS = 720, 1280, 30
CX, CY = 360, 470            # camera focal point on screen
WELL_Y = 930                 # content never enters below this line (caption safe zone)
INK = (27, 24, 48); INKW = 3
BN_B = '/usr/share/fonts/truetype/noto/NotoSansBengali-Bold.ttf'
LAT_B = '/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf'
_fc = {}
def font(path, size):
    k = (path, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)
    return _fc[k]
def isLat(w): return bool(re.search(r'[A-Za-z]', w))
# ---------- easing ----------
def cl(x, a=0., b=1.): return a if x < a else b if x > b else x
def ramp(t, a, b): return cl((t - a) / max(b - a, 1e-6))
def eio(x): x = cl(x); return x * x * (3 - 2 * x)
def eo(x): x = cl(x); return 1 - (1 - x) ** 3
def eob(x):
    x = cl(x); c1 = 1.9; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def lerp(a, b, x): return a + (b - a) * x
def kf(t, keys, ease=eio):
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1: return lerp(v0, v1, ease((t - t0) / max(t1 - t0, 1e-6)))
    return keys[-1][1]
# ---------- drawing pen (1x coords, 2x pixels) ----------
class Pen:
    def __init__(s, w, h):
        s.w, s.h = w, h
        s.im = Image.new('RGBA', (int(w * 2), int(h * 2)), (0, 0, 0, 0)); s.d = ImageDraw.Draw(s.im)
    def _p(s, pts): return [(x * 2, y * 2) for x, y in pts]
    def ell(s, box, fill, w=INKW, ink=INK):
        x0, y0, x1, y1 = box
        if w: s.d.ellipse([(x0 - w) * 2, (y0 - w) * 2, (x1 + w) * 2, (y1 + w) * 2], fill=ink)
        if fill: s.d.ellipse([x0 * 2, y0 * 2, x1 * 2, y1 * 2], fill=fill)
    def rr(s, box, fill, r=8, w=INKW, ink=INK):
        x0, y0, x1, y1 = box
        if w: s.d.rounded_rectangle([(x0 - w) * 2, (y0 - w) * 2, (x1 + w) * 2, (y1 + w) * 2], r * 2 + w * 2, fill=ink)
        if fill: s.d.rounded_rectangle([x0 * 2, y0 * 2, x1 * 2, y1 * 2], r * 2, fill=fill)
    def poly(s, pts, fill, w=INKW, ink=INK):
        p = s._p(pts)
        if w: s.d.line(p + [p[0]], fill=ink, width=int(4 * w), joint='curve'); s.cap(pts, 2 * w, ink, w=0, inner=False)
        s.d.polygon(p, fill=fill)
    def cap(s, pts, width, color, w=0, inner=True):
        p = s._p(pts)
        s.d.line(p, fill=color, width=int(width * 2), joint='curve')
        r = width
        for x, y in p: s.d.ellipse([x - r, y - r, x + r, y + r], fill=color)
    def line(s, pts, width, color, w=INKW, ink=INK):
        if w: s.cap(pts, width + 2 * w, ink)
        s.cap(pts, width, color)
    def chord(s, box, a0, a1, fill, w=INKW, ink=INK):
        x0, y0, x1, y1 = box
        if w: s.d.chord([(x0 - w) * 2, (y0 - w) * 2, (x1 + w) * 2, (y1 + w) * 2], a0, a1, fill=ink)
        s.d.chord([x0 * 2, y0 * 2, x1 * 2, y1 * 2], a0, a1, fill=fill)
    def done(s): return s.im
# ---------- text ----------
def runs(w): return re.findall(r"[A-Za-z0-9\-\.']+|[^A-Za-z0-9\-\.']+", w) or [w]
def wlen(w, px, ff=None):
    return sum(font(ff or (LAT_B if isLat(r) else BN_B), px).getlength(r) for r in runs(w)) if w else 0
def wdraw(d, x, y, w, px, fill, stroke, sfill, ff=None):
    for r in runs(w):
        f = font(ff or (LAT_B if isLat(r) else BN_B), px); d.text((x, y), r, font=f, fill=fill, stroke_width=stroke, stroke_fill=sfill); x += f.getlength(r)
def text_img(text, size, fill=(255, 255, 255), stroke=0, sfill=INK, align='center', lead=1.25, forcefont=None):
    lines = text.split('\n'); S = 2
    rows = []
    for ln in lines:
        ws = ln.split(' ') if ln else ['']
        parts = []
        for w in ws:
            parts.append((w, None, wlen(w, size * S, forcefont)))
        sp = font(BN_B, size * S).getlength(' ')
        tw = sum(p[2] for p in parts) + sp * (len(parts) - 1)
        rows.append((parts, sp, tw))
    maxw = max(r[2] for r in rows); pad = stroke * S + 8
    lh = int(size * S * lead)
    im = Image.new('RGBA', (int(maxw + 2 * pad), lh * len(rows) + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for ri, (parts, sp, tw) in enumerate(rows):
        x = pad + (maxw - tw) / 2 if align == 'center' else pad
        y = pad + ri * lh
        for w, f, wl in parts:
            if w: wdraw(d, x, y, w, size * S, fill, stroke * S, sfill, forcefont)
            x += wl + sp
    return im
# ---------- sprite cache with mipmaps ----------
class Sprite:
    def __init__(s, im):
        s.w1, s.h1 = im.width / 2, im.height / 2
        s.lv = [im]
        while s.lv[-1].width > 24 and s.lv[-1].height > 24 and len(s.lv) < 5:
            a = s.lv[-1]; s.lv.append(a.resize((max(1, a.width // 2), max(1, a.height // 2)), Image.BOX))
        s.bytes = sum(l.width * l.height * 4 for l in s.lv)
    def get(s, w, h):
        w = max(1, int(round(w))); h = max(1, int(round(h)))
        lv = s.lv[0]
        for l in s.lv:
            if l.width >= w * 0.99: lv = l
            else: break
        if lv.size == (w, h): return lv
        return lv.resize((w, h), Image.BILINEAR)
B = {}                   # builders: name -> fn(*args) -> 2x RGBA
_SC = OrderedDict(); _bytes = [0]; CAP = 260e6
def get_sprite(key):
    sp = _SC.get(key)
    if sp is not None: _SC.move_to_end(key); return sp
    sp = Sprite(B[key[0]](*key[1:])); _SC[key] = sp; _bytes[0] += sp.bytes
    while _bytes[0] > CAP and len(_SC) > 1:
        _, o = _SC.popitem(last=False); _bytes[0] -= o.bytes
    return sp
# ---------- basic builders ----------
def b_rr(w, h, fill, r=12, ink=1):
    p = Pen(w + 8, h + 8); p.rr((4, 4, 4 + w, 4 + h), fill, r, INKW if ink else 0); return p.done()
def b_circ(r, fill, ink=1):
    p = Pen(2 * r + 8, 2 * r + 8); p.ell((4, 4, 4 + 2 * r, 4 + 2 * r), fill, INKW if ink else 0); return p.done()
def b_text(text, size, fill=(255, 255, 255), stroke=0, sfill=INK, align='center'): return text_img(text, size, fill, stroke, sfill, align)
def b_grad(c1, c2, w=900, h=1500):
    a = np.linspace(0, 1, h)[:, None, None]
    arr = (np.array(c1)[None, None, :] * (1 - a) + np.array(c2)[None, None, :] * a) * np.ones((1, w, 1))
    im = Image.fromarray(arr.astype(np.uint8), 'RGB').convert('RGBA')
    return im.resize((w * 2, h * 2), Image.BILINEAR) if False else im.resize((w * 2, h * 2))
def b_bubble(text, size=34, tail='bl', fill=(255, 255, 255), tc=INK, dashed=0):
    t = text_img(text, size, tc, 0); tw, th = t.width / 2, t.height / 2
    w, h = tw + 40, th + 24; pad = 32
    p = Pen(w + 2 * pad, h + 2 * pad); x0, y0 = pad, pad
    tx = {'bl': x0 + 44, 'br': x0 + w - 44, 'bc': x0 + w / 2, 'tl': x0 + 44, 'tr': x0 + w - 44}[tail]
    dxs = -10 if tail[1] == 'l' else 10 if tail[1] == 'r' else 0
    if tail[0] == 'b': tri = [(tx - 14, y0 + h - 6), (tx + 14, y0 + h - 6), (tx + dxs, y0 + h + 26)]; yy = y0 + h
    else: tri = [(tx - 14, y0 + 6), (tx + 14, y0 + 6), (tx + dxs, y0 - 26)]; yy = y0
    p.poly(tri, fill)
    p.rr((x0, y0, x0 + w, y0 + h), fill, 24)
    p.d.rectangle([(tx - 11) * 2, (yy - 3.5) * 2, (tx + 11) * 2, (yy + 3.5) * 2], fill=fill)
    im = p.done()
    im.alpha_composite(t, (int((x0 + w / 2) * 2 - t.width / 2), int((y0 + h / 2) * 2 - t.height / 2)))
    return im
# ---------- phone ----------
def b_phone(state='ok', w=84, ang=0):
    h = int(w * 2.0); p = Pen(w + 20, h + 20); o = 10
    p.rr((o, o, o + w, o + h), (44, 48, 70), 14)
    sc = {'ok': (120, 200, 255), 'dark': (40, 44, 60), 'notes': (255, 252, 235), 'cracked': (120, 200, 255), 'sad': (255, 200, 120), 'rare': (200, 140, 255)}.get(state, (120, 200, 255))
    p.rr((o + 6, o + 12, o + w - 6, o + h - 12), sc, 8, 2)
    if state == 'notes':
        for i in range(9): p.d.line([ (o + 14) * 2, (o + 26 + i * 15) * 2, (o + w - 14 - (i % 3) * 10) * 2, (o + 26 + i * 15) * 2], fill=(90, 90, 120), width=4)
    if state == 'cracked':
        pts = [(o + w * .65, o + 12), (o + w * .55, o + h * .25), (o + w * .35, o + h * .4), (o + w * .5, o + h * .55), (o + w * .2, o + h * .8)]
        p.cap(pts, 2.2, (255, 255, 255), 0); p.cap([(o + w * .55, o + h * .25), (o + w * .85, o + h * .3)], 1.6, (255, 255, 255), 0)
        p.cap([(o + w * .5, o + h * .55), (o + w * .8, o + h * .62), (o + w * .9, o + h * .8)], 1.6, (255, 255, 255), 0)
    if state == 'rare':
        p.ell((o + w * .3, o + h * .35, o + w * .7, o + h * .35 + w * .4), (255, 220, 90), 2)
    p.d.ellipse([(o + w / 2 - 4) * 2, (o + 4) * 2, (o + w / 2 + 4) * 2, (o + 8) * 2], fill=(20, 20, 30))
    im = p.done()
    return im.rotate(ang, resample=Image.BICUBIC, expand=True) if ang else im
# ---------- clock ----------
def b_clock(am=0, ah=0, r=64, style='wall', sec=-1):
    p = Pen(2 * r + 24, 2 * r + 24); c = r + 12
    if style == 'wall':
        p.ell((c - r, c - r, c + r, c + r), (92, 64, 52), 4); p.ell((c - r + 9, c - r + 9, c + r - 9, c + r - 9), (252, 246, 228), 3)
    elif style == 'neon':
        p.ell((c - r, c - r, c + r, c + r), (30, 40, 80), 4); p.ell((c - r + 9, c - r + 9, c + r - 9, c + r - 9), (240, 252, 255), 3)
    else:
        p.ell((c - r, c - r, c + r, c + r), (252, 246, 228), 4)
    for i in range(12):
        a = math.radians(i * 30); L = 9 if i % 3 == 0 else 5
        p.cap([(c + math.sin(a) * (r - 14), c - math.cos(a) * (r - 14)), (c + math.sin(a) * (r - 14 - L), c - math.cos(a) * (r - 14 - L))], 2, INK)
    def hand(a, L, wd, col):
        a = math.radians(a); p.line([(c, c), (c + math.sin(a) * L, c - math.cos(a) * L)], wd, col, 2)
    hand(ah, r * .5, 4.5, INK); hand(am, r * .75, 3.5, INK)
    if sec >= 0: p.cap([(c - math.sin(math.radians(sec)) * 10, c + math.cos(math.radians(sec)) * 10), (c + math.sin(math.radians(sec)) * (r - 16), c - math.cos(math.radians(sec)) * (r - 16))], 1.6, (230, 60, 60))
    p.ell((c - 5, c - 5, c + 5, c + 5), (230, 60, 60), 2)
    return p.done()
# ---------- characters ----------
CH = {
 'zahid': dict(skin=(226, 165, 120), hair=(30, 26, 38), hs='short', shirt=(58, 110, 165), pants=(60, 64, 88), mus=1, body='shirt', acc='lanyard'),
 'girl': dict(skin=(214, 150, 104), hair=(40, 26, 26), hs='braids', shirt=(250, 250, 250), pants=(34, 54, 120), body='uniform', acc='bag'),
 'cust': dict(skin=(204, 146, 102), hair=(235, 235, 235), hs='cap', shirt=(160, 56, 66), pants=(235, 235, 235), mus=1, body='panjabi'),
 'cust2': dict(skin=(232, 176, 132), hair=(150, 150, 165), hs='short', shirt=(70, 140, 100), pants=(60, 60, 74), glasses=1, body='shirt'),
 'bro': dict(skin=(226, 165, 120), hair=(30, 26, 38), hs='short', shirt=(240, 150, 50), pants=(70, 80, 110), body='shirt'),
 'cust3': dict(skin=(190, 135, 98), hair=(30, 26, 38), hs='short', shirt=(130, 90, 170), pants=(50, 50, 60), body='shirt'),
 'cust4': dict(skin=(232, 176, 132), hair=(90, 60, 40), hs='braids', shirt=(230, 110, 130), pants=(60, 60, 90), body='shirt'),
}
EXPR = {  # brow slope L,R (px, + = inner end up), brow y, eye open(0..1.3), mouth, extra
 'neutral': (0, 0, 0, 1, 'flat', ''), 'worry': (7, 7, -3, 1, 'wavy', 'sweat'), 'think': (-4, 6, -2, .8, 'side', ''),
 'shock': (-3, -3, -9, 1.4, 'o', ''), 'happy': (-3, -3, -2, 1, 'smile', 'blush'), 'smug': (3, -2, 0, .55, 'smirk', ''),
 'sad': (8, 8, 0, .9, 'frown', ''), 'grin': (-4, -4, -3, 1, 'big', 'blush'), 'angry': (-8, -8, 0, .9, 'frown', ''),
}
def b_char(name, expr='neutral', blink=0, mouth=0, pose='down', br=0, look=0, walk=-1, sil=None, hold=0):
    c = CH[name]; p = Pen(300, 440); ox = 20; skin = c['skin']; INKc = INK
    bb = -br * 0.9
    sh = c['shirt']; cx = ox + 130
    if c.get('acc') == 'bag':
        p.rr((cx - 62, 160 + bb, cx + 62, 290), (240, 120, 60), 16)
    # legs
    hip = 300
    def leg(x, ph):
        sw = math.sin(ph) * 26 if walk >= 0 else 0; lift = max(0, math.cos(ph)) * 8 if walk >= 0 else 0
        fx = x + sw; fy = 398 - lift
        col = c['pants']
        if c['body'] == 'uniform': col = skin
        p.line([(x, hip), (fx, fy)], 26, col, INKW)
        shoe = (40, 40, 50) if c['body'] != 'panjabi' else (150, 100, 60)
        p.ell((fx - 17, fy - 4, fx + 21, fy + 14), shoe, INKW)
    leg(cx - 22, walk * 0.8 if walk >= 0 else 0); leg(cx + 22, walk * 0.8 + math.pi if walk >= 0 else 0)
    # torso
    tb = 300 if c['body'] != 'panjabi' else 362
    p.rr((cx - 56, 150 + bb, cx + 56, tb), sh, 30)
    if c['body'] == 'uniform':
        p.poly([(cx - 56, 232), (cx + 56, 232), (cx + 74, 332), (cx - 74, 332)], c['pants'])
        p.poly([(cx - 14, 152 + bb), (cx, 190 + bb), (cx + 14, 152 + bb)], (200, 40, 50), 2)
    elif c['body'] == 'panjabi':
        p.d.line([(cx * 2, 190 * 2), (cx * 2, 290 * 2)], fill=INK, width=5)
        for i in range(3): p.ell((cx + 6, 196 + i * 24, cx + 12, 202 + i * 24), (255, 255, 255), 1)
    else:
        p.poly([(cx - 16, 152 + bb), (cx, 184 + bb), (cx + 16, 152 + bb)], (245, 245, 250), 2)
        if c.get('acc') == 'lanyard':
            p.line([(cx - 20, 152 + bb), (cx - 4, 240 + bb)], 5, (255, 190, 40), 2); p.rr((cx - 14, 236 + bb, cx + 8, 262 + bb), (255, 255, 255), 4, 2)
        for i in range(3): p.d.line([(cx * 2 + 30, (210 + i * 30) * 2), (cx * 2 + 70, (210 + i * 30) * 2)], fill=tuple(int(v * .8) for v in sh), width=4)
    # arms
    P = {'down': ((-70, 270), (70, 270)), 'talk': ((-70, 270), (92, 200)), 'hold': ((-30, 240), (30, 240)), 'point': ((-70, 270), (150, 168)),
         'shrug': ((-96, 210), (96, 210)), 'hips': ((-84, 255), (84, 255)), 'up': ((-70, 270), (84, 100)), 'work': ((-40, 262), (44, 262)),
         'both': ((-90, 130), (90, 130)), 'give': ((-70, 270), (96, 230)), 'wave': ((-70, 270), (96, 110))}[pose]
    for side, (hx, hy) in zip((-1, 1), P):
        sx_, sy_ = cx + side * 52, 172 + bb; ex, ey = cx + hx, hy
        d = math.hypot(ex - sx_, ey - sy_); L = 62
        if d >= 2 * L - 1: ex = sx_ + (ex - sx_) * (2 * L - 2) / d; ey = sy_ + (ey - sy_) * (2 * L - 2) / d; d = math.hypot(ex - sx_, ey - sy_)
        mx, my = (sx_ + ex) / 2, (sy_ + ey) / 2; hh = math.sqrt(max(L * L - d * d / 4, 0))
        nx, ny = -(ey - sy_) / d, (ex - sx_) / d
        if ny < 0: nx, ny = -nx, -ny   # elbow bends downward
        if side * nx < 0 and abs(nx) > .2: pass
        elx, ely = mx + nx * hh, my + ny * hh
        col = sh if c['body'] != 'uniform' else (250, 250, 250)
        p.line([(sx_, sy_), (elx, ely), (ex, ey)], 24, col, INKW)
        p.ell((ex - 12, ey - 12, ex + 12, ey + 12), skin, INKW)
        if hold and side == 1: pass
    # neck + head
    hb = -br * 1.0
    p.rr((cx - 14, 132 + hb, cx + 14, 164 + bb), skin, 6)
    hc = (cx, 92 + hb)
    if c['hs'] == 'braids':
        for s_ in (-1, 1):
            p.ell((cx + s_ * 52 - 11, 100 + hb, cx + s_ * 52 + 11, 176 + hb), c['hair'], INKW)
            p.ell((cx + s_ * 52 - 9, 164 + hb, cx + s_ * 52 + 9, 178 + hb), (210, 50, 70), 2)
    p.ell((cx - 58, 90 + hb, cx - 44, 116 + hb), skin, INKW); p.ell((cx + 44, 90 + hb, cx + 58, 116 + hb), skin, INKW)
    p.ell((cx - 52, 36 + hb, cx + 52, 150 + hb), skin, INKW)
    if c['hs'] in ('short', 'braids'):
        p.chord((cx - 56, 28 + hb, cx + 56, 130 + hb), 192, 348, c['hair'])
        p.poly([(cx - 52, 84 + hb), (cx - 44, 62 + hb), (cx - 20, 56 + hb), (cx - 38, 80 + hb)], c['hair'], 0)
    elif c['hs'] == 'cap':
        p.rr((cx - 44, 24 + hb, cx + 44, 64 + hb), (250, 250, 250), 18); p.d.line([((cx - 44) * 2, 54 * 2 + hb * 2), ((cx + 44) * 2, 54 * 2 + hb * 2)], fill=INK, width=4)
        for i in range(5): p.ell((cx - 30 + i * 15, 36 + hb, cx - 25 + i * 15, 41 + hb), (150, 190, 230), 0)
    # face
    ex_ = EXPR[expr]; bl, brr, by, eo_, mt, extra = ex_
    ey = 94 + hb
    for s_, sl in ((-1, bl), (1, brr)):
        x = cx + s_ * 21
        if blink or eo_ < .3:
            p.cap([(x - 10, ey + 2), (x, ey + 6), (x + 10, ey + 2)] if expr != 'happy' and expr != 'grin' else [(x - 10, ey + 5), (x, ey - 4), (x + 10, ey + 5)], 2.4, INK, 0)
        elif expr in ('happy', 'grin'):
            p.cap([(x - 10, ey + 5), (x, ey - 5), (x + 10, ey + 5)], 2.6, INK, 0)
        else:
            ry = 12 * eo_
            p.ell((x - 10, ey - ry, x + 10, ey + ry), (255, 255, 255), 2)
            pr = 5.5 if eo_ < 1.3 else 3.5
            lx = 0 if look == 2 else look * 4; ly = -5 if (look == 2 or expr == 'think') else 0
            p.ell((x + lx - pr, ey - pr + ly, x + lx + pr, ey + pr + ly), INK, 0)
            if eo_ < .7: p.d.rectangle([(x - 12) * 2, (ey - ry - 3) * 2, (x + 12) * 2, (ey - ry + ry * 0.9) * 2], fill=skin); p.cap([(x - 11, ey - ry * .1), (x + 11, ey - ry * .1)], 2.2, INK, 0)
        # brow
        if s_ == -1: ya, yb = by - 8 - sl * .5 + 0, by - 8 + sl * .5
        yL = 74 + hb + by
        inner = (x + s_ * -9, yL - sl * (0.6)); outer = (x + s_ * 11, yL + sl * (0.6))
        if expr == 'think' and s_ == 1: inner = (inner[0], inner[1] - 6); outer = (outer[0], outer[1] - 6)
        p.cap([inner, outer], 3.6, c['hair'] if c['hair'][0] < 120 else (90, 90, 100), 0)
    p.cap([(cx - 4, 110 + hb), (cx + 2, 112 + hb), (cx + 5, 108 + hb)], 1.8, tuple(int(v * .7) for v in skin), 0)
    my = 130 + hb
    if c.get('mus'): p.ell((cx - 20, my - 12, cx + 20, my - 3), c['hair'] if c['hair'][0] < 120 else (130, 130, 140), 1.5)
    m = mt
    if mouth and m in ('flat', 'smile', 'smirk', 'side'): m = 'open'
    if m == 'flat': p.cap([(cx - 9, my + 3), (cx + 9, my + 3)], 2.8, INK, 0)
    elif m == 'smile': p.cap([(cx - 14, my), (cx - 6, my + 8), (cx + 6, my + 8), (cx + 14, my)], 2.8, INK, 0)
    elif m == 'big': p.poly([(cx - 17, my - 1), (cx + 17, my - 1), (cx + 12, my + 14), (cx - 12, my + 14)], (255, 255, 255), 2); p.cap([(cx - 17, my - 1), (cx + 17, my - 1)], 2, INK, 0)
    elif m == 'smirk': p.cap([(cx - 10, my + 6), (cx + 2, my + 6), (cx + 12, my), (cx + 16, my - 4)], 2.8, INK, 0)
    elif m == 'frown': p.cap([(cx - 12, my + 9), (cx - 5, my + 3), (cx + 5, my + 3), (cx + 12, my + 9)], 2.8, INK, 0)
    elif m == 'wavy': p.cap([(cx - 12, my + 5), (cx - 6, my + 1), (cx, my + 6), (cx + 6, my + 1), (cx + 12, my + 5)], 2.4, INK, 0)
    elif m == 'side': p.cap([(cx - 6, my + 4), (cx + 10, my + 1)], 2.8, INK, 0)
    elif m == 'o': p.ell((cx - 8, my - 2, cx + 8, my + 16), (90, 30, 40), 2)
    elif m == 'open':
        hgt = 5 if mouth == 1 else 13
        p.ell((cx - 10, my, cx + 10, my + hgt + 3), (90, 30, 40), 2)
    if extra == 'sweat': p.poly([(cx + 50, 52 + hb), (cx + 58, 70 + hb), (cx + 42, 70 + hb)], (150, 215, 255), 2); p.ell((cx + 42, 64 + hb, cx + 58, 78 + hb), (150, 215, 255), 2)
    if extra == 'blush':
        for s_ in (-1, 1): p.ell((cx + s_ * 34 - 8, 108 + hb, cx + s_ * 34 + 8, 116 + hb), (245, 130, 130), 0)
    if c.get('glasses'):
        for s_ in (-1, 1): p.d.ellipse([(cx + s_ * 21 - 15) * 2, (ey - 14) * 2, (cx + s_ * 21 + 15) * 2, (ey + 14) * 2], outline=INK, width=5)
        p.cap([(cx - 6, ey), (cx + 6, ey)], 2, INK, 0)
    im = p.done()
    if sil is not None:
        a = im.getchannel('A'); im = Image.new('RGBA', im.size, sil + (255,)); im.putalpha(a)
    return im
def char_head_y(): return 92
B.update(rr=b_rr, circ=b_circ, text=b_text, grad=b_grad, bubble=b_bubble, phone=b_phone, clock=b_clock, char=b_char)
# ---------- items / scene ----------
def comb(*fs):
    def f(t):
        r = dict(dx=0, dy=0, rot=0, s=1, sx=1, sy=1, a=1)
        for g in fs:
            d = g(t)
            if not d: continue
            for k, v in d.items():
                if k in ('dx', 'dy', 'rot'): r[k] += v
                else: r[k] *= v
        return r
    return f
def enter(t0, kind='pop', d=.4, dist=80):
    def f(t):
        x = (t - t0) / d
        if x <= 0: return dict(a=0, s=.001 if kind == 'pop' else 1)
        if x >= 1: return {}
        if kind == 'pop': return dict(s=max(eob(x), .001), a=cl(x * 4))
        if kind == 'fade': return dict(a=eio(x))
        e = 1 - eo(x)
        return dict(a=cl(x * 3), dx={'left': -dist, 'right': dist}.get(kind, 0) * e, dy={'up': dist, 'down': -dist}.get(kind, 0) * e)
    return f
def leave(t1, d=.3, kind='fade', dist=120):
    def f(t):
        x = (t - t1) / d
        if x <= 0: return {}
        x = min(x, 1); 
        if x >= 1: return dict(a=0)
        return dict(a=1 - x, dx={'left': -dist, 'right': dist}.get(kind, 0) * x, dy={'up': -dist, 'down': dist}.get(kind, 0) * x)
    return f
def bob(amp=4, per=2., ph=0): return lambda t: dict(dy=math.sin(t / per * 6.283 + ph) * amp)
def sway(amp=3, per=3., ph=0): return lambda t: dict(rot=math.sin(t / per * 6.283 + ph) * amp)
def breathe(amp=.012, per=3.2, ph=0): return lambda t: dict(sy=1 + math.sin(t / per * 6.283 + ph) * amp, sx=1 - math.sin(t / per * 6.283 + ph) * amp * .4)
def move(t0, t1, x0, y0, x1, y1, ease=eio):
    return lambda t: dict(dx=lerp(x0, x1, ease(ramp(t, t0, t1))), dy=lerp(y0, y1, ease(ramp(t, t0, t1))))
class Item:
    def __init__(s, spr, x, y, z, sc, rot, a, anchor, t0, t1, anim, fixed, flip):
        s.spr, s.x, s.y, s.z, s.s, s.rot, s.a, s.anchor, s.t0, s.t1, s.anim, s.fixed, s.flip = spr, x, y, z, sc, rot, a, anchor, t0, t1, anim, fixed, flip
class Scene:
    def __init__(s, meta, idx):
        s.meta = meta; s.idx = idx; s.items = []; s.camk = [(0, CX, CY, 1.0, 0)]; s.bgc = ((250, 240, 220), (240, 220, 190))
        s.shakes = []; s.flashes = []; s.hits = []; s.dur = meta['end'] - meta['start']; s.errs = []; s.whoosh_extra = []
        s.words = [dict(w=w['w'], s=w['s'] - meta['start'], e=w['e'] - meta['start']) for w in meta['words']]
        s.talk = {}
    def cue(s, sub, n=0, end=False):
        m = [w for w in s.words if sub in w['w']]
        if len(m) <= n: s.errs.append(sub); return 0.0
        return m[n]['e' if end else 's']
    def bg(s, c1, c2, z=.2, extra=None):
        s.bgc = (c1, c2); s.add(('grad', c1, c2), 360, 640, z=z, fixed=False)
    def add(s, spr, x, y, z=1., s_=1., rot=0, a=1., anchor=(.5, .5), t0=-99, t1=1e9, anim=None, fixed=False, flip=False, **kw):
        it = Item(spr, x, y, z, kw.get('sc', s_), rot, a, anchor, t0, t1, anim, fixed, flip); s.items.append(it); return it
    def cam(s, *keys): s.camk = list(keys)
    def shake(s, t, d=.45, amp=14): s.shakes.append((t, d, amp))
    def flash(s, t, d=.35, col=(255, 255, 255), a=.8): s.flashes.append((t, d, col, a))
    def hit(s, t, kind='hit'): s.hits.append((t, kind))
    def cam_at(s, t):
        k = s.camk
        if t <= k[0][0]: return k[0][1:5]
        for a, b in zip(k, k[1:]):
            if t <= b[0]:
                e = b[5] if len(b) > 5 else eio
                x = e((t - a[0]) / max(b[0] - a[0], 1e-6))
                return tuple(lerp(a[i], b[i], x) for i in range(1, 5))
        return k[-1][1:5]
    def render(s, t):
        cxp, cyp, zoom, roll = s.cam_at(t)
        ox = oy = 0
        for (t0, d, amp) in s.shakes:
            if t0 <= t <= t0 + d:
                f = (1 - (t - t0) / d) ** 2 * amp; ox += math.sin(t * 91) * f; oy += math.cos(t * 77 + 1) * f
        cxp -= ox; cyp -= oy
        fr = Image.new('RGB', (W, H), s.bgc[1])
        for it in s.items:
            if t < it.t0 or t > it.t1: continue
            st = it.anim(t) if it.anim else {}
            a = it.a * st.get('a', 1)
            if a <= 0.01: continue
            key = it.spr(t) if callable(it.spr) else it.spr
            sp = get_sprite(key)
            px = it.x + st.get('dx', 0); py = it.y + st.get('dy', 0)
            if it.fixed:
                sx_, sy_, zs = px, py, 1.0
            else:
                zs = zoom ** it.z
                sx_ = CX + ((px - CX) + (CX - cxp) * it.z) * zs; sy_ = CY + ((py - CY) + (CY - cyp) * it.z) * zs
            sc = it.s * st.get('s', 1) * zs
            w = sp.w1 * sc * st.get('sx', 1); h = sp.h1 * sc * st.get('sy', 1)
            rot = it.rot + st.get('rot', 0)
            if w < 1 or h < 1: continue
            if max(w, h) * (1.5 if rot else 1) + abs(sx_) < -50: continue
            ax, ay = it.anchor
            if (not rot) and (sx_ - ax * w > W or sx_ + (1 - ax) * w < 0 or sy_ - ay * h > H or sy_ + (1 - ay) * h < 0): continue
            if w > 4000 or h > 4000: continue
            im = sp.get(w, h)
            if it.flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
            if a < .99: im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v, a=a: int(v * a)))
            if rot:
                im = im.rotate(-rot, resample=Image.BILINEAR, expand=True)
                r = math.radians(rot); vx, vy = (ax - .5) * w, (ay - .5) * h
                rx = vx * math.cos(r) - vy * math.sin(r); ry = vx * math.sin(r) + vy * math.cos(r)
                cxs, cys = sx_ - rx, sy_ - ry
                fr.paste(im, (int(cxs - im.width / 2), int(cys - im.height / 2)), im)
            else:
                fr.paste(im, (int(round(sx_ - ax * w)), int(round(sy_ - ay * h))), im)
        if abs(roll) > .05:
            fr = fr.rotate(roll, resample=Image.BILINEAR, center=(CX, CY), fillcolor=s.bgc[1])
        for (t0, d, col, al) in s.flashes:
            if t0 <= t <= t0 + d:
                f = al * (1 - (t - t0) / d) ** 1.5
                fr = Image.blend(fr, Image.new('RGB', (W, H), col), f)
        return fr
# ---------- captions ----------
class Captions:
    def __init__(s, scenes_meta):
        s.chunks = []; s.cache = {}
        f = font(BN_B, 2 * 54)
        for m in scenes_meta:
            ws = m['words']; cur = []
            def flush():
                if cur: s.chunks.append(list(cur)); cur.clear()
            for i, w in enumerate(ws):
                if cur and (w['clause'] != cur[-1]['clause'] or len(cur) >= 5 or sum(wlen(x['w'] + ' ', 108) for x in cur + [w]) / 2 > 600): flush()
                cur.append(w)
            flush()
        s.starts = [c[0]['s'] for c in s.chunks]
    def render(s, t):
        i = max(0, np.searchsorted(s.starts, t + .06, side='right') - 1)
        ch = s.chunks[i]
        if t < ch[0]['s'] - .06: return None
        endt = ch[-1]['e'] + .35
        if i + 1 < len(s.chunks) and t >= s.starts[i + 1] - .06: return None
        if t > endt: return None
        act = max([k for k, w in enumerate(ch) if w['s'] <= t] or [0])
        pop = int(cl((t - ch[act]['s']) / .14) * 3)
        key = (i, act, pop)
        if key not in s.cache:
            S = 2; size = 54
            parts = [(w['w'], None, wlen(w['w'], size * S)) for w in ch]
            sp = font(BN_B, size * S).getlength(' ')
            tw = sum(p[2] for p in parts) + sp * (len(parts) - 1)
            im = Image.new('RGBA', (int(tw + 80), int(size * S * 1.9)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            x = 40
            for k, (w, f, wl) in enumerate(parts):
                col = (255, 214, 58) if k == act else (255, 255, 255)
                if k == act:
                    bigpx = int(size * S * (1.1 if pop < 3 else 1.06)); off = (wlen(w, bigpx) - wl) / 2
                    wdraw(d, x - off, 30 - (3 if pop < 3 else 0), w, bigpx, col, 8 * S // 2 + 4, INK)
                else:
                    wdraw(d, x, 30, w, size * S, col, 8 * S // 2 + 4, INK)
                x += wl + sp
            if im.width > (W - 80) * 2: im = im.resize((W - 80) * 2 // 1, int(im.height * (W - 80) * 2 / im.width))
            s.cache[key] = im.resize((im.width // 2, im.height // 2), Image.LANCZOS)
            if len(s.cache) > 600: s.cache.pop(next(iter(s.cache)))
        im = s.cache[key]
        a = cl((t - (ch[0]['s'] - .06)) / .1)
        return im, a
def darken(c, k): return tuple(int(v * k) for v in c)
_well = {}
def apply_well(fr, col):
    if col not in _well:
        a = np.zeros((H, 1, 1), np.float32)
        ys = np.arange(H)
        a[:, 0, 0] = np.clip((ys - (WELL_Y - 50)) / 60.0, 0, 1) ** 1.5
        _well[col] = (a, np.array(col, np.float32)[None, None, :])
    a, c = _well[col]
    arr = np.asarray(fr, np.float32)
    return Image.fromarray((arr * (1 - a) + c * a).astype(np.uint8))
_vig = [None]
def vignette(fr):
    if _vig[0] is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W * .75)) ** 2 + ((yy - 560) / (H * .6)) ** 2)
        _vig[0] = (1 - 0.30 * np.clip(r - .45, 0, 1) ** 1.5)[:, :, None]
    return Image.fromarray((np.asarray(fr, np.float32) * _vig[0]).astype(np.uint8))
