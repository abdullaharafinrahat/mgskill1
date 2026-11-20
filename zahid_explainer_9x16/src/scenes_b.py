from props import *
from scenes_a import *
def s_ten(sc):
    c = sc.cue; sc.bg((226, 240, 232), (176, 206, 196), .2); tn = c('খাতায়') - .6
    for i in range(10):
        x = 110 + (i % 5) * 125; y = 290 + (i // 5) * 230; t0 = c('দশটা') - .1 + .2 * i
        img(sc, lambda t, t0=t0: ('phone', 'cracked' if t < t0 + .35 else 'ok', 62, 0), x, y, t0=t0, kind='up', d=.25, z=1, anim=leave(tn + .05 * i, .35, 'up', 500))
        img(sc, ('check', GREEN, 44), x + 30, y + 54, t0=t0 + .4, kind='pop', d=.2, z=1.1, anim=leave(tn + .05 * i, .35, 'up', 500))
    img(sc, ('notebook', 0) if False else (lambda t: ('notebook', int(ramp(t, c('শুরুর'), c('লিখল') + .6) * 5.99))), 360, 540, t0=tn, kind='up', dist=700, d=.6, z=1, s=1.12)
    img(sc, ('rr', 14, 120, (40, 60, 160), 6, 1), 620, 800, t0=tn + .4, kind='right', rot=35, z=1.1, anim=lambda t: dict(dx=-30 * math.sin(t * 5), dy=-14 * math.sin(t * 9)))
    sc.cam((0, 360, 420, 1.0, 0), (tn - .3, 360, 450, 1.1, 0), (tn + .6, 360, 560, 1.15, 2), (sc.dur, 340, 540, 1.3, 0))
def s_chart(sc):
    c = sc.cue; sc.bg((250, 238, 214), (232, 214, 176), .2); tH = c('পঞ্চাশ'); tL = c('চল্লিশ')
    sc.add(lambda t: ('bars', int(ramp(t, .35, c('বেশি') + .1) * 40) / 40.0, 1 if tH - .5 <= t < tL - .6 else (2 if t >= tL - .6 else 0)), 360, 470, z=1, t0=0, anim=enter(0, 'up', .5, 120))
    count_txt(sc, 360, 190, tH - 1.0, tH + .3, 0, 50, size=150, fill=CORAL, stroke=9, fixed=True, t_end=tL - .75)
    count_txt(sc, 360, 190, tL - .55, tL + .3, 0, 40, size=150, fill=TEAL, stroke=9, fixed=True)
    sc.cam((0, 360, 470, .95, 0), (c('বেশি') - .2, 360, 480, 1.0, 0), (tH - .2, 237, 360, 1.9, -2), (tH + .1, 237, 350, 2.2, 0, eo), (tL - .9, 250, 380, 2.0, 0), (tL - .45, 453, 430, 2.0, 2), (sc.dur, 453, 430, 2.25, 0))
    sc.shake(tH + .25, .5, 16); sc.flash(tH + .25, .35, (255, 140, 110), .55); sc.hit(tH + .25, 'big')
    sc.hit(tL + .3, 'hit'); sc.flash(tL + .3, .25, (130, 230, 230), .4)
def s_strike(sc):
    c = sc.cue; sc.bg((255, 190, 130), (255, 224, 170), .2); tk = c('কেটে')
    sc.add(('sun', 90), 560, 330, z=.3, anim=lambda t: dict(dy=lerp(420, 0, eo(ramp(t, 0, 2.4)))))
    sc.add(('rays', 300, 14), 560, 330, z=.3, a=.5, anim=lambda t: dict(rot=t * 8, dy=lerp(420, 0, eo(ramp(t, 0, 2.4)))))
    sc.add(('skyline', (230, 150, 110), 900, 300, 9), 400, 700, z=.5)
    sc.add(lambda t: ('poster', 'দ্রুত ও\nনির্ভরযোগ্য\nমোবাইল সার্ভিস', 50, int(eo(ramp(t, tk - .1, tk + .5)) * 20) / 20.0, 1, INK, (255, 244, 214), 0), 360, 430, anim=comb(enter(.1, 'down', .4, 100), sway(1.2, 2.5)))
    chr_(sc, 'zahid', 150, 890, s=.7, expr='neutral', ex=[(tk, 'angry'), (tk + .7, 'smug')], pose='down', po=[(tk - .2, 'point')])
    sc.cam((0, 360, 480, 1.0, 0), (tk, 360, 440, 1.15, 0), (tk + .6, 360, 420, 1.4, 0), (sc.dur, 360, 420, 1.5, 0))
    sc.shake(tk + .5, .25, 7); sc.hit(tk + .1, 'scratch')
def s_write(sc):
    c = sc.cue; sc.bg((255, 214, 170), (255, 236, 200), .2); t0 = c('সাধারণ') - .1; t1 = c('মিনিটে', end=True)
    sc.add(('skyline', (236, 190, 150), 900, 300, 11), 400, 700, z=.5)
    sc.add(lambda t: ('poster', 'সাধারণ মডেলের\nস্ক্রিন বদলান\n৫০ মিনিটে।', 48, 0, int(ramp(t, t0, t1) * 24) / 24.0, INK, (255, 252, 240), 0), 360, 380, anim=enter(.05, 'down', .4, 90))
    img(sc, ('broom',), 360, 400, t0=t0 - .1, z=1.15, s=.8, rot=70, anim=lambda t: dict(dx=lerp(-200, 200, ramp(t, t0, t1)), a=1 - ramp(t, t1 + .1, t1 + .3), dy=8 * math.sin(t * 14)))
    stamp(sc, '৫০', 360, 740, c('৫০') - .3, size=170, fill=RED, rot=-6, z=1.2)
    chr_(sc, 'zahid', 570, 900, s=.65, expr='happy', pose='talk', z=1.1)
    sc.cam((0, 200, 420, 1.1, 0), (t1 - .2, 480, 430, 1.1, 0), (t1 + .2, 360, 520, 1.3, -2), (sc.dur, 360, 540, 1.38, 0))
    sc.shake(t1 + .1, .4, 12); sc.hit(t1 + .1, 'big'); sc.flash(t1 + .1, .25, (255, 230, 150), .5)
def s_half(sc):
    c = sc.cue; sc.bg((40, 40, 70), (24, 24, 50), .2); th = c('অর্ধেক') - .1
    sc.add(('rays', 300, 14), 360, 330, z=.3, s_=2.2, a=.3, anim=lambda t: dict(rot=t * 10))
    img(sc, lambda t: ('stopw', int(lerp(0, 420, ramp(t, 0, .9))) // 6 * 6 % 360, 130, 1 if t > .9 else 0), 360, 340, t0=0, s=1.4, kind='pop',
        anim=lambda t: dict(dx=7 * math.sin(t * 60) * (.9 < t < 1.6), s=1 + .02 * math.sin(t * 5)), t1=th + .5)
    sc.add(('tag', 0, 'চার্জ', MUST), 360, 700, z=1.1, s_=1.3, t0=c('চার্জ') - .2, t1=th, anim=enter(c('চার্জ') - .2, 'down', .3, 200))
    sc.add(('tag', 1, 'চার্জ', MUST), 360, 700, z=1.1, s_=1.3, t0=th, anim=lambda t: dict(dx=-20 * eo(ramp(t, th, th + .3)), rot=-6 * eo(ramp(t, th, th + .3))))
    sc.add(('tag', 2, 'চার্জ', MUST), 360, 700, z=1.1, s_=1.3, t0=th, anim=lambda t: dict(dx=40 * eo(ramp(t, th, th + .5)), dy=300 * (ramp(t, th + .1, th + 1.0)) ** 2, rot=40 * ramp(t, th, th + 1), a=1 - ramp(t, th + .6, th + 1.0)))
    sc.cam((0, 360, 400, 1.2, 0), (.9, 360, 400, 1.35, 3), (th - .4, 360, 560, 1.1, 0), (th + .2, 360, 650, 1.35, 0), (sc.dur, 360, 650, 1.45, 0))
    sc.flash(.9, .3, (255, 60, 60), .5); sc.shake(.9, .5, 10); sc.hit(.9, 'alarm'); sc.hit(th + .1, 'slice'); sc.shake(th + .1, .3, 12)
def s_six(sc):
    c = sc.cue; sc.bg((255, 226, 176), (240, 190, 130), .2); tcl = c('ঘড়ির') - .2; td = c('দাম')
    names = ['cust', 'cust2', 'cust3', 'cust4', 'bro', 'girl']
    sc.add(('wall', 1000, 1300, (250, 218, 170)), 500, 470, z=.35)
    for i, n in enumerate(names):
        t0 = .25 + .4 * i
        chr_(sc, n, 105 + i * 102, 770, z=1, s=.5, expr='neutral', ex=[(td, 'sad'), (tcl, 'happy')], lk=[(tcl, 2)], pose='down', anim=comb(enter(t0, 'pop', .3), lambda t: dict(dy=-6 * abs(math.sin(t * 3.1415)) if t > tcl + 1 else 0)))
    sc.add(('bench', 640), 360, 740, z=1.02)
    count_txt(sc, 360, 300, .25, 2.4, 0, 6, size=210, fill=CORAL, stroke=10, t_end=td - .1)
    img(sc, ('bubble', 'দাম?', 54, 'bc'), 360, 380, t0=td - .1, z=1.1, t1=tcl + .1)
    img(sc, ('cross', RED, 130), 360, 360, t0=td + .5, z=1.2, t1=tcl + .1)
    img(sc, lambda t: ('clock', int(t * 36) % 360, 200, 110, 'wall', (int(t) * 6) % 360), 360, 330, t0=tcl, kind='pop', z=.9, s=1.3)
    sc.cam((0, 360, 600, 1.35, 0), (2.6, 360, 560, 1.3, 0), (tcl - .3, 360, 520, 1.15, 0), (tcl + .5, 360, 440, .95, 0), (sc.dur, 360, 440, 1.05, 0))
    sc.hit(2.4, 'ding')
def s_week3(sc):
    c = sc.cue; sc.bg((80, 110, 150), (50, 70, 110), .2); tt = c('তৃতীয়')
    for i, (y, col) in enumerate(((330, (226, 234, 246)), (450, (226, 234, 246)), (570, CORAL))):
        t0 = .15 + .3 * i
        sc.add(('rr', 560, 90, col, 14, 1), 360, y, z=1, anim=comb(enter(t0, 'left', .3, 200), (lambda t, i=i: dict(s=1 + .05 * eo(ramp(t, tt, tt + .3)), dx=0) if i == 2 else {})))
        sc.add(('text', 'সপ্তাহ ' + bn(i + 1), 46, INK if i < 2 else WHITE, 0, INK), 360, y, z=1.02, anim=enter(t0 + .1, 'fade'))
    sc.add(('cloud', (36, 40, 70), 380), 360, 160, z=1.15, s_=1.6, anim=lambda t: dict(dx=lerp(500, 0, eo(ramp(t, 0, 1.0))) + 10 * math.sin(t * 2)))
    img(sc, ('bolt',), 300, 260, t0=c('পরীক্ষাটা'), kind='pop', d=.12, z=1.2, s=1.2, t1=c('পরীক্ষাটা') + .35)
    sc.cam((0, 360, 330, 1.0, -4), (tt - .3, 360, 450, 1.0, 0), (tt + .3, 360, 570, 1.5, 3), (sc.dur, 360, 570, 1.7, 0))
    sc.flash(c('পরীক্ষাটা'), .3, (255, 255, 200), .7); sc.shake(c('পরীক্ষাটা'), .4, 12); sc.hit(c('পরীক্ষাটা'), 'thunder')
def s_rare(sc):
    c = sc.cue; sc.bg((226, 214, 240), (180, 160, 210), .2); tb = c('বিরল')
    sc.add(('wall', 1000, 1300, (232, 222, 246)), 500, 470, z=.35)
    chr_(sc, 'zahid', 600, 880, z=.95, s=.8, expr='neutral', ex=[(tb, 'think')], lk=[(0, -1)])
    sc.add(('counter', 300, 160), 600, 830, z=1.05)
    chr_(sc, 'cust2', 320, 880, z=1.05, s=1.0, expr='neutral', pose='hold', ex=[(tb, 'smug')], walk=walk_fn(.1, 1.0), anim=lambda t: dict(dx=lerp(500, 0, eo(ramp(t, .1, 1.0)))))
    img(sc, lambda t: ('phone', 'rare', 84, 0), 320, 710, t0=.9, z=1.15, s=.8, anim=lambda t: dict(dx=lerp(500, 0, 1) * 0))
    sc.add(('burst', (255, 230, 120), 70, 8), 320, 700, z=1.1, a=.0, t0=tb - .1, anim=lambda t: dict(rot=t * 90, s=1 + .2 * math.sin(t * 10), a=.8 * ramp(t, tb - .1, tb + .1)))
    sc.cam((0, 450, 500, 1.0, 2), (1.1, 330, 500, 1.15, 0), (tb, 330, 640, 1.5, 0), (sc.dur, 320, 700, 2.1, -2))
    sc.hit(tb + .1, 'ding'); sc.flash(tb + .1, .3, (230, 200, 255), .5)
def s_seventy(sc):
    c = sc.cue; sc.bg((70, 20, 30), (36, 12, 24), .2); tl = c('সত্তর') + .25
    val = lambda t: lerp(0, 70, eo(ramp(t, .05, tl)))
    t50 = next(t / 100 for t in range(0, 300) if val(t / 100) >= 50)
    sc.add(('rr', 580, 70, (255, 240, 220), 18, 1), 360, 560, z=1)
    sc.add(lambda t: ('rr', max(int(560 * val(t) / 80), 4), 50, (220, 70, 60) if val(t) > 50 else GREEN, 10, 0), 80 + 10, 560, z=1.02, anchor=(0, .5))
    sc.add(('rr', 8, 100, INK, 2, 0), 90 + 350, 560, z=1.05); txt(sc, bn(50), 440, 470, size=44, fill=WHITE, stroke=4, z=1.05)
    sc.add(lambda t: ('text', bn(int(val(t))), 230, WHITE if val(t) < 50 else (255, 90, 80), 11, INK), 360, 300, z=1, fixed=True, anim=lambda t: dict(s=1 + (.3 * (1 - eo((t - tl) / .35)) ** 2 if t > tl else 0)))
    img(sc, lambda t: ('stopw', int(val(t) * 6) % 360, 70, 1 if val(t) > 50 else 0), 360, 760, t0=0, z=1, s=1.2, anim=lambda t: dict(dx=6 * math.sin(t * 50) * (val(t) > 50)))
    sc.cam((0, 360, 470, 1.0, 0), (t50 - .05, 360, 470, 1.0, 0), (t50 + .1, 440, 520, 1.3, -3, eo), (tl - .1, 400, 480, 1.2, 0), (tl + .1, 360, 480, 1.45, 3, eo), (sc.dur, 360, 480, 1.35, 0))
    sc.flash(t50, .3, (255, 60, 50), .6); sc.shake(t50, .3, 14); sc.hit(t50, 'alarm'); sc.shake(tl, .5, 20); sc.hit(tl, 'big'); sc.flash(tl, .3, (255, 255, 255), .6)
def s_giveback(sc):
    c = sc.cue; sc.bg((220, 236, 214), (170, 204, 170), .2); ta = c('অর্ধেক') - .1; th = c('হাতে')
    sc.add(('wall', 1000, 1300, (230, 244, 226)), 500, 470, z=.35)
    chr_(sc, 'cust2', 190, 880, s=.9, expr='neutral', ex=[(th + .8, 'happy')], pose='down', po=[(th + .3, 'give')])
    chr_(sc, 'zahid', 530, 880, s=.9, expr='sad', ex=[(c('অর্ধেক'), 'neutral')], pose='give', po=[(th + 1.2, 'talk')], talk=[(c('ভাই') - .05, sc.dur - .15)])
    sc.add(('counter', 220, 150), 360, 835, z=1.05)
    img(sc, ('phone', 'ok', 70, 0), 470, 730, t0=.1, z=1.15, s=.75, anim=lambda t: dict(dx=-eio(ramp(t, th, th + .9)) * 280))
    sc.add(('tag', 0, 'শ্রম', MUST), 360, 330, z=1.1, s_=1.2, t0=c('শ্রমের') - .2, t1=ta, anim=enter(c('শ্রমের') - .2, 'down', .3, 150))
    sc.add(('tag', 1, 'শ্রম', MUST), 360, 330, z=1.1, s_=1.2, t0=ta, anim=lambda t: dict(dx=-16 * eo(ramp(t, ta, ta + .3)), rot=-5 * eo(ramp(t, ta, ta + .3))))
    sc.add(('tag', 2, 'শ্রম', MUST), 360, 330, z=1.1, s_=1.2, t0=ta, anim=lambda t: dict(dx=40 * eo(ramp(t, ta, ta + .5)), dy=300 * ramp(t, ta + .1, ta + 1) ** 2, rot=35 * ramp(t, ta, ta + 1), a=1 - ramp(t, ta + .6, ta + 1)))
    sc.cam((0, 360, 500, 1.0, 0), (th, 360, 500, 1.1, 0), (th + 1.0, 500, 500, 1.2, -1), (ta - .3, 480, 440, 1.2, 0), (ta + .2, 380, 400, 1.45, 2), (sc.dur, 370, 400, 1.3, 0))
    sc.hit(ta + .1, 'slice')
def s_shock(sc):
    c = sc.cue; sc.bg((255, 226, 190), (250, 190, 150), .2); ts = c('অবাক'); tn = c('মাথা')
    sc.add(('wall', 1000, 1300, (255, 234, 206)), 500, 470, z=.35)
    chr_(sc, 'cust2', 220, 880, z=1.05, s=1.0, expr='neutral', ex=[(ts, 'shock'), (tn, 'happy')], talk=[(c('আপনি') - .05, tn - .4)])
    chr_(sc, 'zahid', 570, 880, z=1.0, s=.9, expr='neutral', ex=[(tn - .1, 'happy')], anim=lambda t: dict(dy=7 * max(0, math.sin((t - tn) * 9)) * (tn < t < tn + 1.0) * -1))
    sc.add(('counter', 220, 150), 570, 840, z=1.06)
    for i, (x, y, r) in enumerate(((100, 330, -20), (330, 260, 10), (60, 480, -30))):
        img(sc, ('text', '!', 120, MUST, 8, INK), x, y, t0=ts + .05 * i, z=1.3, rot=r, d=.2, t1=ts + 1.5)
    img(sc, ('bubble', 'আপনি নিজে থেকেই\nকমাচ্ছেন?', 32, 'bl'), 300, 340, t0=c('আপনি') - .1, z=1.15, anim=bob(3, 2), t1=tn - .1)
    sc.cam((0, 300, 500, 1.0, 0), (ts - .05, 280, 500, 1.05, 0), (ts + .1, 230, 440, 1.5, -3, eo), (c('আপনি') + .5, 250, 470, 1.25, 0), (tn - .3, 400, 500, 1.1, 0), (tn + .6, 560, 520, 1.5, 0), (sc.dur, 560, 520, 1.6, 0))
    sc.shake(ts, .4, 14); sc.hit(ts, 'hit')
def s_brother(sc):
    c = sc.cue; sc.bg((255, 214, 170), (240, 180, 130), .2); tb = c('ভাইকে')
    sc.add(('skyline', (230, 170, 130), 1000, 300, 12), 400, 700, z=.4)
    sc.add(('shop', 'small'), 560, 620, z=1, s_=1.0)
    chr_(sc, 'cust2', 330, 880, z=1.05, s=.95, expr='happy', walk=walk_fn(.2, 1.3), anim=lambda t: dict(dx=lerp(500, 0, eo(ramp(t, .2, 1.3)))))
    chr_(sc, 'bro', 150, 880, z=1.1, s=.85, expr='happy', walk=walk_fn(tb - .2, tb + .9), anim=lambda t: dict(dx=lerp(-400, 0, eo(ramp(t, tb - .2, tb + .9))), a=ramp(t, tb - .2, tb - .1)))
    img(sc, ('text', '+১', 110, GREEN, 8, INK), 150, 380, t0=tb + .9, z=1.2, d=.25)
    sc.cam((0, 780, 470, 1.0, -2), (1.2, 480, 470, 1.15, 0), (tb, 300, 480, 1.1, 0), (sc.dur, 280, 480, 1.3, 0))
    sc.hit(tb + .9, 'ding')
def s_learn(sc):
    c = sc.cue; sc.bg((226, 232, 246), (180, 190, 220), .2); tp = c('প্রতিশ্রুতির'); td = c('দ্রুত')
    def th(t): return lerp(0, -7, eob(ramp(t, td, td + .5))) + lerp(0, 24, eio(ramp(t, tp + .35, tp + .7)))
    def pos(t, s):
        a = math.radians(th(t)); return 360 + s * 200 * math.cos(a), 300 + s * 200 * math.sin(a)
    sc.add(('scalepost',), 360, 580, z=1, anchor=(.5, .5))
    sc.add(('beam', 460), 360, 300, z=1.02, anim=lambda t: dict(rot=th(t)))
    for s_, lab, col, w, t0, size in ((-1, 'দ্রুত', MINT, 160, td - .1, 30), (1, 'প্রতিশ্রুতি', CORAL, 250, tp - .1, 28)):
        def an(t, s_=s_, t0=t0):
            x, y = pos(t, s_); drop = (1 - eo(ramp(t, t0, t0 + .35))) * -500 if s_ == 1 else 0
            return dict(dx=x - 360 - (0), dy=y - 300 + drop, a=ramp(t, t0, t0 + .05))
        sc.add(('pan', lab, w, col, INK if col != CORAL else WHITE, size), 360, 300, z=1.05, anchor=(.5, .0), anim=an)
    chr_(sc, 'zahid', 130, 900, s=.6, expr='think', ex=[(c('নিজের'), 'happy')], lk=[(0, 1)])
    sc.cam((0, 360, 470, 1.0, 0), (tp - .1, 360, 470, 1.05, 0), (tp + .3, 380, 420, 1.35, 1, eo), (sc.dur, 360, 430, 1.25, 0))
    sc.hit(tp + .35, 'big'); sc.shake(tp + .35, .5, 14)
def s_book(sc):
    c = sc.cue; sc.bg((60, 50, 90), (34, 30, 60), .2); tg = c('গুরুত্বপূর্ণ')
    sc.add(('rays', 300, 14), 360, 470, z=.35, s_=2.4, a=.4, anim=lambda t: dict(rot=t * 6))
    sc.add(('book',), 360, 480, z=1, s_=1.5, anim=comb(enter(.15, 'down', .4, 500), lambda t: dict(rot=-4 + 4 * eo(ramp(t, .1, 1.0)), dy=4 * math.sin(t * 2)) if t > .1 else {}))
    sc.add(('rr', 40, 110, MUST, 8, 1), 480, 660, z=1.1, t0=c('শিক্ষা') - .2, anim=enter(c('শিক্ষা') - .2, 'down', .3, 140))
    img(sc, ('burst', (255, 230, 120), 90, 9), 360, 380, t0=tg, kind='pop', z=1.2, s=1.4, a=.9, t1=tg + 1.2, anim=lambda t: dict(rot=t * 60))
    sc.cam((0, 360, 470, 1.4, -5), (.9, 360, 470, 1.05, 0), (tg, 360, 460, 1.1, 0), (tg + .2, 360, 440, 1.4, 2, eo), (sc.dur, 360, 450, 1.3, 0))
    sc.hit(.35, 'hit'); sc.shake(.35, .3, 10); sc.flash(tg, .3, (255, 230, 140), .4)
def s_claims(sc):
    c = sc.cue; sc.bg((190, 226, 250), (230, 244, 255), .2); td = c('দাবি')
    sc.add(('cloud', (255, 255, 255), 300), 150, 220, z=.4, s_=1.2, anim=lambda t: dict(dx=t * 8)); sc.add(('cloud', (255, 255, 255), 300), 600, 640, z=.5, s_=1.0, anim=lambda t: dict(dx=-t * 6))
    for i, (w, x, col) in enumerate((('ভালো', 150, CORAL), ('সেরা', 360, LILAC), ('"দ্রুত"', 570, TEAL))):
        tt = c(w.strip('"')) - .1
        sc.add(('balloon', w.strip('"'), col, 0), x, 560, z=1, s_=1.15, anim=lambda t, tt=tt, i=i: dict(dy=lerp(500, 0, eo(ramp(t, tt, tt + .8))) + 12 * math.sin(t * 2 + i) - lerp(0, 900, ramp(t, td + 1.6, td + 2.8)) * (1), dx=10 * math.sin(t * 1.5 + i), a=ramp(t, tt, tt + .1)))
    stamp(sc, 'দাবি', 360, 480, td - .1, size=190, fill=RED, rot=-14, z=1.3)
    sc.cam((0, 360, 650, 1.0, 0), (td - .4, 360, 520, 1.05, 0), (td, 360, 480, 1.3, -3, eo), (sc.dur, 360, 450, 1.1, 0))
    sc.shake(td + .1, .45, 14); sc.hit(td + .1, 'stamp')
def s_numbers(sc):
    c = sc.cue; sc.bg((226, 238, 240), (190, 214, 220), .2); ts = c('সংখ্যা')
    for i, x in enumerate((150, 360, 570)):
        sc.add(('burst', (255, 255, 255), 80, 8), x, 480 - i % 2 * 30, z=1, anim=lambda t, i=i: dict(s=1 + 2 * ramp(t, i * .06, .35 + i * .06), a=1 - ramp(t, .2 + i * .06, .4 + i * .06)))
        sc.add(('balloon', '', (200, 200, 210), 0), x, 560, z=1, s_=1.15, t1=i * .06 + .02)
    sc.add(('rr', 330, 230, (84, 92, 110), 16, 1), 360, 500, z=1, anim=lambda t: dict(dy=-700 * (1 - eo(ramp(t, ts - .2, ts + .35))) + (-18 * abs(math.sin((t - ts - .35) * 12)) * math.exp(-(t - ts - .35) * 5) if t > ts + .35 else 0), a=ramp(t, ts - .2, ts - .1)))
    sc.add(('text', '৫০', 150, MUST, 9, INK), 360, 500, z=1.05, anim=lambda t: dict(dy=-700 * (1 - eo(ramp(t, ts - .2, ts + .35))) + (-18 * abs(math.sin((t - ts - .35) * 12)) * math.exp(-(t - ts - .35) * 5) if t > ts + .35 else 0), a=ramp(t, ts - .2, ts - .1)))
    sc.add(('rr', 520, 44, (255, 232, 160), 6, 1), 360, 700, z=1, t0=c('আপনি') - .3, anim=enter(c('আপনি') - .3, 'up', .3, 100))
    for i in range(14): sc.add(('rr', 4, 14 if i % 5 else 28, INK, 1, 0), 130 + i * 38, 696, z=1.02, t0=c('আপনি') - .1 + i * .02, anim=enter(c('আপনি') - .1 + i * .02, 'fade'))
    img(sc, ('check', GREEN, 120), 560, 380, t0=c('পারবেন') - .2, z=1.2, s=1.3)
    sc.cam((0, 360, 420, 1.0, 0), (ts + .3, 360, 480, 1.1, 0), (c('আপনি'), 360, 520, 1.2, 0), (sc.dur, 360, 560, 1.35, 0))
    sc.shake(ts + .35, .4, 16); sc.hit(ts + .35, 'big')
def s_takeaway(sc):
    c = sc.cue; sc.bg((250, 240, 214), (236, 220, 178), .2); tn = c('পরের') - .2; tw = c('ঘড়ি') - .2
    sc.add(('rr', 400, 320, (255, 232, 110), 8, 1), 360, 420, z=1, rot=-4, t1=tn + .3, anim=comb(enter(.1, 'down', .35, 400), leave(tn, .3, 'up', 700)))
    sc.add(('text', 'practical\ntakeaway', 56, INK, 0, INK), 360, 420, z=1.02, rot=-4, t1=tn + .3, anim=comb(enter(.3, 'fade'), leave(tn, .3, 'up', 700)))
    sc.add(('rr', 110, 34, (240, 240, 200), 3, 1), 360, 270, z=1.03, rot=-4, t1=tn + .3, anim=leave(tn, .3, 'up', 700))
    sc.add(('poster', 'সেরা\nসার্ভিস', 56, 0, 1, INK, (255, 250, 232), 260), 200, 400, z=1, s_=.9, t0=tn, anim=enter(tn + .1, 'left', .4, 500))
    sc.add(('poster', '৫০\nমিনিটে', 56, 0, 1, INK, (255, 250, 232), 260), 520, 400, z=1, s_=.9, t0=tn, anim=enter(tn + .25, 'right', .4, 500))
    img(sc, lambda t: ('stopw', int(lerp(0, 300, ramp(t, tw + .2, tw + 2.0)) // 6) * 6, 90, 0), 360, 650, t0=tw, kind='up', dist=300, z=1.1, s=1.0)
    img(sc, ('cross', RED, 130), 200, 400, t0=tw + 1.0, z=1.2, s=1.2)
    img(sc, ('check', GREEN, 140), 520, 400, t0=c('দেখতে') - .1, z=1.2, s=1.2)
    sc.cam((0, 360, 440, 1.2, -2), (tn, 360, 440, 1.2, 0), (tn + .5, 360, 500, .95, 0), (tw + 1.0, 250, 440, 1.25, 0), (c('দেখতে') - .2, 520, 440, 1.35, 1), (sc.dur, 440, 500, 1.1, 0))
    sc.hit(tw + 1.0, 'hit'); sc.hit(c('দেখতে') - .1, 'ding')
def s_stillwall(sc):
    c = sc.cue; sc.bg((255, 226, 176), (240, 192, 130), .2); tp = c('পার্থক্য'); te = c('এখন')
    sc.add(('wall', 1000, 1300, (250, 220, 170)), 500, 470, z=.35)
    sc.add(('rays', 300, 14), 360, 300, z=.5, s_=2.4, a=.4, anim=lambda t: dict(rot=t * 6))
    img(sc, lambda t: ('clock', int(t * 6) % 360 + 120, 100, 120, 'wall', (int(t) * 6) % 360), 360, 300, t0=-99, z=.9, s=1.4)
    chr_(sc, 'zahid', 360, 880, s=1.0, expr='neutral', sil=(150, 150, 165), flip=True, z=1.0,
         anim=lambda t: dict(dx=-lerp(0, 320, ramp(t, tp, tp + 1.4)) * 1, a=ramp(t, tp - .3, tp) * (1 - ramp(t, tp + 1.0, te - .2))))
    chr_(sc, 'zahid', 360, 880, z=1.05, s=1.0, expr='happy', pose='hips', lk=[(0, 2)], anim=enter(te - .2, 'up', .4, 150))
    chr_(sc, 'cust3', 590, 770, z=1.0, s=.45, expr='happy', lk=[(0, 2)], anim=enter(te + .6, 'pop')); chr_(sc, 'cust4', 660, 770, z=1.0, s=.45, expr='happy', lk=[(0, 2)], anim=enter(te + .9, 'pop'))
    sc.cam((0, 360, 330, 1.6, 0), (tp - .2, 360, 360, 1.45, 0), (tp + .8, 360, 480, 1.05, 2), (te + .3, 360, 520, .95, 0), (sc.dur, 360, 470, 1.15, 0))
    sc.flash(te - .1, .3, (255, 235, 170), .45); sc.hit(te - .1, 'ding')
def s_claimpromise(sc):
    c = sc.cue; sc.bg((50, 50, 80), (28, 28, 52), .2); td = c('দাবি'); tp = c('প্রতিশ্রুতি')
    sc.add(('text', 'দ্রুত', 190, (150, 150, 170), 8, INK), 360, 330, z=1, t1=td + 1.3, anim=lambda t: dict(a=1 - ramp(t, td + .6, td + 1.2), dy=lerp(0, 300, ramp(t, td + .3, td + 1.2)) ** 1.0, rot=lerp(0, 22, ramp(t, td + .3, td + 1.2)), s=1 + .02 * math.sin(t * 40) * (td - .5 < t < td + .3)))
    for i, (x, y) in enumerate(((320, 330), (420, 330))): sc.add(('rr', 6, 130, (255, 255, 255), 0, 0), x + i * 10, y, z=1.02, rot=18 - i * 30, t0=td - .1, t1=td + .5)
    ct = c('আর') - .1
    sc.add(('rays', 300, 14), 360, 520, z=.4, s_=2.4, a=.5, t0=tp, anim=lambda t: dict(rot=t * 20))
    img(sc, ('clock', 120, 100, 150, 'neon', -1), 360, 520, t0=c('আর') - .1, z=.8, s=1.8, a=.45)
    sc.add(('burst', (255, 214, 80), 150, 12), 360, 520, z=1, s_=1.8, t0=c('পঞ্চাশ') - .1, anim=lambda t: dict(rot=t * 25, a=ramp(t, c('পঞ্চাশ') - .1, c('পঞ্চাশ') + .1)))
    stamp(sc, 'পঞ্চাশ\nমিনিট', 360, 520, c('পঞ্চাশ') - .15, size=124, fill=(255, 240, 150), rot=-4, z=1.2)
    sc.cam((0, 360, 330, 1.3, 0), (td + .4, 360, 380, 1.0, 0), (c('পঞ্চাশ') - .2, 360, 480, .95, 0), (c('পঞ্চাশ') + .1, 360, 520, 1.35, 3, eo), (sc.dur, 360, 520, 1.15, 0))
    sc.shake(td + .1, .3, 10); sc.hit(td + .1, 'crack'); sc.shake(tp - .1, .5, 20); sc.flash(tp - .1, .4, (255, 220, 100), .75); sc.hit(tp - .1, 'big')
def s_cta(sc):
    c = sc.cue; sc.bg(NAVY, (30, 90, 110), .2); tf = c('follow')
    sc.add(('rays', 300, 14), 360, 420, z=.4, s_=2.2, a=.3, anim=lambda t: dict(rot=t * 10))
    img(sc, lambda t: ('clock', int(t * 36) % 360, 200, 70, 'neon', (int(t) * 6) % 360), 600, 220, t0=.2, z=.7, s=1.0)
    sc.add(('rr', 460, 250, WHITE, 28, 1), 360, 430, z=1, anim=enter(.1, 'pop'))
    sc.add(('text', 'follow করুন', 52, INK, 0, INK), 360, 380, z=1.02, anim=enter(.3, 'fade'))
    sc.add(lambda t: ('rr', 300, 70, GREEN if t > tf + .6 else CORAL, 35, 1), 360, 490, z=1.02, anim=lambda t: dict(s=1 - .08 * math.exp(-abs(t - tf - .6) * 18)))
    sc.add(lambda t: ('text', '✓' if False else ('ফলো করছেন' if t > tf + .6 else 'Follow'), 36, WHITE, 0, INK), 360, 490, z=1.04)
    img(sc, ('ring', 40, WHITE, 6), 420, 520, t0=tf + .6, kind='pop', z=1.3, d=.3, t1=tf + 1.1, s=1.5)
    sc.add(('hand',), 420, 640, z=1.3, anchor=(.4, .05), anim=lambda t: dict(dy=-lerp(0, 120, eo(ramp(t, tf + .1, tf + .6))) + lerp(0, 40, ramp(t, tf + .6, tf + .9)), a=ramp(t, tf - .3, tf), s=1.4))
    chr_(sc, 'zahid', 130, 900, s=.75, expr='happy', pose='wave', z=1.1, anim=enter(.4, 'left', .4, 200))
    for i, (x, y) in enumerate(((580, 340), (630, 260), (540, 250))):
        img(sc, ('burst', CORAL, 36, 8), x, y, t0=tf + .7 + i * .1, z=1.2, d=.3, t1=tf + 1.6)
    sc.cam((0, 360, 470, 1.0, 0), (tf + .6, 360, 480, 1.1, 0), (sc.dur, 380, 480, 1.25, 0))
    sc.hit(tf + .6, 'ding'); sc.flash(tf + .6, .3, (150, 255, 200), .35)
FUNCS_B = [s_ten, s_chart, s_strike, s_write, s_half, s_six, s_week3, s_rare, s_seventy, s_giveback, s_shock, s_brother, s_learn, s_book, s_claims, s_numbers, s_takeaway, s_stillwall, s_claimpromise, s_cta]
FUNCS = FUNCS_A + FUNCS_B
