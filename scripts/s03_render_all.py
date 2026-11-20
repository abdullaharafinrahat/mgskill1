# Step 3: render all frame ranges in parallel (2 workers) into segment mp4s
import math, json, subprocess, os, time
FPS = 30
DUR = json.load(open("timing.json"))["duration"]
N = math.ceil(DUR * FPS)
K = 10
size = math.ceil(N / K)
jobs = [(i * size, min(N, (i + 1) * size), f"seg_{i:02d}.mp4") for i in range(K)]
running = []
t0 = time.time()
while jobs or running:
    running = [p for p in running if p.poll() is None]
    while jobs and len(running) < 2:
        a, b, out = jobs.pop(0)
        if os.path.exists(out + ".done"):
            continue
        cmd = f"python3 s02_render.py {a} {b} {out} > {out}.log 2>&1 && touch {out}.done"
        running.append(subprocess.Popen(cmd, shell=True))
    time.sleep(2)
print("all segments done in", round(time.time() - t0), "s")
