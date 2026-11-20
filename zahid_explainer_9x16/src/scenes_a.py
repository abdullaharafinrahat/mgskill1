from props import *
def b_keyg():
    p = Pen(70, 150); p.ell((10, 6, 60, 56), None, 0); p.d.ellipse([10 * 2, 6 * 2, 60 * 2, 56 * 2], outline=INK, width=22); p.d.ellipse([16 * 2, 12 * 2, 54 * 2, 50 * 2], outline=(255, 205, 60), width=12)
    p.rr((29, 54, 41, 140), (255, 205, 60), 3); p.rr((41, 100, 56, 112), (255, 205, 60), 2); p.rr((41, 122, 52, 132), (255, 205, 60), 2); return p.done()
B['keyg'] = b_keyg
def dark(c): return darken(c, .5)
def s_hook(sc):
    c = sc.cue; sc.bg(NAVY, DTEAL, .2); tl = c('পঞ্চাশ')
    img(sc, ('rays', 300, 14), 360, 400, z=.4, s=2.2, a=.5, anim=lambda t: dict(rot=t * 18))
    img(sc, lambda t: ('stopw', int(eo(ramp(t, .15, tl)) * 300) // 6 * 6, 110, 0), 360, 360, t0=.05, s=1.5, anim=bob(5, 2))
    count_txt(sc, 360, 650, .2, tl, 0, 50, size=190, fill=MUST)
    txt(sc, 'মিনিট', 360, 800, size=88, fill=WHITE, stroke=6, t0=c('মিনিট'), kind='up')
    img(sc, lambda t: ('phone', 'cracked' if t < c('বদলাতে') + .25 else 'ok', 84, 0), 120, 760, t0=.3, kind='left', s=1.1, rot=-12, anim=bob(4, 1.6), z=1.2)
    sc.cam((0, 360, 470, 1.3, 0), (tl, 360, 470, 1.0, 0), (tl + .14, 360, 470, 1.2, 0, eo), (sc.dur, 360, 470, 1.08, 0))
    sc.shake(tl, .5, 18); sc.flash(tl, .4, (255, 240, 180), .8); sc.hit(tl, 'big')
def s_fate(sc):
    c = sc.cue; sc.bg((250, 214, 130), (232, 160, 70), .2)
    parallax_shapes(sc, (240, 190, 100), .35, 6, 3, 200, 800)
    ts = c('ভাগ্য') - .2; te = c('বদলে', end=True) + .1
    img(sc, ('poster', 'একটা লাইন', 54, 0, 1, INK, (255, 250, 230), 0), 360, 250, t0=c('লাইনই') - .3, kind='down', anim=sway(3, 2.4))
    def ck(t):
        a = 2 * math.pi * 2.5 * eo(ramp(t, ts, te)); return ('coin', 0 if math.cos(a) > 0 else 1, 90)
    def can(t):
        a = 2 * math.pi * 2.5 * eo(ramp(t, ts, te)); r = ramp(t, ts, te)
        base = dict(dy=-330 * math.sin(math.pi * r) - 12 * math.exp(-(t - te) * 8) * math.sin((t - te) * 30) * (t > te), sx=max(abs(math.cos(a)), .06))
        return base
    img(sc, ck, 360, 600, t0=0, s=1.15, anim=can, z=1.1)
    sc.add(('shop', 'smalldim'), 360, 760, z=.5, s_=.6, a=.0)
    sc.cam((0, 360, 400, .9, -3), (te, 360, 470, 1.0, 2), (te + .1, 360, 480, 1.28, 0, eo), (sc.dur, 360, 480, 1.18, 0))
    sc.flash(te, .5, (255, 220, 90), .7); sc.shake(te, .35, 10); sc.hit(te, 'hit')
def s_rent(sc):
    c = sc.cue; sc.bg((190, 200, 220), (150, 160, 190), .15); tp = c('শাটার') - .15
    img(sc, ('wall', 900, 1300, (206, 214, 232)), 700, 470, z=.3)
    for i in range(5):
        t_i = .2 + .42 * i
        img(sc, ('cal', 'মাস', bn(12 - i), RED), 300, 400, t0=t_i, kind='pop', d=.2, z=1, s=1.5, rot=-4 + i * 2,
            anim=(leave(t_i + .42, .25, 'down', 400) if i < 4 else None), t1=1e9 if i == 4 else t_i + .7)
    stamp(sc, 'ভাড়া', 330, 640, c('ভাড়া'), size=96, rot=-10)
    img(sc, ('shop', 'smalldim'), 1000, 600, z=1, s=1.2, t0=-99, kind='fade')
    img(sc, lambda t: ('shutter', 300, 212, int(eo(ramp(t, c('শাটার') + .3, c('শাটার') + 1.9)) * .96 * 30) / 30.0), 1000, 661, z=1, s=1.2)
    chr_(sc, 'zahid', 780, 870, z=1.1, s=.85, expr='neutral', ex=[(tp + .2, 'worry')], pose='down', po=[(tp + 1.5, 'hips')], look=1)
    sc.cam((0, 300, 470, 1.15, 0), (tp - .4, 330, 470, 1.25, 0), (tp + .5, 940, 520, 1.0, 0), (sc.dur, 900, 560, 1.3, 0))
    sc.shake(c('বন্ধ'), .3, 8)
def s_mirpur(sc):
    c = sc.cue; sc.bg((200, 232, 220), (160, 205, 190), .15); t2 = c('ছোট') - .05
    img(sc, ('map',), 300, 470, z=1, t0=-99, kind='fade', s=1.1, t1=t2 + .1)
    img(sc, ('pin',), 300, 360, t0=c('মিরপুরের') - .1, kind='down', z=1, s=1.4, anim=lambda t: dict(dy=-18 * abs(math.sin((t - c('মিরপুরের')) * 6)) * math.exp(-(t - c('মিরপুরের')) * 2) if t > c('মিরপুরের') else 0), t1=t2 + .1)
    X = 2000
    sc.add(('grad', (140, 200, 255), (255, 232, 190)), 360 + X, 640, z=.2)
    sc.add(('skyline', (150, 160, 200), 900, 500, 3), 360 + X, 600, z=.45)
    sc.add(('shop', 'big'), 70 + X, 560, z=1, s_=1.0, anchor=(.5, .5))
    sc.add(('shop', 'big'), 650 + X, 560, z=1, s_=1.0)
    img(sc, ('shop', 'small'), 360 + X, 740, t0=t2 + .1, kind='pop', s=.78, z=1.05, d=.5)
    sc.cam((0, 300, 400, 1.0, 0), (t2 - .02, 300, 360, 3.8, 0), (t2, 360 + X, 520, .75, 0), (sc.dur, 360 + X, 520, 1.1, 0))
    sc.flash(t2, .28, (255, 255, 255), .9)
def s_father(sc):
    c = sc.cue; sc.bg((226, 196, 150), (196, 160, 112), .2); sc.add(('wall', 1400, 1300, (222, 190, 140)), 600, 470, z=.35)
    img(sc, ('rr', 230, 290, (130, 90, 60), 10, 1), 240, 390, z=1, t0=.05, kind='down')
    img(sc, ('rr', 190, 250, (214, 186, 140), 6, 1), 240, 390, z=1, t0=.05, kind='fade')
    chr_(sc, 'cust', 240, 495, z=1, s=.42, sil=(120, 84, 56), anim=enter(.1, 'fade'))
    img(sc, ('keyg',), 240, 600, t0=c('শেষ') - .2, kind='down', z=1.05, s=1.1, anchor=(.5, .1), anim=sway(8, 2.2))
    tp = c('দেয়ালে') - .5
    img(sc, lambda t: ('clock', 120, 100, 110, 'wall', (int(t) * 6) % 360), 900, 400, t0=tp, kind='pop', z=1, s=1.25)
    img(sc, ('burst', (255, 255, 255), 80, 8), 900, 400, t0=tp, kind='fade', a=.2, z=.9, s=2.2, anim=lambda t: dict(rot=t * 10))
    sc.cam((0, 240, 470, 1.05, 0), (tp - .1, 260, 470, 1.35, 2), (tp + .6, 900, 440, 1.2, 0), (sc.dur, 900, 420, 1.45, 0))
def s_tried(sc):
    c = sc.cue; sc.bg((250, 226, 170), (236, 190, 120), .2); ts = c('শুধু') - .1
    img(sc, ('wall', 1000, 1300, (240, 214, 160)), 500, 470, z=.35)
    img(sc, lambda t: ('clock', 40, 300, 50, 'wall', -1), 360, 300, z=.7, s=1, t0=-99, kind='fade')
    chr_(sc, 'zahid', 360, 880, s=.95, expr='worry', pose='work', ex=[(ts, 'neutral')], look=0, lk=[(ts, -1)], po=[(ts, 'down')])
    sc.add(('counter', 520, 170), 360, 830, z=1.05)
    items = [('wrench',), ('broom',), ('card', 'অফার', 200, 90, CORAL, 34, WHITE), ('card', 'ছাড়!', 180, 90, TEAL, 34, WHITE), ('wrench',), ('card', 'ফ্লায়ার', 220, 90, LILAC, 34, WHITE)]
    for i, k in enumerate(items):
        t0 = .1 + .55 * i; yy = 230 + (i % 3) * 150; z = (.8, 1.0, 1.25)[i % 3]
        sc.add(k, 360, yy, z=z, rot=0, anim=lambda t, t0=t0: dict(dx=lerp(-520, 520, ramp(t, t0, t0 + .95)), rot=t * 200, a=1 if t0 < t < t0 + .95 and t < ts + .1 else 0))
    sc.add(('rr', 260, 18, (150, 105, 70), 6, 1), 600, 660, z=1, anim=enter(ts, 'right'))
    img(sc, lambda t: ('stopw', 40, 60, 0), 600, 590, t0=ts, kind='right', z=1, s=1.0, a=.9)
    sc.add(('spot', 100, 190), 600, 590, fixed=False, z=1, s_=4.5, anim=lambda t: dict(a=ramp(t, ts + .2, ts + .7)))
    img(sc, ('cross', RED, 90), 600, 590, t0=c('মেপে'), z=1.1, s=1.2)
    sc.cam((0, 360, 470, 1.0, 0), (ts, 360, 470, 1.12, 0), (ts + .8, 480, 540, 1.5, -2), (sc.dur, 480, 540, 1.6, 0))
    sc.shake(c('মেপে'), .25, 8)
def s_ad(sc):
    c = sc.cue; sc.bg((200, 160, 120), (150, 112, 86), .2); sc.add(('wall', 1000, 1300, (214, 176, 134)), 500, 470, z=.35)
    t0 = c('দ্রুত') - .3
    img(sc, lambda t: ('poster', 'দ্রুত ও\nনির্ভরযোগ্য\nমোবাইল সার্ভিস', 50, 0, ramp(t, t0 + .3, t0 + 1.3), INK, (255, 244, 214), 0), 360, 290, t0=.1, kind='down', z=1, s=1.0, anchor=(.5, 0.0),
        anim=lambda t: dict(rot=14 * math.exp(-t * 1.6) * math.cos(t * 6)))
    chr_(sc, 'zahid', 170, 930, s=.8, expr='smug', pose='point', ex=[(c('দ্রুত'), 'smug')], z=1.1, talk=())
    sc.add(('counter', 280, 160), 540, 840, z=1.05)
    sc.cam((0, 360, 480, 1.0, 1), (c('দ্রুত'), 340, 450, 1.1, -1), (sc.dur, 360, 450, 1.2, 0))
def s_howfast(sc):
    c = sc.cue; sc.bg(NAVY, (60, 50, 120), .2); tq = c('দ্রুত', n=1)
    img(sc, ('rays', 300, 12), 360, 400, z=.3, s=2.2, a=.3, anim=lambda t: dict(rot=-t * 14))
    sc.add(('text', 'দ্রুত', 180, MUST, 8, INK), 360, 380, anim=lambda t: dict(sx=lerp(1, 1.45, eio(ramp(t, c('মানে'), tq))) * (1 + .02 * math.sin(t * 30) * ramp(t, c('মানে'), tq)), sy=lerp(1, .8, eio(ramp(t, c('মানে'), tq)))))
    p = [('rr', 560, 28, (255, 232, 160), 6, 1)]
    sc.add(p[0], 360, 560, anim=enter(c('মানে') - .3, 'up'))
    for i in range(15): sc.add(('rr', 5, 18 if i % 5 else 34, INK, 1, 0), 120 + i * 40, 560, anim=enter(c('মানে') - .1 + i * .02, 'fade'))
    txt(sc, '?', 360, 700, size=300, fill=CORAL, stroke=10, t0=tq, kind='pop', d=.25)
    sc.cam((0, 360, 470, 1.0, 0), (tq - .05, 360, 470, 1.06, 0), (tq + .12, 360, 520, 1.3, 4, eo), (sc.dur, 360, 520, 1.2, 2))
    sc.shake(tq, .4, 16); sc.flash(tq, .25, (255, 120, 100), .5); sc.hit(tq, 'hit')
def s_daily(sc):
    sc.bg((255, 214, 150), (240, 170, 110), .2); sc.add(('skyline', (214, 160, 120), 900, 500, 5), 400, 560, z=.35)
    sc.add(('shop', 'small'), 120, 650, z=1, s_=1.0)
    cols = [(40, 50, 90), (90, 40, 60), (30, 80, 70), (70, 50, 110), (40, 40, 40)]
    for i in range(5):
        z = (.7, 1.0, 1.25)[i % 3]; s = (.5, .75, 1.0)[i % 3]; t0 = .05 + .1 * i
        chr_(sc, ('cust', 'cust2', 'cust3', 'cust4', 'bro')[i], 800, 840 - (1 - s) * 100, z=z, s=s, sil=cols[i], walk=lambda t: int(t * 10) % 8,
             anim=lambda t, t0=t0: dict(dx=lerp(0, -520 - (i % 3) * 60, ramp(t, t0, t0 + 1.25)) , a=ramp(t, t0, t0 + .1)))
    sc.cam((0, 540, 470, 1.0, 0), (sc.dur, 280, 470, 1.15, -1))
def s_ask(sc):
    c = sc.cue; sc.bg((200, 224, 214), (150, 190, 180), .2); sc.add(('wall', 1000, 1300, (214, 232, 224)), 500, 470, z=.35)
    chr_(sc, 'zahid', 530, 870, s=.9, expr='neutral', ex=[(c('কতক্ষণ'), 'worry')], z=1)
    sc.add(('counter', 330, 160), 530, 830, z=1.05)
    chr_(sc, 'cust', 200, 870, s=.95, expr='neutral', pose='hold', talk=[(c('ভাই') - .1, sc.dur - .2)], z=1.1)
    img(sc, ('phone', 'cracked', 84, 0), 200, 704, t0=.1, z=1.15, s=.7)
    img(sc, ('bubble', 'ভাই, কতক্ষণ লাগবে?', 36, 'bl'), 330, 330, t0=c('ভাই') - .1, kind='pop', z=1.1, anim=bob(4, 2))
    sc.cam((0, 380, 500, 1.0, 1), (c('কতক্ষণ'), 300, 480, 1.18, 0), (sc.dur, 260, 520, 1.38, -1))
def s_vague(sc):
    c = sc.cue; sc.bg((214, 200, 230), (170, 150, 200), .2); sc.add(('wall', 1000, 1300, (226, 214, 238)), 500, 470, z=.35)
    tk = c('কখন')
    chr_(sc, 'zahid', 520, 870, s=.9, expr='neutral', ex=[(tk, 'worry')], talk=[(c('জাহিদ'), c('যাবে', end=True))])
    sc.add(('counter', 330, 160), 520, 830, z=1.05)
    chr_(sc, 'cust', 190, 870, s=.95, expr='neutral', pose='talk', ex=[(c('লোকটা'), 'angry'), (tk, 'worry')], talk=[(c('লোকটা'), sc.dur - .2)], lk=[(0, 1)])
    img(sc, ('bubble', 'হয়ে যাবে।', 36, 'bc', (255, 244, 200)), 520, 430, t0=c('হয়ে') - .1, z=1.1, anim=comb(bob(5, 1.6), lambda t: dict(a=1 if t < c('লোকটা') else .55)))
    for i in range(3): img(sc, ('text', '…', 50, (120, 110, 150), 0, INK), 420 + i * 40, 330 - i * 30, t0=c('হয়ে') + .4 + i * .15, kind='up')
    txt(sc, 'কখন?', 190, 330, size=120, fill=CORAL, stroke=8, t0=tk, d=.22, z=1.2)
    sc.cam((0, 520, 480, 1.25, 0), (c('লোকটা') - .1, 520, 480, 1.25, 0), (c('লোকটা') + .5, 220, 480, 1.1, 2), (tk, 220, 470, 1.1, 0), (tk + .15, 210, 440, 1.45, -3, eo), (sc.dur, 210, 450, 1.35, 0))
    sc.shake(tk, .35, 12); sc.hit(tk, 'hit')
def s_noanswer(sc):
    c = sc.cue; sc.bg((200, 200, 215), (150, 150, 180), .2); tp = c('কিছুক্ষণ')
    sc.add(('skyline', (130, 140, 170), 1400, 500, 7), 700, 620, z=.3)
    sc.add(('shop', 'smalldim'), 140, 640, z=.9, s_=1.0)
    chr_(sc, 'zahid', 290, 880, z=1.05, s=.9, expr='worry', pose='shrug', ex=[(tp + 1.2, 'sad')], talk=())
    img(sc, ('bubble', '…', 60, 'bl', (255, 255, 255, 255)), 300, 400, t0=.4, z=1.1, anim=bob(4, 2.2), t1=tp + .6)
    sc.add(('shop', 'big'), 1130, 480, z=1.0, s_=1.35, anim=lambda t: dict(s=1 + .015 * math.sin(t * 5)))
    chr_(sc, 'cust', 420, 880, z=1.05, s=.9, expr='neutral', walk=walk_fn(tp, tp + 3.2), pose='hold',
         anim=lambda t: dict(dx=lerp(0, 760, eio(ramp(t, tp, tp + 3.2))), a=1 - ramp(t, tp + 3.0, tp + 3.5)), lk=[(tp, 1)])
    sc.cam((0, 290, 480, 1.25, 0), (tp, 300, 480, 1.25, 0), (tp + 1.0, 560, 470, 1.0, 0), (tp + 3.3, 1050, 480, 1.0, 0), (sc.dur, 1050, 480, 1.1, 0))
    sc.flash(tp + 2.9, .2, (255, 235, 180), .35)
def s_girl(sc):
    c = sc.cue; sc.bg((255, 220, 200), (240, 170, 150), .2); sc.add(('wall', 1000, 1300, (255, 230, 214)), 500, 470, z=.35)
    sc.add(('rr', 200, 360, (150, 105, 70), 10, 1), 640, 640, z=.8)
    chr_(sc, 'girl', 380, 880, z=1.05, s=.95, expr='neutral', ex=[(c('পরীক্ষা') - .3, 'worry')], walk=walk_fn(.1, 1.6), po=[(1.7, 'down')],
         anim=lambda t: dict(dx=lerp(480, 0, eo(ramp(t, .1, 1.6)))))
    img(sc, ('card', 'পরীক্ষা', 270, 100, RED, 44, WHITE), 540, 260, t0=c('পরীক্ষা') - .2, rot=-8, z=1.15, anim=sway(3, 1.5))
    img(sc, ('cal', 'কাল', '!', RED), 170, 330, t0=c('পরদিন') - .1, z=1.1, s=1.0, rot=6)
    sc.cam((0, 460, 480, 1.0, 2), (1.6, 380, 480, 1.1, 0), (sc.dur, 360, 450, 1.4, -1))
def s_allphone(sc):
    c = sc.cue; sc.bg((60, 70, 120), (36, 40, 84), .2); tc = c('ভাঙা')
    parallax_shapes(sc, (80, 92, 150), .4, 7, 9, 150, 800, (80, 200))
    for i, (tx, col, side) in enumerate((('গণিত', CORAL, -1), ('বিজ্ঞান', TEAL, 1), ('ইংরেজি', MUST, -1), ('ইতিহাস', LILAC, 1))):
        t0 = c('সব') + .1 * i
        sc.add(('card', tx, 190, 80, col, 32, WHITE if col != MUST else INK), 360, 300 + i * 90, z=1.1, rot=side * 8,
               anim=lambda t, t0=t0, side=side: dict(dx=side * lerp(420, 0, eo(ramp(t, t0, t0 + .6))), s=lerp(1, .2, ramp(t, t0 + .5, t0 + .75)), a=ramp(t, t0, t0 + .1) * (1 - ramp(t, t0 + .7, t0 + .75))))
    img(sc, lambda t: ('phone', 'cracked' if t > tc else 'notes', 200, 0), 360, 470, t0=0, z=1, s=1.0, anim=comb(bob(4, 2), lambda t: dict(s=1 + .1 * (1 - eo((t - tc) / .4)) ** 2) if t > tc else {}))
    sc.cam((0, 360, 470, .9, 0), (tc - .1, 360, 470, 1.05, 0), (tc + .1, 330, 420, 1.55, 3, eo), (sc.dur, 330, 430, 1.7, 0))
    sc.shake(tc, .5, 20); sc.flash(tc, .3, (255, 255, 255), .8); sc.hit(tc, 'crack')
def s_girlask(sc):
    c = sc.cue; sc.bg((38, 44, 96), (26, 28, 70), .2); tz = c('জাহিদ')
    sc.add(('moon', 70), 600, 220, z=.45); sc.add(('skyline', (50, 60, 110), 900, 400, 4), 400, 640, z=.4)
    chr_(sc, 'girl', 170, 880, s=.9, expr='worry', ex=[(tz + .4, 'sad')], talk=[(0, c('পাব', end=True))], z=1)
    sc.add(('counter', 330, 160), 540, 830, z=1.05)
    chr_(sc, 'zahid', 540, 870, s=.9, expr='neutral', ex=[(tz + .5, 'smug')], talk=[(tz, sc.dur - .1)], z=1.0)
    img(sc, ('bubble', 'আজ রাতের মধ্যে\nপাব?', 34, 'bl'), 320, 360, t0=c('আজ') - .1, z=1.1, anim=bob(4, 2.2), t1=tz + .2)
    img(sc, ('bubble', 'হয়ে যাবে।', 36, 'bc', (255, 244, 200)), 500, 420, t0=c('যাবে') - .5, z=1.1, anim=bob(4, 1.8))
    sc.cam((0, 260, 480, 1.1, 0), (tz - .3, 280, 480, 1.2, 0), (tz + .4, 470, 480, 1.25, -1), (sc.dur, 380, 500, 1.1, 0))
def s_silence(sc):
    c = sc.cue; sc.bg((120, 130, 150), (84, 92, 112), .2); tk = c('কখন')
    img(sc, lambda t: ('clock', (int(t) * 6) % 360, 200, 110, 'neon', int(t * 1) * 6 % 360), 360, 290, z=.5, s=1.5, t0=-99, kind='fade')
    chr_(sc, 'girl', 360, 900, s=1.3, expr='neutral', ex=[(c('চুপ'), 'sad'), (tk - .4, 'neutral')], talk=[(tk - .15, sc.dur - .1)], z=1.1)
    txt(sc, 'কখন?', 360, 150, size=120, fill=CORAL, stroke=9, t0=tk, d=.22, fixed=True)
    sc.cam((0, 360, 470, 1.0, 0), (tk - .1, 360, 540, 1.3, 0), (tk + .1, 360, 530, 1.45, -2, eo), (sc.dur, 360, 530, 1.5, 0))
    sc.shake(tk, .3, 9); sc.hit(tk, 'tick')
def s_fork(sc):
    c = sc.cue; sc.bg((250, 226, 170), (230, 190, 130), .2)
    sc.add(('skyline', (214, 176, 130), 900, 400, 8), 400, 640, z=.35)
    sc.add(('sign', 'অপেক্ষা', 'অন্য দোকান'), 360, 470, z=1, s_=1.0)
    sc.add(('bench', 160), 130, 720, z=.9, s_=.8); sc.add(('shop', 'big'), 620, 640, z=.8, s_=.45)
    tr = c('দোকানে')
    chr_(sc, 'girl', 360, 880, s=.75, z=1.05, expr='worry', lk=[(c('অপেক্ষা'), -1), (c('নাকি'), 1)], ex=[(tr, 'neutral')])
    sc.cam((0, 360, 560, 1.0, 0), (c('অপেক্ষা') - .2, 360, 560, 1.0, 0), (c('অপেক্ষা') + .3, 230, 600, 1.3, -2), (c('নাকি') - .1, 240, 600, 1.3, -2), (c('নাকি') + .35, 500, 600, 1.3, 2), (sc.dur, 500, 610, 1.35, 0))
def s_simple(sc):
    c = sc.cue; sc.bg((226, 236, 246), (190, 210, 235), .2); tm = c('মনে')
    sc.add(('skyline', (190, 204, 230), 900, 300, 2), 400, 760, z=.4)
    img(sc, ('bubble', 'কথাটা খুব সাধারণ।', 28, 'bl'), 330, 420, t0=.2, z=1, anim=comb(bob(3, 2), leave(c('কিন্তু') - .1, .3, 'up', 60)))
    chr_(sc, 'girl', 240, 900, z=1.0, s=.85, expr='neutral', sil=(150, 160, 190), talk=[(.3, c('কিন্তু') - .3)], anim=comb(enter(.1, 'fade', .3), leave(c('কিন্তু') - .1, .3, 'fade')))
    chr_(sc, 'zahid', 360, 880, z=1.05, s=1.0, expr='neutral', ex=[(c('কিন্তু'), 'think')], lk=[(tm, 0)], anim=enter(c('জাহিদের') - .3, 'up', .4, 140))
    img(sc, ('burst', (255, 238, 120), 120, 12), 360, 330, t0=tm, kind='fade', z=1, s=2.0, a=.6, anim=lambda t: dict(rot=t * 40))
    img(sc, ('bulb',), 360, 340, t0=tm, kind='pop', z=1.1, s=1.5, anim=bob(5, 1.2))
    sc.cam((0, 360, 470, .8, 0), (c('জাহিদের'), 360, 480, .95, 0), (tm, 360, 460, 1.0, 0), (tm + .2, 360, 480, 1.3, 0, eo), (sc.dur, 360, 470, 1.4, 0))
    sc.flash(tm, .3, (255, 240, 140), .55); sc.hit(tm, 'ding')
def s_realize(sc):
    c = sc.cue; sc.bg((30, 70, 90), (14, 34, 50), .2); tj = c('জানতে'); tf = c('ফিরে')
    img(sc, ('rays', 300, 16), 360, 420, z=.4, s=2.2, a=.4, t0=tj, anim=lambda t: dict(rot=t * 20))
    img(sc, lambda t: ('phone', 'ok', 150, 0), 360, 470, t0=0, z=1, s=1.0, anim=lambda t: dict(
        dx=lerp(0, 0, 1), dy=lerp(0, 300, eio(ramp(t, tj, tj + .5))) - lerp(0, 330, eio(ramp(t, tf, tf + .5))), s=lerp(1, .45, eio(ramp(t, tj, tj + .5))) * lerp(1, .2, eio(ramp(t, tf, tf + .5))), a=1 - ramp(t, tf + .4, tf + .5)))
    img(sc, ('wrench',), 260, 360, t0=.1, z=1.1, anim=lambda t: dict(rot=t * 90, a=1 - ramp(t, tj - .2, tj + .1)))
    img(sc, ('cross', RED, 160), 360, 470, t0=c('ঠিক') - .05, z=1.2, anim=lambda t: dict(a=1 - ramp(t, tj, tj + .1)), s=1.0)
    img(sc, lambda t: ('clock', int(t * 120) % 360, int(t * 10) % 360, 120, 'plain', -1), 360, 400, t0=tj + .1, z=1, s=1.5, anim=lambda t: dict(s=1 + .04 * math.sin(t * 6)))
    sc.cam((0, 360, 470, 1.0, 0), (tj, 360, 470, 1.05, 0), (tj + .5, 360, 420, 1.3, 2), (sc.dur, 360, 420, 1.5, 0))
    sc.flash(tj + .15, .3, (160, 255, 220), .5); sc.hit(tj + .1, 'ding'); sc.flash(tf + .5, .35, (255, 255, 255), .6)
def s_night(sc):
    c = sc.cue; sc.bg(NIGHT, (30, 36, 84), .2); tc = c('ঘড়িটার') - .6
    sc.add(('moon', 50), 120, 160, z=.3)
    sc.add(('skyline', (36, 44, 90), 1500, 500, 6), 700, 700, z=.35)
    sc.add(('shop', 'small'), 300, 600, z=1, s_=1.25)
    img(sc, lambda t: ('shutter', 300, 212, .62), 300, 665, z=1, s=1.25, t0=-99)
    sc.add(('ring', 150, (255, 235, 150), 5), 1080, 330, z=.9, s_=1.3, a=.35, anim=lambda t: dict(s=1 + .08 * math.sin(t * 4)))
    img(sc, lambda t: ('clock', 120, 100, 130, 'wall', (int(t) * 6) % 360), 1080, 330, z=1, s=1.3, t0=-99, kind='fade')
    chr_(sc, 'zahid', 860, 880, z=1.1, s=1.0, expr='neutral', ex=[(c('প্রথমবার'), 'think')], lk=[(tc, 1)], look=0)
    sc.cam((0, 300, 520, .85, 0), (1.4, 340, 520, 1.15, 0), (tc, 380, 480, 1.1, 0), (tc + .8, 1000, 380, 1.3, 0), (sc.dur, 1060, 340, 1.7, 0))
    sc.flash(c('তাকাল'), .3, (255, 230, 150), .4)
FUNCS_A = [s_hook, s_fate, s_rent, s_mirpur, s_father, s_tried, s_ad, s_howfast, s_daily, s_ask, s_vague, s_noanswer, s_girl, s_allphone, s_girlask, s_silence, s_fork, s_simple, s_realize, s_night]
