# Step 2: render frames (skia) and pipe to ffmpeg. Usage: s02_render.py <start_frame> <end_frame> <out.mp4> | s02_render.py --still t1 t2 ...
import sys, json, math, subprocess
import skia
from v_lib import *
from v_props import *
from v_scenes1 import *
from v_scenes2 import *

FPS = 30
TR = 0.42  # transition length
TM = json.load(open("timing.json"))
SENT = TM["sentences"]
DUR = TM["duration"]

# (name, first sentence, last sentence, function)
TIMELINE = [
    ("hook", 0, 0, sc_hook), ("fortune", 1, 1, sc_shop_fortune), ("rent", 2, 2, sc_rent), ("mirpur", 3, 3, sc_mirpur),
    ("father", 4, 4, sc_father), ("oldclock", 5, 5, sc_clock_old), ("tries", 6, 6, sc_tries), ("untimed", 7, 7, sc_untimed),
    ("adold", 8, 8, sc_ad_old), ("fastq", 9, 9, sc_fast_q), ("daily", 10, 10, sc_daily), ("talk", 11, 13, sc_counter_talk),
    ("noans", 14, 14, sc_no_answer), ("leave", 15, 15, sc_leave), ("girl", 16, 16, sc_girl_arrive), ("exam", 17, 17, sc_exam),
    ("notes", 18, 18, sc_notes), ("crack", 19, 19, sc_cracked), ("ask", 20, 21, sc_girl_ask), ("retort", 22, 22, sc_girl_retort),
    ("think", 23, 23, sc_zahid_think), ("realize", 24, 24, sc_realize), ("wantback", 25, 25, sc_want_back),
    ("night", 26, 26, sc_night_clock), ("ten", 27, 27, sc_ten_phones), ("notebook", 28, 28, sc_notebook),
    ("chart", 29, 30, sc_chart), ("strike", 31, 31, sc_strike), ("newbanner", 32, 33, sc_new_banner),
    ("six", 34, 34, sc_six), ("noprice", 35, 35, sc_no_price), ("waitclock", 36, 36, sc_wait_clock),
    ("week3", 37, 37, sc_week3), ("rare", 38, 38, sc_rare), ("seventy", 39, 39, sc_seventy),
]


class Ctx:
    def __init__(self, t0, t1, a, b):
        self.t0, self.t1, self.a, self.b = t0, t1, a, b

    def st(self, si):
        return SENT[si]["ws"] - self.t0

    def w(self, si, wi):
        ws = SENT[si]["words"]
        wi = max(0, min(wi, len(ws) - 1))
        return ws[wi]["start"] - self.t0


SCENES = []
for (name, a, b, fn) in TIMELINE:
    t0 = SENT[a]["start"]
    t1 = SENT[b]["end"]
    SCENES.append(dict(name=name, t0=t0, t1=t1, fn=fn, ctx=Ctx(t0, t1, a, b)))
for i, s in enumerate(SCENES):  # make scenes contiguous
    if i + 1 < len(SCENES):
        s["t1"] = SCENES[i + 1]["t0"]
    s["D"] = s["t1"] - s["t0"]
    s["ctx"].t1 = s["t1"]


def scene_at(t):
    for i, s in enumerate(SCENES):
        if s["t0"] <= t < s["t1"]:
            return i
    return len(SCENES) - 1


def run_scene(c, i, lt):
    s = SCENES[i]
    c.save()
    c.clipRect(skia.Rect.MakeWH(W, H))
    try:
        s["fn"](c, lt, s["D"], s["ctx"])
    finally:
        c.restore()


# ------------------------------------------------------------ captions
def build_chunks():
    chunks = []
    for d in SENT:
        words = d["words"]
        if d["i"] == len(SENT) - 1:  # truncated sentence: spread words over the remaining audio
            n = len(words)
            for k, w in enumerate(words):
                w["start"] = d["ws"] + (d["end"] - d["ws"]) * 0.8 * k / n
        cur = []
        for w in words:
            test = [x["w"] for x in cur] + [w["w"]]
            if cur and len(wrap_words(test, 62, 900)) > 2:
                chunks.append(cur)
                cur = []
            cur.append(w)
        if cur:
            chunks.append(cur)
    out = []
    for k, ch in enumerate(chunks):
        t_start = max(0.0, ch[0]["start"] - 0.05)
        t_end = chunks[k + 1][0]["start"] - 0.05 if k + 1 < len(chunks) else DUR
        t_end = min(t_end, ch[-1]["end"] + 0.6)
        out.append(dict(ts=t_start, te=t_end, words=ch))
    return out


CHUNKS = build_chunks()


def draw_caption(c, t):
    ch = None
    for x in CHUNKS:
        if x["ts"] <= t < x["te"]:
            ch = x
            break
    if ch is None:
        return
    size = 62
    words = [w["w"] for w in ch["words"]]
    lines = wrap_words(words, size, 900)
    lh = size * 1.32
    bw = max(text_w(" ".join(l), size) for l in lines) + 90
    bh = len(lines) * lh + 46
    a = clamp(prog(t, ch["ts"], ch["ts"] + 0.12))
    cy = 1650
    yoff = (1 - ease_out(a)) * 18
    c.save()
    c.translate(0, yoff)
    rrect(c, W / 2 - bw / 2, cy - bh / 2, bw, bh, 36, fill("#2B1D14", 0.78 * a))
    k = 0
    for li, l in enumerate(lines):
        y = cy - bh / 2 + 23 + size * 0.98 + li * lh
        lw = text_w(" ".join(l), size)
        x0 = W / 2 - lw / 2
        for j, wd in enumerate(l):
            pre = text_w(" ".join(l[:j]) + " ", size) if j else 0
            wt = ch["words"][k]
            active = wt["start"] - 0.02 <= t
            nxt = ch["words"][k + 1]["start"] if k + 1 < len(ch["words"]) else 1e9
            cur = active and t < nxt
            draw_text(c, wd, x0 + pre, y, size, "#F2C14B" if cur else "#FFF3D6", "b", "l", a=a)
            k += 1
    c.restore()


# ------------------------------------------------------------ frame composition
def draw_frame(c, t):
    i = scene_at(t)
    s = SCENES[i]
    lt = t - s["t0"]
    if i > 0 and lt < TR:
        p = lt / TR
        e = ease(p)
        mode = i % 3
        prev = SCENES[i - 1]
        plt = prev["D"] + lt
        if mode == 0:  # circular iris
            run_scene(c, i - 1, plt)
            c.save()
            path = skia.Path()
            path.addCircle(W / 2, H / 2, e * 1300)
            c.clipPath(path, skia.ClipOp.kIntersect, True)
            run_scene(c, i, lt)
            c.restore()
            c.drawCircle(W / 2, H / 2, e * 1300, stroke("#FFF3D6", 14 * (1 - p)))
        elif mode == 1:  # push from the right
            c.save(); c.translate(-W * 0.35 * e, 0); run_scene(c, i - 1, plt); c.restore()
            c.save(); c.translate(W * (1 - e), 0)
            rect(c, -30, 0, 30, H, fill("#2B1D14"))
            run_scene(c, i, lt); c.restore()
        else:  # wipe up from bottom
            run_scene(c, i - 1, plt)
            c.save(); c.clipRect(skia.Rect.MakeXYWH(0, H * (1 - e), W, H)); run_scene(c, i, lt); c.restore()
            rect(c, 0, H * (1 - e) - 10, W, 14, fill("#F2C14B"))
    else:
        run_scene(c, i, lt)
    # global grade: subtle warm vignette
    vignette(c, 0.22, "#2B1409")
    draw_caption(c, t)
    # fade in / out
    if t < 0.25:
        rect(c, 0, 0, W, H, fill("#000000", 1 - t / 0.25))
    if t > DUR - 0.55:
        rect(c, 0, 0, W, H, fill("#000000", clamp((t - (DUR - 0.55)) / 0.5)))


def main():
    if sys.argv[1] == "--still":
        out = sys.argv[2]
        ts = [float(x) for x in sys.argv[3:]]
        for tt in ts:
            surf = skia.Surface(W, H)
            c = surf.getCanvas()
            draw_frame(c, tt)
            surf.makeImageSnapshot().save(f"{out}_{tt:07.2f}.png")
        return
    f0, f1, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    ff = subprocess.Popen(["./ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", out],
                          stdin=subprocess.PIPE)
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    for f in range(f0, f1):
        t = f / FPS
        c.clear(skia.ColorBLACK)
        draw_frame(c, t)
        ff.stdin.write(surf.makeImageSnapshot().tobytes())
        if (f - f0) % 60 == 0:
            print(out, f, "/", f1, flush=True)
    ff.stdin.close()
    ff.wait()


if __name__ == "__main__":
    main()
