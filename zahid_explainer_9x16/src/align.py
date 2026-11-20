import numpy as np, json, re
from script_data import SCENES
db = np.load('db.npy'); H = 0.01
SIL = -47
speech = (db >= SIL).astype(float)
cs = np.concatenate([[0], np.cumsum(speech)]) * H
lead = float(np.argmax(db > SIL) * H)
tail = float((len(db) - np.argmax(db[::-1] > SIL)) * H)
P = [tuple(p) for p in json.load(open('pauses.json')) if p[0] > lead and p[1] < tail]
CONS = [chr(c) for c in list(range(0x995, 0x9BA)) + [0x9DC, 0x9DD, 0x9DF]]
MATRA = 'ািীুূৃেৈোৌ'
def syl(word):
    if re.search(r'[A-Za-z]', word):
        return max(1, len(re.findall(r'[aeiouyAEIOUY]+', word)))
    n = 0
    w = re.sub(r'[^\u0980-\u09FF]', '', word); L = len(w)
    for i, ch in enumerate(w):
        if ch in 'অআইঈউঊঋএঐওঔ' or ch in MATRA: n += 1
        elif ch in CONS:
            nx = w[i + 1] if i + 1 < L else ''
            if nx == '্' or nx in MATRA: continue
            if i == L - 1 or (i == L - 2 and nx in 'ংঃঁ'): continue
            n += 1
        elif ch == 'ৎ': n += 1
    if re.search(r'[\u09E6-\u09EF]', word): n = max(n, 3)
    return max(1, n)
clauses = []
for si, (sid, cl) in enumerate(SCENES):
    for c in cl: clauses.append((si, c))
words_per = [c.split() for _, c in clauses]
sylw = [[syl(w) for w in ws] for ws in words_per]
csyl = [sum(s) for s in sylw]
rate = cs[-1] / sum(csyl)
print('clauses', len(clauses), 'pauses', len(P), 'rate s/syl', rate)
N = len(clauses); M = len(P)
def strong(txt): return txt.rstrip('"').endswith(('।', '?', ':'))
INF = 1e18
def spt(a, b): return cs[int(round(b / H))] - cs[int(round(a / H))]
def ccost(a, b, k):
    sp = spt(a, b); exp = rate * csyl[k]
    return (sp - exp) ** 2 / (exp + 0.4)
def rew(j, k):
    return (0.8 if strong(clauses[k][1]) else 0.3) * min(P[j][1] - P[j][0], 0.5)
best = [[INF] * M for _ in range(N)]; back = [[-1] * M for _ in range(N)]
for j in range(M):
    best[0][j] = ccost(lead, P[j][0], 0) - rew(j, 0)
for k in range(1, N - 1):
    for j in range(k, M):
        bc = INF; bi = -1
        for i in range(max(0, j - 40), j):
            if best[k - 1][i] >= INF: continue
            c = best[k - 1][i] + ccost(P[i][1], P[j][0], k)
            if c < bc: bc = c; bi = i
        if bi >= 0:
            best[k][j] = bc - rew(j, k); back[k][j] = bi
bj = -1; bc = INF
for i in range(M):
    if best[N - 2][i] < INF:
        c = best[N - 2][i] + ccost(P[i][1], tail, N - 1)
        if c < bc: bc = c; bj = i
assign = [bj]
for k in range(N - 2, 0, -1): assign.append(back[k][assign[-1]])
assign = assign[::-1]
starts = [lead] + [P[j][1] for j in assign]; ends = [P[j][0] for j in assign] + [tail]
allw = []
for k in range(N):
    a, b = starts[k], ends[k]; tot = spt(a, b); ws = words_per[k]
    wt = [s + 0.35 for s in sylw[k]]; W = sum(wt); acc = 0
    cs_a = cs[int(round(a / H))]
    def inv(target, right=False):
        idx = np.searchsorted(cs, cs_a + target, side='right' if right else 'left'); return min(idx, len(cs) - 1) * H
    for w, x in zip(ws, wt):
        s = inv(acc / W * tot, True); e = inv((acc + x) / W * tot); acc += x
        allw.append(dict(w=w, s=float(s), e=float(max(e, s + 0.05)), clause=k, scene=clauses[k][0]))
cuts = [0.0]; pw = []
for k in range(N - 1):
    if clauses[k][0] != clauses[k + 1][0]:
        j = assign[k]; cuts.append((P[j][0] + P[j][1]) / 2); pw.append(P[j][1] - P[j][0])
cuts.append(171.1543)
scenes = []
for si, (sid, cl) in enumerate(SCENES):
    ws = [w for w in allw if w['scene'] == si]
    scenes.append(dict(id=sid, start=cuts[si], end=cuts[si + 1], words=ws,
                       tw=(min(0.16, pw[si - 1] / 2 + 0.03) if si > 0 else 0)))
json.dump(dict(scenes=scenes, lead=lead, tail=tail), open('timing.json', 'w'), ensure_ascii=False, indent=1)
for s in []:
    print(f"{s['id']:12s} {s['start']:7.2f}-{s['end']:7.2f} dur {s['end']-s['start']:5.2f} words {len(s['words'])} tw {s['tw']:.2f}")
dev = [P[j][1] - P[j][0] for j in assign]
print('boundary pause dur min/mean', min(dev), np.mean(dev), 'n scenes', len(scenes))
print('--- per-clause ratio (actual speech / expected)')
for k in range(N):
    sp=spt(starts[k],ends[k]); ex=rate*csyl[k]
    flag='  <<<' if sp/ex>1.6 or sp/ex<0.6 else ''
    print(k, clauses[k][0], f"{starts[k]:.2f}-{ends[k]:.2f} r={sp/ex:.2f}{flag}")
