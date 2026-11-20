# -*- coding: utf-8 -*-
"""Step 3: render all frames in parallel (4 workers) straight into H.264 segments."""
import sys, os, subprocess, math, time
HERE = os.path.dirname(os.path.abspath(__file__))
FF = open(os.path.join(HERE, "ffpath")).read().strip()
PARTS = 4

def worker(k):
    import cairo
    from registry import draw_frame, DURATION, FPS, W, H
    total = int(math.ceil(DURATION * FPS))
    per = int(math.ceil(total / PARTS))
    f0, f1 = k * per, min(total, (k + 1) * per)
    out = os.path.join(HERE, "parts", f"part{k}.mp4")
    cmd = [FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "-g", "30", "-threads", "1",
           "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    t0 = time.time()
    for f in range(f0, f1):
        ctx.save()
        draw_frame(ctx, f / FPS)
        ctx.restore()
        surf.flush()
        p.stdin.write(bytes(surf.get_data()))
        if (f - f0) % 100 == 0:
            print(f"[part {k}] {f - f0}/{f1 - f0}  {time.time() - t0:.0f}s", flush=True)
    p.stdin.close()
    p.wait()
    print(f"[part {k}] done {f1 - f0} frames in {time.time() - t0:.0f}s", flush=True)

if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "parts"), exist_ok=True)
    if len(sys.argv) > 1:
        worker(int(sys.argv[1]))
    else:
        procs = [subprocess.Popen([sys.executable, __file__, str(k)], cwd=HERE) for k in range(PARTS)]
        for p in procs:
            p.wait()
        print("ALL PARTS DONE")
