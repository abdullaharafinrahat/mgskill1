import numpy as np, wave, json
from scipy.signal import butter, sosfilt
from scipy.io import wavfile
SR = 44100; rng = np.random.RandomState(7)
from render import Video, META, KINDS, TOTAL
v = Video()
hits = []; wh = []
for i, sc in enumerate(v.sc):
    for (t, k) in sc.hits: hits.append((META[i]['start'] + t, k))
    if i > 0: wh.append((META[i]['start'], KINDS[i % 8]))
json.dump(dict(hits=hits, whooshes=wh), open('events.json', 'w'))
print(len(hits), 'hits', len(wh), 'whooshes', sorted(set(k for _, k in hits)))
N = int((TOTAL + 1.0) * SR); tt = np.arange(N) / SR
sr_, vd = wavfile.read('voice44.wav'); vd = vd.astype(np.float32) / 32768
if vd.ndim == 1: vd = np.stack([vd, vd], 1)
voice = np.zeros((N, 2), np.float32); voice[:min(N, len(vd))] = vd[:N]
voice *= 0.72 / np.abs(voice).max()
def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, btype=kind, fs=SR, output='sos'), x)
# --- music
mus = np.zeros((N, 2), np.float32)
chords = [[110, 164.8, 220, 261.6, 329.6], [87.3, 130.8, 174.6, 220, 261.6], [65.4, 130.8, 196, 261.6, 329.6], [98, 146.8, 196, 246.9, 293.7]]
CL = 6.0
for k in range(int(TOTAL / CL) + 2):
    ch = chords[k % 4]; t0 = k * CL - 1.0; i0 = max(0, int(t0 * SR)); i1 = min(N, int((t0 + CL + 2.0) * SR))
    if i1 <= i0: continue
    t = tt[i0:i1]; env = np.minimum(np.minimum((t - t0) / 1.5, 1), np.minimum((t0 + CL + 2.0 - t) / 1.5, 1)).clip(0, 1) ** 1.2
    for si, f in enumerate(ch):
        for ch_i, det in ((0, 1.0015), (1, .9985)):
            w = np.sin(2 * np.pi * f * det * t + si) + .3 * np.sin(4 * np.pi * f * det * t) + .1 * np.sin(6 * np.pi * f * det * t)
            mus[i0:i1, ch_i] += (w * env * (0.045 if f > 100 else .06) * (.8 + .2 * np.sin(2 * np.pi * (.1 + .03 * si) * t))).astype(np.float32)
for c in range(2): mus[:, c] = filt(mus[:, c], 'low', 1800)
tick = np.zeros(N, np.float32)
for k in range(int(TOTAL) + 1):
    i0 = int(k * SR); n = int(.06 * SR); t = np.arange(n) / SR; f = 1900 if k % 2 == 0 else 1300
    if i0 + n < N: tick[i0:i0 + n] += (np.sin(2 * np.pi * f * t) * np.exp(-t * 90) * .05).astype(np.float32)
mus[:, 0] += tick; mus[:, 1] += tick
# duck from voice envelope
vm = np.abs(voice).mean(1); hop = SR // 100; env = np.array([vm[i:i + hop].mean() for i in range(0, N - hop, hop)])
en = np.zeros_like(env); a = 0.0
for i, x in enumerate(env):
    a = x if x > a else a * .93 + x * .07
    en[i] = a
duck = 1 - .72 * np.clip(en / .05, 0, 1)
duck = np.interp(np.arange(N) / SR, (np.arange(len(duck)) + .5) / 100, duck)
mus *= (duck[:, None] * 0.9).astype(np.float32)
mus *= np.clip(tt / 2.0, 0, 1)[:, None] * np.clip((TOTAL + .8 - tt) / 2.0, 0, 1)[:, None]
# --- sfx
sfx = np.zeros((N, 2), np.float32)
def put(sig, t0, pan=0.0, g=1.0):
    i0 = int(t0 * SR)
    if i0 < 0: sig = sig[-i0:]; i0 = 0
    n = min(len(sig), N - i0)
    if n > 0:
        sfx[i0:i0 + n, 0] += sig[:n] * g * (1 - max(pan, 0)); sfx[i0:i0 + n, 1] += sig[:n] * g * (1 + min(pan, 0))
def noise(d): return rng.randn(int(d * SR)).astype(np.float32)
def whoosh(kind):
    d = .5; n = noise(d); t = np.linspace(0, 1, len(n)); env = np.sin(np.pi * t) ** 2
    cut = (500 + 5000 * t) if kind.startswith('zoom') else (4000 - 3000 * t) if kind == 'whipR' else (800 + 4500 * t)
    out = np.zeros_like(n); seg = 24
    for s in range(seg):
        a, b = int(s * len(n) / seg), int((s + 1) * len(n) / seg)
        out[a:b] = filt(n[a:b] + 0, 'band', [max(200, cut[a] * .6), min(cut[a] * 1.4 + 300, 12000)], 2)
    return out * env * 1.1
def boom(f0=60, d=.9, g=1.0):
    t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * (f0 + 90 * np.exp(-t * 18)) * t) * np.exp(-t * 4.5) * g).astype(np.float32)
def sfxk(k):
    t = np.arange(int(1.0 * SR)) / SR
    if k == 'big': n = filt(noise(.5), 'low', 3000) * np.exp(-np.arange(int(.5 * SR)) / SR * 9); b = boom(52, 1.2, .9); b[:len(n)] += n * .5; return b
    if k == 'hit': return boom(70, .6, .8) + np.pad(filt(noise(.15), 'band', [800, 4000]) * np.exp(-np.arange(int(.15 * SR)) / SR * 30) * .4, (0, int(.45 * SR)))
    if k == 'crack': n = filt(noise(.5), 'high', 2500); return np.pad(n * np.exp(-np.arange(len(n)) / SR * 14) * .6, (0, int(.5 * SR))) + np.pad(boom(80, .4, .5), (0, int(.6 * SR)))
    if k == 'ding': return (np.sin(2 * np.pi * 1318 * t) + .4 * np.sin(2 * np.pi * 2637 * t)) * np.exp(-t * 4) * .35
    if k == 'alarm': return ((np.sin(2 * np.pi * 880 * t) * (np.floor(t * 8) % 2 == 0)) * np.exp(-t * 1.5) * .3)[:int(.7 * SR)] + np.pad(boom(55, .8, .6), (0, int(.0 * SR)))[:int(.7 * SR)]
    if k == 'slice': n = filt(noise(.35), 'band', [1500, 7000]); e = np.sin(np.pi * np.linspace(0, 1, len(n))) ** 3; return n * e * .7
    if k == 'stamp': return boom(75, .5, 1.0) + np.pad(filt(noise(.08), 'band', [1000, 5000]) * .5 * np.exp(-np.arange(int(.08 * SR)) / SR * 40), (0, int(.42 * SR)))
    if k == 'tick': return np.sin(2 * np.pi * 1500 * t[:int(.08 * SR)]) * np.exp(-t[:int(.08 * SR)] * 60) * .5
    if k == 'thunder': n = filt(noise(1.4), 'low', 260); return n * np.exp(-np.arange(len(n)) / SR * 2.5) * 5 + boom(45, 1.4, .6)[:len(n)]
    if k == 'scratch': n = noise(.5); n = filt(n, 'band', [1200, 6000]); e = np.sin(np.pi * np.linspace(0, 1, len(n))); return n * e * .5
    return boom(70, .5, .6)
for t0, k in wh: put(whoosh(k), t0 - .28, pan=(-.5 if k == 'whipL' else .5 if k == 'whipR' else 0), g=.28)
for t0, k in hits: put(sfxk(k).astype(np.float32), t0, g=.38 if k in ('big', 'thunder') else .28)
mix = voice * 1.0 + mus * 1.0 + sfx * 1.0
mix = np.tanh(mix * 1.1) / np.tanh(1.1 * 1.0) if False else mix
pk = np.abs(mix).max(); print('peak before', pk)
# soft limiter: only compresses peaks above .8
th = .8; m = np.abs(mix); over = m > th
mix[over] = np.sign(mix[over]) * (th + (1 - th) * np.tanh((m[over] - th) / (1 - th)))
mix *= .891 / max(np.abs(mix).max(), .891) if np.abs(mix).max() > .891 else 1
print('final peak', np.abs(mix).max(), 'voice rms db', 20 * np.log10(np.sqrt((voice ** 2).mean())), 'music rms db', 20 * np.log10(np.sqrt((mus ** 2).mean()) + 1e-9), 'sfx peak', np.abs(sfx).max())
n_out = int(TOTAL * SR)
wavfile.write('mix.wav', SR, (mix[:n_out] * 32767).astype(np.int16))
