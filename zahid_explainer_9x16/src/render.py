import sys, os, json, math, subprocess, time, numpy as np
from PIL import Image, ImageFilter, ImageDraw
from engine import *
import engine
from scenes_b import FUNCS
T = json.load(open('/tmp/work/timing.json')); META = T['scenes']
TOTAL = 171.1543; NF = int(math.ceil(TOTAL * FPS)); CHUNK = 90
KINDS = ['whipL', 'zoomIn', 'whipR', 'whipU', 'zoomThru', 'whipL', 'whipR', 'zoomIn']
class Video:
    def __init__(s):
        s.sc = []; s.errs = []
        for i, (m, f) in enumerate(zip(META, FUNCS)):
            sc = Scene(m, i)
            try: f(sc)
            except Exception as e:
                import traceback; traceback.print_exc(); s.errs.append((m['id'], repr(e)))
            if sc.errs: s.errs.append((m['id'], 'unresolved cues: ' + ','.join(sc.errs)))
            s.sc.append(sc)
        s.cap = Captions(META)
        _a = np.clip((np.arange(H) - (WELL_Y - 50)) / 60.0, 0, 1) ** 1.5
        s.wa = _a.astype(np.float32)[:, None, None]
    def well(s, fr, col):
        arr = np.asarray(fr, np.float32); c = np.array(col, np.float32)[None, None, :]
        return Image.fromarray((arr * (1 - s.wa) + c * s.wa).astype(np.uint8))
    def stage(s, i, gt): return s.sc[i].render(gt - META[i]['start'])
    def trans(s, A, B, p, kind):
        e = eio(p); w = math.sin(math.pi * p)
        if kind.startswith('whip'):
            dx, dy = {'whipL': (-1, 0), 'whipR': (1, 0), 'whipU': (0, -1)}[kind]
            off = e * (W if dx else H)
            can = Image.new('RGB', (W, H)); can.paste(A, (int(dx * off), int(dy * off))); can.paste(B, (int(dx * off - dx * W), int(dy * off - dy * H)))
            arr = np.asarray(can, np.float32); k = int(2 + 22 * w); ax = 1 if dx else 0
            acc = np.zeros_like(arr); n = 9
            for sft in np.linspace(-k, k, n): acc += np.roll(arr, int(sft), axis=ax)
            return Image.fromarray((acc / n).astype(np.uint8))
        zin = lambda im, z: im.crop((int(CX - CX / z), int(CY - CY / z), int(CX + (W - CX) / z), int(CY + (H - CY) / z))).resize((W, H), Image.BILINEAR)
        if kind == 'zoomIn': za, zb = 1 + 2.2 * e, .55 + .45 * e
        else: za, zb = 1 + 1.4 * e, 1.9 - .9 * e
        a_ = zin(A, za)
        b_ = zin(B, zb) if zb >= 1 else B.resize((int(W * zb), int(H * zb)), Image.BILINEAR)
        if zb < 1:
            bb = Image.new('RGB', (W, H), B.getpixel((5, 5))); bb.paste(b_, (int(CX - CX * zb), int(CY - CY * zb))); b_ = bb
        m = eio(ramp(p, .3, .7)); out = Image.blend(a_, b_, m)
        out = out.filter(ImageFilter.GaussianBlur(1 + 7 * w))
        return Image.blend(out, Image.new('RGB', (W, H), (255, 255, 255)), .25 * w)
    def frame(s, gt):
        gt = min(gt, TOTAL - 1e-3)
        i = max(k for k in range(len(META)) if META[k]['start'] <= gt)
        wc = None; fr = None
        if i + 1 < len(META):
            tw = META[i + 1]['tw']; c = META[i + 1]['start']
            if gt > c - tw:
                p = (gt - (c - tw)) / (2 * tw); fr = s.trans(s.stage(i, gt), s.stage(i + 1, gt), p, KINDS[(i + 1) % 8]); wc = (i, i + 1, p)
        if fr is None and i > 0:
            tw = META[i]['tw']; c = META[i]['start']
            if gt < c + tw:
                p = (gt - (c - tw)) / (2 * tw); fr = s.trans(s.stage(i - 1, gt), s.stage(i, gt), p, KINDS[i % 8]); wc = (i - 1, i, p)
        if fr is None: fr = s.stage(i, gt)
        c1 = darken(s.sc[i].bgc[1], .28)
        if wc: a, b, p = wc; ca = darken(s.sc[a].bgc[1], .28); cb = darken(s.sc[b].bgc[1], .28); c1 = tuple(int(lerp(ca[k], cb[k], p)) for k in range(3))
        fr = s.well(fr, c1)
        r = s.cap.render(gt)
        if r:
            im, a = r
            if a < 1: im = im.copy(); im.putalpha(im.getchannel('A').point(lambda v: int(v * a)))
            fr.paste(im, (int(W / 2 - im.width / 2), 1040 - im.height // 2), im)
        return vignette(fr)
_V = None
def init():
    global _V; _V = Video()
def do_chunk(ci):
    out = f'/tmp/work/chunks/c{ci:04d}.mp4'
    if os.path.exists(out): return ci
    f0 = ci * CHUNK; f1 = min(NF, f0 + CHUNK)
    pr = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', '-pix_fmt', 'yuv420p', '-g', '30', '-bf', '0', '-f', 'mp4', out + '.tmp'], stdin=subprocess.PIPE)
    for f in range(f0, f1): pr.stdin.write(_V.frame(f / FPS).tobytes())
    pr.stdin.close(); pr.wait(); os.rename(out + '.tmp', out); return ci
def sheets():
    v = Video(); os.makedirs('/tmp/work/qa', exist_ok=True)
    print('ERRORS:', v.errs)
    tw, th = 160, 284; per = 8
    for sh in range(0, len(META), per):
        sheet = Image.new('RGB', (2 * 5 * tw + 20, 4 * (th + 14)), (30, 30, 30)); d = ImageDraw.Draw(sheet)
        for k, i in enumerate(range(sh, min(sh + per, len(META)))):
            m = META[i]; col, row = k // 4, k % 4
            for j, f in enumerate((.05, .25, .5, .75, .95)):
                gt = m['start'] + (m['end'] - m['start']) * f
                im = v.frame(gt).resize((tw, th)); sheet.paste(im, (col * (5 * tw + 20) + j * tw, row * (th + 14) + 14))
            d.text((col * (5 * tw + 20) + 2, row * (th + 14) + 1), f"{i+1} {m['id']} {m['start']:.1f}-{m['end']:.1f}", fill=(255, 255, 0))
        sheet.save(f'/tmp/work/qa/sheet{sh // per + 1}.png')
    print('sheets done')
def only(ids):
    v = Video(); print('ERRORS:', v.errs)
    for i in ids:
        m = META[i]; ims = []
        for f in (.1, .3, .5, .7, .9):
            ims.append(v.frame(m['start'] + (m['end'] - m['start']) * f).resize((288, 512)))
        sh = Image.new('RGB', (288 * 5, 512)); [sh.paste(im, (k * 288, 0)) for k, im in enumerate(ims)]; sh.save(f'/tmp/work/qa/scene{i+1}.png')
if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'qa': sheets()
    elif mode == 'only': only([int(x) - 1 for x in sys.argv[2:]])
    elif mode == 'render':
        from multiprocessing import Pool
        os.makedirs('/tmp/work/chunks', exist_ok=True)
        n = (NF + CHUNK - 1) // CHUNK; t0 = time.time(); done = 0
        with Pool(2, initializer=init) as pool:
            for ci in pool.imap_unordered(do_chunk, range(n)):
                done += 1; print(f'chunk {ci} done {done}/{n} elapsed {time.time()-t0:.0f}s', flush=True)
        print('ALLDONE', flush=True)
