# -*- coding: utf-8 -*-
"""STEP 4 - concat rendered segments, add narration + subtle whoosh SFX, write final MP4."""
import glob, subprocess, wave, json
import numpy as np
from common import *

SR = 44100
tl = json.load(open(TIMELINE, encoding='utf-8'))
dur = tl['duration']
sfx = np.zeros(int((dur + 1) * SR), dtype=np.float32)
rng = np.random.default_rng(7)


def whoosh(t0, length=0.55, gain=0.16):
    n = int(length * SR)
    x = rng.standard_normal(n).astype(np.float32)
    # moving low-pass via cumulative smoothing with changing coefficient
    out = np.zeros(n, dtype=np.float32)
    y = 0.0
    for i in range(n):
        u = i / n
        a = 0.04 + 0.5 * np.sin(np.pi * u)
        y += a * (x[i] - y)
        out[i] = y
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    out = out * env * gain * 3
    i0 = int(max(0, t0) * SR)
    sfx[i0:i0 + n] += out[: len(sfx) - i0]


for k, v in tl['scenes'].items():
    if int(k) > 1:
        whoosh(v['start'] - 0.3)

def pop(t0, f=520, gain=0.12):
    n = int(0.12 * SR); tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * (f + 900 * tt * 3) * tt) * np.exp(-tt * 38) * gain
    i0 = int(t0 * SR); sfx[i0:i0 + n] += s[: len(sfx) - i0].astype(np.float32)

for ch in tl['chunks']:
    if ch['id'] in (1, 3, 15, 39, 53, 63, 71, 77, 86):
        pop(ch['start'] + 0.05)

sfx = np.clip(sfx, -1, 1)
with wave.open(f'{OUT}/sfx.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((sfx * 32767).astype(np.int16).tobytes())

segs = sorted(glob.glob(f'{OUT}/seg_*.mp4'))
with open(f'{OUT}/list.txt', 'w') as f:
    for s in segs:
        f.write(f"file '{s}'\n")
subprocess.run([FFMPEG, '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', f'{OUT}/list.txt', '-c', 'copy', f'{OUT}/video_only.mp4'], check=True)
final = f'{OUT}/zahid_50_minute.mp4'
subprocess.run([FFMPEG, '-y', '-v', 'error', '-i', f'{OUT}/video_only.mp4', '-i', AUDIO, '-i', f'{OUT}/sfx.wav',
                '-filter_complex', '[1:a]volume=1.0[a1];[2:a]volume=0.8[a2];[a1][a2]amix=inputs=2:duration=first:normalize=0[a]',
                '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart',
                '-shortest', final], check=True)
print('wrote', final)
