# -*- coding: utf-8 -*-
"""STEP 1 - analyse the narration audio and align script chunks to time.

Outputs out/timeline.json (chunk start/end + scene ranges) and out/env.json
(per-frame voice loudness used for lip-sync)."""
import subprocess, json, sys
import numpy as np
from common import FFMPEG, AUDIO, OUT, FPS
from script_data import CHUNKS

SR = 16000
raw = subprocess.run([FFMPEG, "-v", "error", "-i", AUDIO, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                     capture_output=True).stdout
y = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
dur = len(y) / SR
print("duration", dur)

HOP = SR // 100                    # 10 ms
n = len(y) // HOP
rms = np.sqrt((y[:n * HOP].reshape(n, HOP) ** 2).mean(axis=1) + 1e-12)
db = 20 * np.log10(rms + 1e-9)
peak = np.percentile(db, 98)
silent = db < peak - 27
# silence intervals >= 0.12 s
ivs, i = [], 0
while i < n:
    if silent[i]:
        j = i
        while j < n and silent[j]:
            j += 1
        if (j - i) >= 12:
            ivs.append((i / 100, j / 100))
        i = j
    else:
        i += 1
print("silence intervals", len(ivs))

# ---- lip-sync envelope at video fps ----
env = []
for f in range(int(dur * FPS) + 2):
    a, b = int(f / FPS * 100), int((f + 1) / FPS * 100) + 1
    seg = rms[a:b]
    env.append(float(seg.mean()) if len(seg) else 0.0)
env = np.array(env)
env = env / (np.percentile(env, 95) + 1e-9)
env = np.clip(env, 0, 1.2)
env[env < 0.08] = 0
json.dump({"env": [round(float(v), 3) for v in env]}, open(f"{OUT}/env.json", "w"))

# ---- DP alignment (speech segments <-> caption chunks) ----
def weight(t):
    return sum(1 for ch in t if ch.strip() and ch not in "।,?:“”\"-")

texts = [c[1] for c in CHUNKS]
N = len(texts)
w = np.array([weight(t) for t in texts], dtype=float)
sil = [iv for iv in ivs if iv[1] - iv[0] >= 0.08]
speech_start = next(i for i in range(n) if not silent[i]) / 100
speech_end = (n - next(i for i in range(n) if not silent[n - 1 - i])) / 100
segs, cur = [], speech_start
for a_, b_ in sil:
    if a_ > cur + 0.05:
        segs.append((cur, a_))
    cur = b_
if speech_end > cur + 0.05:
    segs.append((cur, speech_end))
S = len(segs)
sd = np.array([b_ - a_ for a_, b_ in segs])
gaps = np.array([segs[j + 1][0] - segs[j][1] for j in range(S - 1)] + [0.0])   # gap after seg j
r = sd.sum() / w.sum()
print("segments", S, "chunks", N, "rate", r)

def strength(t):
    t = t.rstrip("”\" ")
    return 2 if t[-1] in "।?:" else (1 if t[-1] == "," else 0)
st_ = [strength(t) for t in texts]
cw = np.concatenate([[0], np.cumsum(w)])
cs = np.concatenate([[0], np.cumsum(sd)])

def dcost(d, e):
    return (d - e) ** 2 / (0.3 + e) * 3.0

def b_at_gap(i, g):          # chunk i (1-based) ends exactly before a silence of length g
    s = st_[i - 1]
    if s == 2: return 2.0 * max(0, 0.35 - g) / 0.35
    if s == 1: return 0.3 * max(0, 0.2 - g) / 0.2
    return 0.8 + 0.6 * min(g, 0.8)

def b_inside(i):             # chunk boundary inside a continuous speech segment
    return (3.0, 0.3, 0.0)[(2, 1, 0).index(st_[i - 1])]

INF = 1e18
dp = np.full((N + 1, S + 1), INF)
bk = {}
dp[0, 0] = 0
for i in range(1, N + 1):
    for j in range(1, S + 1):
        best, arg = INF, None
        g = gaps[j - 1] if i < N else 0.0
        bc = b_at_gap(i, g) if i < N else 0.0
        for m in range(1, 7):               # segment j holds chunks i-m+1..i
            if i - m < 0 or dp[i - m, j - 1] >= INF:
                continue
            inner = sum(b_inside(q) for q in range(i - m + 1, i))
            c = dp[i - m, j - 1] + dcost(sd[j - 1], (cw[i] - cw[i - m]) * r) + bc + inner
            if c < best:
                best, arg = c, ("A", m)
        for k in range(2, 5):               # chunk i spans segments j-k+1..j
            if j - k < 0 or dp[i - 1, j - k] >= INF:
                continue
            inner_g = gaps[j - k: j - 1]
            ic = sum(0.2 + (0.6 if gg > 0.3 else 0) for gg in inner_g)
            c = dp[i - 1, j - k] + dcost(cs[j] - cs[j - k], w[i - 1] * r) + ic + bc
            if c < best:
                best, arg = c, ("B", k)
        dp[i, j], bk[(i, j)] = best, arg
# backtrack
groups = []     # (segment_index_range, chunk_index_range)
i, j = N, S
while i > 0 and j > 0:
    kind, m = bk[(i, j)]
    if kind == "A":
        groups.append(((j - 1, j), (i - m, i))); i -= m; j -= 1
    else:
        groups.append(((j - m, j), (i - 1, i))); i -= 1; j -= m
groups.reverse()
print("final", i, j, "cost", dp[N, S])

st = [0.0] * N
en = [0.0] * N
for (sa, sb), (ca, cb) in groups:
    a, b = segs[sa][0], segs[sb - 1][1]
    if sb - sa > 1:                     # chunk spanning several segments
        st[ca], en[ca] = a, b
    else:
        tot = w[ca:cb].sum()
        t0 = a
        for q in range(ca, cb):
            d = (b - a) * w[q] / tot
            st[q], en[q] = t0, t0 + d
            t0 += d
# small visual gap between consecutive chunks inside a segment
for q in range(N - 1):
    if abs(en[q] - st[q + 1]) < 1e-6:
        en[q] -= 0.03
en[-1] = dur
chunks = [{"id": q + 1, "scene": CHUNKS[q][0], "text": CHUNKS[q][1], "start": round(float(st[q]), 3),
           "end": round(float(en[q]), 3)} for q in range(N)]
scenes = {}
for q, ch in enumerate(chunks):
    s = ch["scene"]
    if s not in scenes:
        scenes[s] = {"start": 0.0 if q == 0 else round((en[q - 1] + st[q]) / 2, 3), "end": dur}
    if q < N - 1 and CHUNKS[q + 1][0] != s:
        scenes[s]["end"] = round((en[q] + st[q + 1]) / 2, 3)
json.dump({"duration": dur, "chunks": chunks, "scenes": scenes}, open(f"{OUT}/timeline.json", "w"), ensure_ascii=False, indent=1)
for ch in chunks:
    print("%3d s%-2d %6.2f-%6.2f  %s" % (ch["id"], ch["scene"], ch["start"], ch["end"], ch["text"]))
print({k: (v["start"], v["end"]) for k, v in scenes.items()})
