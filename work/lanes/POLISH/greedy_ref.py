"""Greedy joint extension of v36i + bundle set S with v36h's positive 2-bundles and cheap acceptance singles.
Each round prices S+m for every candidate m on v36i; keeps the best L with A >= 0.5002 (a gate-violating best is retried
with each of the top acceptance sources). Writes rounds to greedy.jsonl."""
import sys, json
from multiprocessing import get_context
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work/lanes/BUNDLE')
import menu as M, ev as E
from pathlib import Path
R = '/home/jihoon/competitions/quantumn/work/lanes/BUNDLE/res/'
BASE = M.read(Path('/home/jihoon/competitions/quantumn/work/lanes/MAIN/v36i'))
EDITS = json.load(open(R + 'menu.json'))
tau_h = 3.815473322483099e-05; A0 = 0.5016415049479505; GATE = 0.5002
b2 = sorted([r for r in map(json.loads, open(R + 'b2.jsonl')) if 'loss' in r and r['loss'] < tau_h], key=lambda r: r['loss'])
s1 = [r for r in map(json.loads, open(R + 's1.jsonl')) if 'loss' in r]
moves = [tuple(r['b']) for r in b2] + [tuple(r['b']) for r in sorted(s1, key=lambda r: r['loss']) if r['loss'] < tau_h]
srcs = [tuple(r['b']) for r in sorted([r for r in s1 if r['acceptance'] - A0 > 0.0009 and r['loss'] - tau_h < 3e-8],
                                       key=lambda r: (r['loss'] - tau_h) / (r['acceptance'] - A0))[:12]]
S = json.loads(sys.argv[1])
def price(b):
    b = sorted(set(b))
    try:
        _, txt = M.apply_bundle(BASE, [EDITS[i] for i in b])
    except M.Invalid:
        return b, None
    r = E.price_stem(E.write_stem(txt))
    return b, (r['loss'], r['acceptance']) if 'loss' in r else None
log = open(sys.argv[2], 'a')
with get_context('fork').Pool(12) as pool:
    cur = dict(zip(('loss', 'acceptance'), price(S)[1])); log.write(json.dumps(dict(round=0, S=sorted(S), **cur)) + '\n'); log.flush()
    for rnd in range(1, 30):
        cands = [S + list(m) for m in moves if not set(m) <= set(S)]
        res = [x for x in pool.imap_unordered(price, cands, chunksize=2) if x[1]]
        better = sorted([x for x in res if x[1][0] < cur['loss']], key=lambda x: x[1][0])
        pick = next((x for x in better if x[1][1] >= GATE), None)
        if better and (pick is None or better[0][1][0] < pick[1][0] - 1e-9):
            fund = [x for x in pool.imap_unordered(price, [better[k][0] + list(s) for k in range(min(5, len(better))) for s in srcs]) if x[1]]
            fund = sorted([x for x in fund if x[1][1] >= GATE and x[1][0] < cur['loss']], key=lambda x: x[1][0])
            if fund and (pick is None or fund[0][1][0] < pick[1][0]):
                pick = fund[0]
        if pick is None:
            log.write(json.dumps(dict(round=rnd, stop='no feasible improvement', tried=len(res))) + '\n'); break
        S = pick[0]; cur = dict(loss=pick[1][0], acceptance=pick[1][1])
        log.write(json.dumps(dict(round=rnd, S=S, tried=len(res), **cur)) + '\n'); log.flush()
