"""Second-order loss of a circuit split by fault-region pairs (exact2 engine), B/C-focused categories.
usage: pairs.py <stem> [procs]"""
import sys, json, re
from collections import defaultdict
sys.path.insert(0, '../EVAL')
import numpy as np
import exact2
from qcirc import parse
from decompose import split

D = [0, 20, 7, 10, 3, 22, 21]
A = [1, 14, 8, 9, 2, 16, 15]
B = [6, 26, 13, 11, 4, 23, 27]
C = [12, 25, 19, 17, 5, 29, 28]
stem = sys.argv[1]
procs = int(sys.argv[2]) if len(sys.argv) > 2 else 16
text = open(stem + '.qasm').read()
dq = json.load(open(stem + '.json'))['data_qubits']
units, dets = parse(text)
life_of, find, entry, comp = split(units)
pre = set()
for root, idx in comp.items():
    if root in entry:
        pre |= set(idx)
at = {}
for i, u in enumerate(units):
    for q in u['q']:
        at[(u['t'], q)] = i
T = max(u['t'] for u in units)

def cat_unit(i):
    u = units[i]; qs = set(u['q']); t = u['t']; k = u['k']
    if k == 'CX' and t >= 43:
        c, tg = u['q']
        if c in D and tg in A: return 'DA'
        if c in B and tg in D: return 'BD'
        if c in B and tg in C and t == 44: return 'BtoC'
    if i in pre:
        if qs & set(D) and t >= 44: return 'D_end'
        return 'prefix'
    if qs & set(B + C) and t >= 45: return 'Bread' if qs & set(B) else 'Cread'
    if qs <= set(B): return 'prepB'
    if qs <= set(C): return 'prepC'
    if qs <= set(B + C): return 'prepBC'
    if qs & set(A) or (qs & {18, 31, 34, 35, 16}): return 'A' if qs & set(A) else 'Cread'
    return 'other'

ev = exact2.Eval(text, dq)
m = ev.m
chan_cat = {}
chan_unit = {}
for c, ch in enumerate(m.chans):
    if ch['gap'] is not None:
        q, first, n = ch['gap']
        key = (first - 1, q)
        idle = True
    else:
        st = m.steps[ch['ins']]
        step = None
        for qs, s in st:
            if ch['qubits'][0] in qs:
                step = s
        key = (step, ch['qubits'][0])
        idle = False
    i = at.get(key)
    if i is None:
        chan_cat[c] = 'unmapped'
        continue
    cc = cat_unit(i)
    if idle and cc == 'D_end' or (idle and units[i]['q'][0] in D and key[0] >= 44):
        cc = 'D_idle_end'
    chan_cat[c] = cc
    chan_unit[c] = (units[i]['t'], units[i]['q'], units[i]['k'], 'idle' if idle else ch['kind'])
res = exact2.run(ev, procs=procs, keep_thr=0.0, log=lambda *a: None)
print('loss2', res['loss2'], 'N1', res['N1'])
agg = defaultdict(float)
by_chan = defaultdict(float)
rows = []
for val, fa, fb, nij, aab in res['big']:
    ca, cb = ev.fch[fa], ev.fch[fb]
    k = tuple(sorted((chan_cat.get(ca, '?'), chan_cat.get(cb, '?'))))
    agg[k] += val
    by_chan[ca] += val / 2; by_chan[cb] += val / 2
    if 'prep' in k[0] + k[1] or 'BtoC' in k:
        rows.append((val, ev.fault_label(fa), chan_unit.get(ca), ev.fault_label(fb), chan_unit.get(cb), nij))
tot = sum(agg.values())
print('sum of kept pairs', tot)
for k, v in sorted(agg.items(), key=lambda kv: -kv[1]):
    if abs(v) > 1e-8:
        print(f'{v:.4e} {v/tot*100:6.2f}%  {k}')
cats = defaultdict(float)
for c, v in by_chan.items():
    cats[chan_cat.get(c, '?')] += v
print('half-split by category:', {k: f'{v:.3e}' for k, v in sorted(cats.items(), key=lambda kv: -kv[1])})
rows.sort(key=lambda r: -r[0])
json.dump([dict(val=r[0], a=r[1], ua=str(r[2]), b=r[3], ub=str(r[4]), nij=r[5]) for r in rows[:3000]],
          open(stem.split('/')[-1] + '_bcpairs.json', 'w'), indent=0)
for r in rows[:60]:
    print(f'{r[0]:.3e} nij={r[5]:.2f} | {r[1]} {r[2]} | {r[3]} {r[4]}')
