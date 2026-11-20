"""Script 7: compose frames (scenes + transitions + captions) and render in parallel chunks via ffmpeg pipes."""
import sys, os, subprocess, time
sys.path.insert(0, "/tmp/work")
from sets import *
import scenes_a, scenes_b, scenes_c
FPS = 30
S = sorted(SCENES, key=lambda s: s["start"])
for i, s in enumerate(S): s["end"] = S[i + 1]["start"] if i + 1 < len(S) else END; s["d"] = s["end"] - s["start"]

def draw_scene(c, s, g):
    c.save(); c.rectangle(0, 0, W, H); c.clip(); c.new_path()
    s["fn"](c, K(max(0.0, g - s["start"]) if g < s["start"] else g - s["start"], g, s["d"])); c.restore()

def scene_frame(c, g):
    i = max([j for j, s in enumerate(S) if s["start"] - 0.12 <= g] or [0]); s = S[i]
    w0 = s["start"] - 0.12
    if i > 0 and s["trans"] != "cut" and g < w0 + s["td"]:
        p = clamp((g - w0) / s["td"]); e = e_io(p); pv = S[i - 1]; tr = s["trans"]; kw = s["kw"]
        if tr == "push_l":
            c.save(); c.translate(-e * W, 0); draw_scene(c, pv, g); c.restore()
            c.save(); c.translate((1 - e) * W, 0); draw_scene(c, s, g); c.restore()
        elif tr == "push_u":
            c.save(); c.translate(0, -e * H); draw_scene(c, pv, g); c.restore()
            c.save(); c.translate(0, (1 - e) * H); draw_scene(c, s, g); c.restore()
        elif tr == "iris":
            draw_scene(c, pv, g); c.save(); c.new_path(); c.arc(kw.get("ix", W / 2), kw.get("iy", H / 2), e * 2300 + 1, 0, 2 * math.pi); c.clip(); draw_scene(c, s, g); c.restore()
            circ(c, kw.get("ix", W / 2), kw.get("iy", H / 2), e * 2300, None, (1, 1, 1, .6 * (1 - p)), 14)
        elif tr == "wipe":
            draw_scene(c, pv, g); x = e * (W + 900); c.save(); c.new_path(); c.move_to(-10, -10); c.line_to(x, -10); c.line_to(x - 900, H + 10); c.line_to(-10, H + 10); c.close_path(); c.clip(); draw_scene(c, s, g); c.restore()
            if 0 < p < 1: poly(c, [(x - 12, -10), (x + 16, -10), (x - 884, H + 10), (x - 912, H + 10)], hexc("#FFF4DC"))
        elif tr == "zoom":
            c.save(); c.translate(W / 2, H / 2); c.scale(1 + .15 * e, 1 + .15 * e); c.translate(-W / 2, -H / 2); draw_scene(c, pv, g); c.restore()
            c.push_group(); c.save(); c.translate(W / 2, H / 2); c.scale(lerp(1.35, 1, e), lerp(1.35, 1, e)); c.translate(-W / 2, -H / 2); draw_scene(c, s, g); c.restore()
            c.pop_group_to_source(); c.paint_with_alpha(e)
        elif tr == "flash":
            draw_scene(c, pv if p < .5 else s, g); caption_flash(c, 1 - abs(p - .5) * 2)
        else: draw_scene(c, s, g)
    else: draw_scene(c, s, g)

# ---- captions
_lay = {}
def layout(u):
    if u["id"] in _lay: return _lay[u["id"]]
    size = 62; sp = size * .3; lines = [[]]; wl = 0
    for w in u["words"]:
        tw = text_size(w["w"], size)[0]
        if lines[-1] and wl + sp + tw > 880: lines.append([]); wl = 0
        lines[-1].append((w, tw)); wl += tw + (sp if len(lines[-1]) > 1 else 0)
    out = []
    for ln in lines:
        tot = sum(tw for _, tw in ln) + sp * (len(ln) - 1); x = -tot / 2; row = []
        for w, tw in ln: row.append((w, x + tw / 2, tw)); x += tw + sp
        out.append((row, tot))
    _lay[u["id"]] = (out, size); return _lay[u["id"]]
def caption(c, g):
    u = None
    for x in UN:
        if x["start"] - .08 <= g <= x["end"] + .22: u = x
    if u is None: return
    lines, size = layout(u); n = len(lines); lh = 94; cy = 1565; bh = n * lh + 50; bw = max(t for _, t in lines) + 90
    age = clamp((g - u["start"] + .08) / .14); sc = lerp(.92, 1, e_out(age)); fade = clamp((u["end"] + .22 - g) / .15) if g > u["end"] else 1
    c.save(); c.translate(W / 2, cy); c.scale(sc, sc)
    rect(c, -bw / 2, -bh / 2, bw, bh, (.09, .06, .04, .62 * age * fade), 34)
    for li, (row, tot) in enumerate(lines):
        y = (li - (n - 1) / 2) * lh
        for w, x, tw in row:
            cur = w["s"] <= g < w["e"] or (g >= w["e"] and False); done = g >= w["e"]
            col = hexc("#FFD23F") if cur else (hexc("#FFF1D6") if done else (1, 1, 1))
            text(c, w["w"], x, y, size * (1.08 if cur else 1), col, "bold", stroke=hexc("#2a170c"), sw=7, a=age * fade)
    c.restore()

def frame(c, g):
    scene_frame(c, g); caption(c, g)
    rect(c, 0, 0, W * clamp(g / END), 9, hexc("#FFD23F", .9))
    if g > END - .5: rect(c, 0, 0, W, H, (0, 0, 0, clamp((g - (END - .5)) / .5)))
    if g < .15: rect(c, 0, 0, W, H, (0, 0, 0, 1 - g / .15))

def render_chunk(args):
    idx, a, b = args; out = f"/tmp/work/chunks/c{idx:03d}.mp4"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "-threads", "1", "-g", "30", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    sf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(sf); c.set_antialias(cairo.ANTIALIAS_BEST)
    for i in range(a, b):
        c.save(); c.set_source_rgb(0, 0, 0); c.paint(); c.restore(); frame(c, i / FPS); sf.flush(); p.stdin.write(sf.get_data())
    p.stdin.close(); p.wait(); return idx

if __name__ == "__main__":
    from multiprocessing import Pool
    N = int(END * FPS); os.makedirs("/tmp/work/chunks", exist_ok=True)
    if len(sys.argv) > 1 and sys.argv[1] == "bench":
        t0 = time.time(); render_chunk((999, 1000, 1030)); print("30 frames", time.time() - t0); sys.exit()
    CH = 120; chunks = [(i, a, min(N, a + CH)) for i, a in enumerate(range(0, N, CH))]
    t0 = time.time()
    with Pool(4) as pool:
        for r in pool.imap_unordered(render_chunk, chunks): print("chunk", r, "done", round(time.time() - t0), flush=True)
    with open("/tmp/work/chunks/list.txt", "w") as f:
        for i, _, _ in chunks: f.write(f"file 'c{i:03d}.mp4'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "/tmp/work/chunks/list.txt", "-c", "copy", "/tmp/work/video_silent.mp4"])
    print("ALLDONE", time.time() - t0, N)
