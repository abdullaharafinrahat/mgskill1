"""Script 5: renderer - camera, transitions, captions, parallel encode.
usage:  python3 s5_render.py sheet T1 T2 ...      (contact sheet of frames, for checking)
        python3 s5_render.py full                  (render everything to /tmp/vid/out/video_silent.mp4 + final mp4)"""
import sys, os, json, math, subprocess, glob, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import skia
from s2_lib import *
from s4_scenes_a import SCENES_A
try:
    from s4_scenes_b import SCENES_B
except Exception as e:  # pragma: no cover
    print("scenes_b missing:", e); SCENES_B = {}

SC = {**SCENES_A, **SCENES_B}
OUT = "/tmp/vid/out/"; FF = "/tmp/vid/ffmpeg"; AUD = "/tmp/vid/audio_repo/audio01.mp3"
FPS = 30
TL = json.load(open(OUT + "timeline.json"))
DUR = TL["duration"]; SCN = TL["scenes"]
ENV = np.load(OUT + "env.npy")
TR = 0.5
TRANS = ["slide", "iris", "up", "diag", "iris", "slide", "up", "diag"]

def mouth(t):
    i = int(t * 60)
    e = float(np.mean(ENV[max(0, i - 2): i + 3])) if i < len(ENV) else 0.0
    return clamp((e - 0.06) * 1.8) * (0.45 + 0.55 * abs(math.sin(t * 19)))

_cap_cache = {}

def draw_scene(c, i, t):
    s = SCN[i]; fn, cam = SC[s["name"]]
    tl = max(0.0, t - s["start"]); d = s["end"] - s["start"]
    C = [ch["start"] - s["start"] for ch in s["chunks"]] + [d]
    C[0] = 0.0
    z, fx, fy = cam(tl, d, C)
    fx += 4 * math.sin(t * 0.8); fy += 3 * math.cos(t * 0.65)
    c.save(); c.translate(540, 700); c.scale(z, z); c.translate(-fx, -fy)
    fn(c, tl, d, C, mouth(t))
    c.restore()

def captions(c, t):
    for s in SCN:
        for ch in s["chunks"]:
            if ch["start"] <= t < ch["end"] or (ch is SCN[-1]["chunks"][-1] and t >= ch["start"]):
                lt = t - ch["start"]; p = prog(lt, 0, 0.22)
                size = 54
                lines = wrap(ch["text"], size, 840)
                h = len(lines) * size * 1.42 + 54; w = max(text_w(l, size) for l in lines) + 86
                bottom = 1740
                y0 = bottom - h
                with alpha_layer(c, p):
                    with xform(c, 540, y0 + h / 2 + (1 - ease_out(p)) * 24, 0.94 + 0.06 * ease_out(p)):
                        rect(c, -w / 2 + 4, -h / 2 + 8, w, h, "#000000", r=34, a=80, blur=8)
                        rect(c, -w / 2, -h / 2, w, h, "#1B1410", r=34, a=222)
                        rect(c, -w / 2, -h / 2, w, h, "#F4B942", r=34, a=255, stroke=3)
                        draw_lines(c, lines, 0, -h / 2 + 27 + size * 0.98, size, "#FFFFFF", lh=1.42)
                return

def transition_style(i):
    return TRANS[i % len(TRANS)]

def frame(c, t):
    c.clear(skia.ColorBLACK)
    i = 0
    for k, s in enumerate(SCN):
        if t >= s["start"] - 1e-9: i = k
    nxt = i + 1 if i + 1 < len(SCN) else None
    if nxt is not None and t > SCN[nxt]["start"] - TR:
        e = ease_io((t - (SCN[nxt]["start"] - TR)) / TR); st = transition_style(i)
        c.save()
        if st == "slide": c.translate(-e * 420, 0)
        draw_scene(c, i, t); c.restore()
        c.save()
        if st == "slide":
            c.clipRect(skia.Rect.MakeLTRB((1 - e) * W, 0, W, H)); c.translate((1 - e) * W, 0)
            rect(c, -30, 0, 30, H, "#000000", a=70, blur=10)
        elif st == "up":
            c.clipRect(skia.Rect.MakeLTRB(0, (1 - e) * H, W, H)); c.translate(0, (1 - e) * H)
        elif st == "iris":
            pth = skia.Path(); pth.addCircle(540, 760, e * 1700); c.clipPath(pth, doAntiAlias=True)
        elif st == "diag":
            pth = skia.Path(); k = (e * 1.6 - 0.3)
            pth.moveTo(0, 0); pth.lineTo(W * (k + 0.5) * 1.6, 0); pth.lineTo(W * (k - 0.5) * 1.6, H); pth.lineTo(0, H); pth.close()
            c.clipPath(pth, doAntiAlias=True)
        draw_scene(c, nxt, SCN[nxt]["start"]); c.restore()
        if st == "iris":
            circ(c, 540, 760, e * 1700, "#FFFFFF", 0 if e > 0.99 else 255, stroke=10)
    else:
        draw_scene(c, i, t)
    # vignette
    p = skia.Paint(); p.setShader(skia.GradientShader.MakeRadial((540, 900), 1250, [skia.ColorSetARGB(0, 0, 0, 0), skia.ColorSetARGB(90, 0, 0, 0)]))
    c.drawRect(skia.Rect.MakeWH(W, H), p)
    captions(c, t)
    rect(c, 0, 0, W * t / DUR, 8, "#F4B942")
    fo = prog(t, DUR - 0.8, 0.8)
    if fo > 0: rect(c, 0, 0, W, H, "#000000", a=int(255 * fo))

def to_bytes(surface):
    return surface.makeImageSnapshot().toarray().tobytes()

def render_range(args):
    a, b, path = args
    surf = skia.Surface(W, H); c = surf.getCanvas()
    p = subprocess.Popen([FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for f in range(a, b):
        frame(c, f / FPS)
        p.stdin.write(to_bytes(surf))
    p.stdin.close(); p.wait()
    return path

def sheet(times):
    from PIL import Image
    surf = skia.Surface(W, H); c = surf.getCanvas(); ims = []
    for t in times:
        frame(c, float(t))
        im = Image.frombuffer("RGBA", (W, H), surf.makeImageSnapshot().toarray().tobytes(), "raw", "BGRA", 0, 1).convert("RGB")
        ims.append(im.resize((360, 640)))
    cols = min(len(ims), 5); rows = (len(ims) + cols - 1) // cols
    sh = Image.new("RGB", (cols * 364, rows * 644), "white")
    for k, im in enumerate(ims): sh.paste(im, ((k % cols) * 364, (k // cols) * 644))
    sh.save(OUT + "sheet.png"); print("saved", sh.size)

def full():
    from multiprocessing import Pool
    n = int(math.ceil(DUR * FPS)); step = 120
    jobs = [(a, min(n, a + step), OUT + f"seg_{a // step:03d}.mp4") for a in range(0, n, step)]
    t0 = time.time()
    with Pool(4) as pool:
        for k, pth in enumerate(pool.imap(render_range, jobs)):
            print("done", pth, round(time.time() - t0), "s", flush=True)
    with open(OUT + "list.txt", "w") as f:
        for j in jobs: f.write(f"file '{j[2]}'\n")
    final = OUT + "zahid_50_minute_promise.mp4"
    subprocess.run([FF, "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", OUT + "list.txt", "-i", AUD, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-af", f"afade=t=out:st={DUR-0.7:.2f}:d=0.7", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", final], check=True)
    print("final", final, os.path.getsize(final))

if __name__ == "__main__":
    if sys.argv[1] == "sheet": sheet(sys.argv[2:])
    else: full()
