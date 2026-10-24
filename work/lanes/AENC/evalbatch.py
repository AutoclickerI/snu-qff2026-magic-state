"""Build and price (full all-orders) the top asearch encoders of a scenario, over init variants.

usage: evalbatch.py <asearch.jsonl> <tag> <top> <procs> [drop cells comma-separated]
Writes cand/<tag>_<i>_<j>.{qasm,json} and appends results to res_<tag>.jsonl.
"""
import sys, json, itertools, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from bmodel import A, REL
import enc, build, allorders

MR_OK = {1: 1, 14: 0, 8: 1, 9: 1, 2: 0, 16: 1, 15: 1}


def variants(rec, drop=()):
    piv = [A[i] for i in range(7) if rec['pivots'] >> i & 1]
    cx = [(t, A[c], A[g]) for t, c, g in rec['layers']]
    fg = {q: min(t for t, c, g in cx if q in (c, g)) for q in A}
    rel = {q: (enc.UREL[q] if q in drop else REL[q]) for q in A}
    opts = []
    for q in A:
        o = []
        if q in piv:
            if fg[q] - 1 > rel[q]: o.append(('RX', fg[q] - 1, None))
            if fg[q] - 2 > rel[q]: o.append(('RX', fg[q] - 2, fg[q] - 1))
        else:
            if fg[q] - 1 > rel[q]: o.append(('R', fg[q] - 1, None))
            if q in drop: o.append(('U', enc.UREL[q], None))
            elif MR_OK[q]: o.append(('MR', REL[q], None))
        opts.append(o)
    for combo in itertools.product(*opts):
        spec = dict(init={}, cx=cx, checks=[], drop=tuple(drop))
        for q, (k, t, chk) in zip(A, combo):
            spec['init'][q] = (k, t)
            if chk is not None: spec['checks'].append((chk, q))
        if enc.legal(spec) is None:
            yield spec


if __name__ == '__main__':
    src, tag, top, procs = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    drop = tuple(int(x) for x in sys.argv[5].split(',')) if len(sys.argv) > 5 and sys.argv[5] else ()
    recs = [json.loads(l) for l in open(src)][:top]
    (HERE / 'cand').mkdir(exist_ok=True)
    out = open(HERE / f'res_{tag}.jsonl', 'a')
    for i, r in enumerate(recs):
        for j, spec in enumerate(variants(r, drop)):
            stem = HERE / 'cand' / f'{tag}_{i}_{j}'
            build.build(spec, stem, drop=drop)
            try:
                res = allorders.run(stem, procs)
            except Exception as e:
                res = dict(stem=str(stem), error=repr(e)[:300])
            res.update(screen=r['score'], cx=r['cx'], spec=dict(init={str(k): v for k, v in spec['init'].items()},
                                                                   cx=spec['cx'], checks=spec['checks'], drop=list(drop)))
            out.write(json.dumps(res) + '\n'); out.flush()
            print(json.dumps({k: res.get(k) for k in ('stem', 'loss', 'acceptance', 'screen', 'error')}), flush=True)
