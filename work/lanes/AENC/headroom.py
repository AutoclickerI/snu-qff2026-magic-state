"""Exact all-orders headroom of v36c's A-encoder region by fault type / cell / Pauli component (class table)."""
import sys, json
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze import Table
import enc
from bmodel import A, POS

T = Table(sys.argv[1])
spec = enc.V36C
f = enc.propagate(spec)
k = len(spec.get('checks', []))
G = 1 << (7 + k)
y = np.arange(G)


def dist(keep):
    logabs = np.zeros(G); sign = np.ones(G)
    for ch, kind in tagged():
        terms = [(pa, t, pr) for pa, t, pr in ch if keep(kind, pa)]
        tot = sum(pr for _, _, pr in terms)
        chi = np.full(G, 1 - tot)
        for pa, t, pr in terms:
            g = f(pa, t)
            chi += pr * (1 - 2 * (np.bitwise_count(y & g) & 1).astype(np.int64))
        sign *= np.sign(chi); logabs += np.log(np.abs(chi))
    a = sign * np.exp(logabs); h = 1
    while h < G:
        a = a.reshape(-1, 2 * h); l = a[:, :h].copy(); r = a[:, h:].copy()
        a[:, :h] = l + r; a[:, h:] = l - r; a = a.reshape(-1); h *= 2
    Pt = (a / G)[:128]
    Aacc = float(Pt @ T.A)
    return float(Pt @ T.N) / Aacc, Aacc


def tagged():
    """channels with a kind label (init/check/cx/idle)."""
    chs = enc.channels(spec)
    n_init = len(spec['init']); n_chk = 2 * len(spec.get('checks', [])); n_cx = len(spec['cx'])
    out = []
    for i, ch in enumerate(chs):
        if i < n_init: kind = 'init'
        elif i < n_init + n_chk: kind = 'check'
        elif i < n_init + n_chk + n_cx: kind = 'cx'
        else: kind = 'idle'
        out.append((ch, kind))
    return out


base = dist(lambda kd, pa: True)
rows = [('v36c region (baseline)', base)]
rows.append(('whole region perfect', (T.L0, float(T.A[0]))))
for kd in ('init', 'check', 'cx', 'idle'):
    rows.append((f'{kd} noise perfect', dist(lambda k_, pa, kd=kd: k_ != kd)))
rows.append(('X/Y components on A perfect', dist(lambda k_, pa: not any(P in 'XY' for P in pa.values()))))
rows.append(('Z/Y components on A perfect', dist(lambda k_, pa: not any(P in 'ZY' for P in pa.values()))))
for q in A:
    rows.append((f'cell {q} (pos {POS[q]}) perfect', dist(lambda k_, pa, q=q: q not in pa)))
for q in A:
    rows.append((f'cell {q} idle perfect', dist(lambda k_, pa, q=q: not (k_ == 'idle' and q in pa))))
L0 = base[0]
print(f'{"counterfactual":34s} {"loss":>12s} {"gain":>10s} {"%":>7s} {"acceptance":>10s}')
for n, (L, Aacc) in rows:
    print(f'{n:34s} {L:12.6e} {L0 - L:+10.3e} {100 * (L0 - L) / L0:+7.2f} {Aacc:10.5f}')
