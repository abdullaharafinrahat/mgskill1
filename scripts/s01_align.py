# Step 1: forced alignment of the script to the narration audio (MMS_FA wav2vec2 + CTC Viterbi)
import json, re, subprocess, sys
import numpy as np, torch, torchaudio
from torchaudio.pipelines import MMS_FA as bundle
import uroman
from script_data import SENTENCES
SENTENCES = SENTENCES[:40]  # the provided audio is cut off during sentence 39

torch.set_num_threads(2)
subprocess.run(["./ffmpeg", "-y", "-loglevel", "error", "-i", "audio01.mp3", "-ac", "1", "-ar", "16000", "narr16k.wav"], check=True)
import wave
with wave.open("narr16k.wav") as wf:
    sr = wf.getframerate()
    pcm = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
wav = torch.from_numpy(pcm)[None, :]
DUR = wav.shape[1] / sr
print("duration", DUR)

import os
model = None if os.path.exists('emission.npy') else bundle.get_model().eval()
labels = bundle.get_labels()
L2I = {c: i for i, c in enumerate(labels)}

# ---- emissions in overlapping chunks ----
CH, CTX = 20 * sr, 2 * sr
em_parts = []
with torch.inference_mode():
    pos = 0 if model is not None else wav.shape[1]
    while pos < wav.shape[1]:
        a = max(0, pos - CTX)
        b = min(wav.shape[1], pos + CH + CTX)
        e, _ = model(wav[:, a:b])
        e = torch.log_softmax(e, -1)[0]
        fr = e.shape[0]
        ratio = (b - a) / fr
        f0 = int(round((pos - a) / ratio))
        f1 = int(round((min(pos + CH, wav.shape[1]) - a) / ratio))
        em_parts.append(e[f0:f1])
        print("chunk", pos / sr, "frames", fr, flush=True)
        pos += CH
emission = np.load('emission.npy') if model is None else torch.cat(em_parts, 0).numpy()
if model is not None: np.save('emission.npy', emission)
emission = emission[:, :28]
emission = emission - np.log(np.exp(emission).sum(1, keepdims=True))
T = emission.shape[0]
fps = T / DUR
print("emission", emission.shape, "fps", fps)

# ---- transcript tokens ----
u = uroman.Uroman()
DIGITS = {"৫০": "পঞ্চাশ"}
words = []  # (sent_idx, original word, token ids)
for si, s in enumerate(SENTENCES):
    for w in s.split():
        base = re.sub(r"[\"।,?:]", "", w)
        base = DIGITS.get(base, base)
        rom = u.romanize_string(base).lower()
        rom = re.sub(r"[^a-z']", "", rom)
        if not rom:
            continue
        words.append((si, w, [L2I[c] for c in rom]))
tokens, owner = [], []
for wi, (si, w, ids) in enumerate(words):
    for t in ids:
        tokens.append(t)
        owner.append(wi)
N = len(tokens)
print("words", len(words), "tokens", N)

# ---- CTC Viterbi (global) ----
blank = 0
S = 2 * N + 1
ext = np.full(S, blank, dtype=np.int64)
ext[1::2] = tokens
NEG = -1e30
score = np.full(S, NEG)
score[0] = emission[0, blank]
score[1] = emission[0, ext[1]]
back = np.zeros((T, S), dtype=np.int8)
skip_ok = np.zeros(S, dtype=bool)
for s_ in range(3, S, 2):
    skip_ok[s_] = ext[s_] != ext[s_ - 2]
for t in range(1, T):
    c0 = score
    c1 = np.concatenate([[NEG], score[:-1]])
    c2 = np.concatenate([[NEG, NEG], score[:-2]])
    c2 = np.where(skip_ok, c2, NEG)
    stack = np.stack([c0, c1, c2])
    arg = stack.argmax(0)
    score = stack.max(0) + emission[t, ext]
    back[t] = arg
s_ = S - 1 if score[S - 1] > score[S - 2] else S - 2
path = np.zeros(T, dtype=np.int64)
for t in range(T - 1, -1, -1):
    path[t] = s_
    s_ = int(s_) - int(back[t, s_])
# token spans
tok_first = {}
tok_last = {}
for t in range(T):
    st = path[t]
    if st % 2 == 1:
        k = (st - 1) // 2
        tok_first.setdefault(k, t)
        tok_last[k] = t
word_t = []
k = 0
for wi, (si, w, ids) in enumerate(words):
    ks = list(range(k, k + len(ids)))
    k += len(ids)
    s0 = tok_first[ks[0]] / fps
    e0 = (tok_last[ks[-1]] + 1) / fps
    word_t.append({"s": si, "w": w, "start": round(s0, 3), "end": round(e0, 3)})

# ---- sentence timing: start at first word, boundaries midway through the gaps ----
sent = []
for si, s in enumerate(SENTENCES):
    ws = [x for x in word_t if x["s"] == si]
    sent.append({"i": si, "text": s, "ws": ws[0]["start"], "we": ws[-1]["end"], "words": ws})
for i, d in enumerate(sent):
    d["start"] = 0.0 if i == 0 else round((sent[i - 1]["we"] + d["ws"]) / 2, 3)
    d["end"] = DUR if i == len(sent) - 1 else round((d["we"] + sent[i + 1]["ws"]) / 2, 3)
json.dump({"duration": DUR, "sentences": sent}, open("timing.json", "w"), ensure_ascii=False, indent=1)
for d in sent:
    n = len(re.sub(r"[\s\"।,?:\-]", "", d["text"]))
    print(f"{d['i']:2d} {d['ws']:7.2f}-{d['we']:7.2f} dur={d['we']-d['ws']:5.2f} rate={n/(d['we']-d['ws']):5.1f}  {d['text'][:28]}")
