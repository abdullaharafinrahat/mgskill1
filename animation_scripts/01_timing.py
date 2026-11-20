# -*- coding: utf-8 -*-
"""Step 1: analyse the narration audio.
 - decodes audio, builds loudness envelope (used for lip-sync)
 - finds pauses
 - aligns every caption chunk of the script to the audio (pause-snapped)
Outputs: timeline.json, amp.npy
"""
import json, subprocess, unicodedata, sys, os
import numpy as np
from script_data import CHUNKS, SCENE_ORDER

HERE = os.path.dirname(os.path.abspath(__file__))
FF = open(os.path.join(HERE, "ffpath")).read().strip()
SR = 16000

raw = subprocess.run([FF, "-v", "error", "-i", os.path.join(HERE, "audio.mp3"), "-f", "s16le", "-ac", "1",
                      "-ar", str(SR), "-"], capture_output=True).stdout
x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
DUR = len(x) / SR
print("audio duration", DUR)

# 10 ms RMS
hop = SR // 100
n = len(x) // hop
rms = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(axis=1))
db = 20 * np.log10(rms + 1e-6)
speech_ref = np.percentile(db, 90)
thr = speech_ref - 24
quiet = db < thr
print("ref dB", speech_ref, "thr", thr)

# pauses (>=180ms)
pauses = []
i = 0
while i < n:
    if quiet[i]:
        j = i
        while j < n and quiet[j]:
            j += 1
        if (j - i) >= 18:
            pauses.append((i / 100.0, j / 100.0))
        i = j
    else:
        i += 1
# speech start / end
nz = np.where(~quiet)[0]
S0, S1 = nz[0] / 100.0, (nz[-1] + 1) / 100.0
pauses = [(a, b) for a, b in pauses if a > S0 + 0.05 and b < S1 - 0.05]
print("speech", S0, S1, "pauses", len(pauses))

# amplitude envelope at 60 fps for lip-sync (smoothed, normalised)
FPS_ENV = 60
h2 = SR // FPS_ENV
m = len(x) // h2
env = np.sqrt((x[: m * h2].reshape(m, h2) ** 2).mean(axis=1))
env = env / (np.percentile(env, 95) + 1e-6)
env = np.clip(env, 0, 1.2)
np.save(os.path.join(HERE, "amp.npy"), env.astype(np.float32))


# ---- alignment -----------------------------------------------------------
def weight(text):
    w = 0.0
    for ch in text:
        cat = unicodedata.category(ch)
        if ch in "।?!":
            w += 5
        elif ch in ",:;":
            w += 3
        elif cat.startswith("L") or cat.startswith("M"):
            w += 0.8 if ch.isascii() else 1.0
        elif cat.startswith("N"):
            w += 1.5
    return w


def pause_after(text):
    t = text.rstrip("”\" ")
    if t.endswith(("।", "?", "!")):
        return 5
    if t.endswith((",", ":")):
        return 3
    return 3


ws = [weight(t) for _, _, t in CHUNKS]
pw = [pause_after(t) for _, _, t in CHUNKS]
N = len(CHUNKS)
pos = []
acc = 0.0
for k in range(N - 1):
    acc += ws[k]
    pos.append(acc + pw[k] / 2)
    acc += pw[k]
acc += ws[-1]
Wtot = acc

bounds = []
anchor_t, anchor_p = S0, 0.0
last_b = S0
used = set()
for k in range(N - 1):
    r = (S1 - anchor_t) / (Wtot - anchor_p)
    pred = anchor_t + (pos[k] - anchor_p) * r
    best, bscore = None, 1e9
    for idx, (a, b) in enumerate(pauses):
        c = (a + b) / 2
        if idx in used or c <= last_b + 0.35:
            continue
        d = abs(c - pred)
        if d > 1.3:
            continue
        score = d - 1.2 * min(b - a, 0.7)
        if score < bscore:
            best, bscore = idx, score
    if best is None:
        bt = pred
        seg = (pred - 0.05, pred + 0.05)
    else:
        used.add(best)
        seg = pauses[best]
        bt = (seg[0] + seg[1]) / 2
    bounds.append((bt, seg[0], seg[1], best is not None))
    anchor_t, anchor_p, last_b = bt, pos[k], bt

# ---- global DP refinement: choose N-1 pauses (increasing) so every chunk duration matches its text length
greedy_rates = []
pb = S0
for k in range(N - 1):
    greedy_rates.append((bounds[k][1] - pb) / max(ws[k], 1))
    pb = bounds[k][2]
R = float(np.median(greedy_rates))
print("median rate", R)
P = len(pauses)
INF = 1e18
def chunk_cost(k, start_t, end_t):
    d = end_t - start_t
    e = ws[k] * R + 0.15
    if d <= 0.15:
        return 1e6
    return ((d - e) / (0.18 * e + 0.25)) ** 2
def pause_bonus(k, i):
    L = min(pauses[i][1] - pauses[i][0], 0.6) / 0.6
    return -(2.2 if pw[k] == 5 else 1.0) * L
# dp[k][i]: boundary k placed at pause i
dp = [[INF] * P for _ in range(N - 1)]
bp = [[-1] * P for _ in range(N - 1)]
for i in range(P):
    dp[0][i] = chunk_cost(0, S0, pauses[i][0]) + pause_bonus(0, i)
for k in range(1, N - 1):
    for i in range(P):
        bestv, bestj = INF, -1
        for j in range(i):
            if dp[k - 1][j] >= INF:
                continue
            v = dp[k - 1][j] + chunk_cost(k, pauses[j][1], pauses[i][0])
            if v < bestv:
                bestv, bestj = v, j
        if bestj >= 0:
            dp[k][i] = bestv + pause_bonus(k, i)
            bp[k][i] = bestj
bestv, bi = INF, -1
for i in range(P):
    if dp[N - 2][i] >= INF:
        continue
    v = dp[N - 2][i] + chunk_cost(N - 1, pauses[i][1], S1)
    if v < bestv:
        bestv, bi = v, i
sel = [0] * (N - 1)
for k in range(N - 2, -1, -1):
    sel[k] = bi
    bi = bp[k][bi]
bounds = [((pauses[i][0] + pauses[i][1]) / 2, pauses[i][0], pauses[i][1], True) for i in sel]

timeline = []
prev_end_center = 0.0
prev_speech_start = S0
for k, (scene, spk, text) in enumerate(CHUNKS):
    if k < N - 1:
        c, ps, pe, snapped = bounds[k]
        speech_end = ps
        end_center = c
    else:
        speech_end = S1
        end_center = DUR
        snapped = True
    timeline.append(dict(i=k, scene=scene, speaker=spk, text=text,
                         start=prev_end_center, end=end_center,
                         s0=prev_speech_start, s1=speech_end, snapped=snapped))
    prev_end_center = end_center
    prev_speech_start = bounds[k][2] if k < N - 1 else 0

scenes = []
for name in SCENE_ORDER:
    cs = [c for c in timeline if c["scene"] == name]
    scenes.append(dict(name=name, start=cs[0]["start"], end=cs[-1]["end"],
                       first=cs[0]["i"], last=cs[-1]["i"]))

json.dump(dict(duration=DUR, chunks=timeline, scenes=scenes), open(os.path.join(HERE, "timeline.json"), "w"),
          ensure_ascii=False, indent=1)

for c in timeline:
    d = c["s1"] - c["s0"]
    print(f'{c["i"]:2d} {c["s0"]:7.2f}-{c["s1"]:7.2f} {d:5.2f}s r={d / max(ws[c["i"]], 1):.3f} snap={int(c["snapped"])} {c["scene"]:8s} {c["text"][:28]}')
print()
for s in scenes:
    print(f'{s["name"]:8s} {s["start"]:7.2f} -> {s["end"]:7.2f} ({s["end"] - s["start"]:.1f}s)')
