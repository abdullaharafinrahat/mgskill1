# -*- coding: utf-8 -*-
"""STEP 3 - frame renderer. Usage:
   python render.py still T [T2 ...]     -> out/still_*.png + contact sheet
   python render.py all                  -> renders segments in parallel (out/seg_XXX.mp4)
"""
import sys, os, math, subprocess, glob
import numpy as np
import skia
from common import *
from gfx import *
from textkit import draw_text, text_width

import scenes_1, scenes_2, scenes_3

SCENES = {}
for m in (scenes_1, scenes_2, scenes_3):
    SCENES.update(m.SCENES)

TD = 0.5                                    # transition length
TRANS = {1: 'iris', 2: 'push', 3: 'iris', 4: 'push', 5: 'iris', 6: 'wipe', 7: 'push', 8: 'iris', 9: 'push',
         10: 'iris', 11: 'wipe', 12: 'push', 13: 'iris'}
T = None


def load():
    global T
    if T is None:
        T = Timeline()
    return T


def scene_at(t):
    tl = load()
    for k in sorted(tl.scenes):
        if t < tl.scenes[k]['end'] or k == max(tl.scenes):
            return k
    return 1


def draw_scene(c, k, t):
    c.save()
    c.clipRect(skia.Rect.MakeWH(W, H))
    SCENES[k](c, t, load())
    c.restore()


def world(c, t):
    tl = load()
    k = scene_at(t)
    kmax = max(tl.scenes)
    nxt = k + 1 if k < kmax else None
    tb = tl.scenes[k]['end']
    prv = k - 1 if k > 1 else None
    ta = tl.scenes[k]['start']
    if nxt and t > tb - TD / 2:
        p = prv_p = (t - (tb - TD / 2)) / TD
        kind = TRANS.get(k, 'iris')
        e = ease_io(p)
        draw_scene(c, k, t)
        c.save()
        if kind == 'iris':
            path = skia.Path(); path.addCircle(W / 2, H * .45, e * 1700)
            c.clipPath(path, doAntiAlias=True)
        elif kind == 'push':
            c.translate(W * (1 - e), 0)
            c.clipRect(skia.Rect.MakeWH(W, H))
            c.drawRect(skia.Rect.MakeLTRB(-30, 0, 0, H), fill('#000000', .5))
        elif kind == 'wipe':
            path = skia.Path(); off = (1 - e) * (H + 700)
            path.moveTo(0, H - off); path.lineTo(W, H - off - 300); path.lineTo(W, H + 10); path.lineTo(0, H + 10); path.close()
            # bottom-up diagonal reveal
            path = skia.Path()
            y0 = H - e * (H + 360)
            path.moveTo(0, y0 + 360); path.lineTo(W, y0); path.lineTo(W, H + 400); path.lineTo(0, H + 400); path.close()
            c.clipPath(path, doAntiAlias=True)
        draw_scene(c, nxt, t)
        c.restore()
        if kind == 'push':
            c.save(); c.translate(-W * e * 0.3, 0); c.restore()
        if kind == 'iris':
            c.drawCircle(W / 2, H * .45, e * 1700, stroke('#ffe9b0', 10 * (1 - e) + 2, 0.8 * (1 - p)))
        return
    draw_scene(c, k, t)


def captions(c, t):
    tl = load()
    chunks = tl.chunks
    cur = None
    for i, ch in enumerate(chunks):
        nxt_start = chunks[i + 1]['start'] if i + 1 < len(chunks) else tl.duration + 1
        if ch['start'] - 0.03 <= t < max(min(nxt_start, ch['end'] + 0.45), ch['start'] + 0.7):
            cur = ch
            break
    if not cur:
        return
    text = cur['text']
    size = 66
    maxw = 930
    words = text.split(' ')
    lines, cl = [], []
    for w_ in words:
        trial = ' '.join(cl + [w_])
        if text_width(trial, size) <= maxw or not cl:
            cl.append(w_)
        else:
            lines.append(cl); cl = [w_]
    if cl:
        lines.append(cl)
    lh = size * 1.5
    total_h = lh * len(lines)
    bw = max(text_width(' '.join(l), size) for l in lines) + 70
    cy = 1500
    age = t - cur['start']
    sc = back_out(age / 0.18) if age < 0.18 else 1.0
    c.save()
    c.translate(W / 2, cy); c.scale(0.85 + 0.15 * sc, 0.85 + 0.15 * sc)
    c.drawRoundRect(skia.Rect.MakeXYWH(-bw / 2 + 5, -total_h / 2 - 10 + 8, bw, total_h + 20), 34, 34, blur_paint('#000000', 10, .4))
    rrect(c, -bw / 2, -total_h / 2 - 10, bw, total_h + 20, 34, fill('#1a0f09', 0.74))
    c.drawRoundRect(skia.Rect.MakeXYWH(-bw / 2, -total_h / 2 - 10, bw, total_h + 20), 34, 34, stroke('#ffd24a', 3, .55))
    allw = [w_ for l in lines for w_ in l]
    tot = sum(len(w_) + 1 for w_ in allw)
    dur = max(cur['end'] - cur['start'], 0.35)
    f = (t - cur['start']) / dur
    acc = 0
    spw = text_width(' ', size)
    for li, l in enumerate(lines):
        lw = text_width(' '.join(l), size)
        x = -lw / 2
        y = -total_h / 2 + lh * li + lh * 0.72
        for w_ in l:
            a0 = acc / tot; acc += len(w_) + 1; a1 = acc / tot
            active = a0 <= f < a1
            col = '#ffd24a' if active else '#ffffff'
            ww = draw_text(c, w_, x, y, size, col, align='l', outline='#000000', outline_w=9, shadow=None)
            x += ww + spw
    c.restore()


def hud(c, t):
    tl = load()
    c.drawRect(skia.Rect.MakeXYWH(0, 0, W, 10), fill('#000000', .25))
    c.drawRect(skia.Rect.MakeXYWH(0, 0, W * t / tl.duration, 10), fill('#ffb43a'))


def frame(c, t):
    world(c, t)
    vignette(c, 0.35)
    captions(c, t)
    hud(c, t)


def new_surface():
    return skia.Surface(W, H)


def render_range(args):
    f0, f1, outfile = args
    load()
    surf = new_surface()
    c = surf.getCanvas()
    cmd = [FFMPEG, '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', '-pix_fmt', 'yuv420p', '-an', outfile]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(f0, f1):
        c.clear(skia.ColorBLACK)
        frame(c, f / FPS)
        arr = surf.makeImageSnapshot().toarray()
        pr.stdin.write(arr.tobytes())
    pr.stdin.close(); pr.wait()
    return outfile


def still(times):
    load()
    from PIL import Image
    ims = []
    for t in times:
        surf = new_surface(); c = surf.getCanvas(); c.clear(skia.ColorBLACK)
        frame(c, t)
        im = Image.fromarray(surf.makeImageSnapshot().toarray()[:, :, [2, 1, 0]])
        im.save(f'{OUT}/still_{t:.2f}.png')
        ims.append(im.resize((340, 604)))
    sheet = Image.new('RGB', (340 * len(ims), 604))
    for i, im in enumerate(ims):
        sheet.paste(im, (340 * i, 0))
    sheet.save(f'{OUT}/sheet.png')
    print('sheet', sheet.size)


def render_all(workers=4, seg_sec=6):
    from multiprocessing import Pool
    tl = load()
    total = int(math.ceil(tl.duration * FPS))
    seg = seg_sec * FPS
    jobs = []
    for i, f0 in enumerate(range(0, total, seg)):
        jobs.append((f0, min(total, f0 + seg), f'{OUT}/seg_{i:03d}.mp4'))
    for fpath in glob.glob(f'{OUT}/seg_*.mp4'):
        os.remove(fpath)
    with Pool(workers) as p:
        for r in p.imap_unordered(render_range, jobs):
            print('done', r, flush=True)


if __name__ == '__main__':
    if sys.argv[1] == 'still':
        still([float(x) for x in sys.argv[2:]])
    elif sys.argv[1] == 'all':
        render_all()
