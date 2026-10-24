"""Exact rank (class table, all orders) of asearch outputs over init variants.

usage: rank.py <table.json> <out.jsonl> [top]
"""
import sys, json, itertools
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze import Table
from bmodel import A, REL, DA
import enc

MR_OK = {1: 1, 14: 0, 8: 1, 9: 1, 2: 0, 16: 1, 15: 1}


def variants(rec, rel=REL, mr_ok=MR_OK, drop=()):
    """All init variants for a circuit: pivots RX at fg-1 or RX at fg-2 + MX check at fg-1; Z inputs R at fg-1 or MR."""
    piv = [A[i] for i in range(7) if rec['pivots'] >> i & 1]
    cx = [(t, A[c], A[g]) for t, c, g in rec['layers']]
    fg = {q: min(t for t, c, g in cx if q in (c, g)) for q in A}
    opts = []
    for q in A:
        o = []
        if q in piv:
            if fg[q] - 1 > rel[q]: o.append(('RX', fg[q] - 1, None))
            if fg[q] - 2 > rel[q]: o.append(('RX', fg[q] - 2, fg[q] - 1))
        else:
            if fg[q] - 1 > rel[q]: o.append(('R', fg[q] - 1, None))
            if mr_ok[q]: o.append(('MR', rel[q], None))
        opts.append(o)
    for combo in itertools.product(*opts):
        spec = dict(init={}, cx=cx, checks=[], drop=tuple(drop))
        for q, (k, t, chk) in zip(A, combo):
            spec['init'][q] = (k, t)
            if chk is not None: spec['checks'].append((chk, q))
        if enc.legal(spec) is None:
            yield spec


if __name__ == '__main__':
    T = Table(sys.argv[1])
    recs = [json.loads(l) for l in open(sys.argv[2])]
    top = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    res = []
    for i, r in enumerate(recs):
        for s in variants(r):
            L, Aacc = T.exact(s)
            res.append((L, Aacc, i, r['cx'], s))
    res.sort(key=lambda x: x[0])
    base = T.exact(enc.V36C)
    print(f'v36c encoder: {base[0]:.10e} acc {base[1]:.5f}; perfect region {T.L0:.6e}; {len(res)} variants of {len(recs)} circuits')
    for L, Aacc, i, cx, s in res[:top]:
        print(f'{L:.10e} acc {Aacc:.5f} d={L - base[0]:+.3e} #{i} cx={cx} init={s["init"]} checks={s["checks"]}')
