"""drop15 exterior (v36c without M57; q15 reset in region): validate the decomposition and build its class table.
usage: ext15.py <procs> validate | table <lo> <hi> | rank <sout.jsonl>...  (rank merges the table halves first)"""
import sys, json, time, os
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bmodel, enc, build, evalx
from bmodel import rep

SPEC = dict(init={1: ('MR', 37), 14: ('RX', 37), 8: ('RX', 36), 9: ('RX', 39), 2: ('R', 36), 16: ('R', 40), 15: ('RX', 39)},
            cx=[(37, 8, 2), (38, 2, 1), (38, 14, 8), (39, 8, 2), (40, 1, 2), (40, 9, 8), (40, 15, 14), (41, 14, 8),
                (41, 15, 16), (42, 8, 2), (42, 14, 15), (43, 8, 14)], checks=[], drop=(15,))
if __name__ == '__main__':
    procs, mode = int(sys.argv[1]), sys.argv[2]
    if mode == 'rank':
        from analyze import Table
        import rank
        halves = sorted(HERE.glob('table_drop15_*_*.json'))
        if halves:                                 # merge the table runs into table_drop15.json
            tab = {}
            for f in halves:
                tab.update(json.loads(f.read_text())['table'])
            assert len(tab) == 128, len(tab)
            (HERE / 'table_drop15.json').write_text(json.dumps(dict(stem='cand/drop15_base', table=tab), indent=1))
        T = Table(HERE / 'table_drop15.json')
        rel = dict(bmodel.REL); rel[15] = 38
        mr = dict(rank.MR_OK); mr[15] = 0
        L36, A36 = 4.1151559437773416e-05, 0.502728
        print(f'drop15 base encoder {T.exact(SPEC)}; perfect region {T.L0:.6e} acc {T.A[0]:.5f}')
        res = []
        for src in sys.argv[3:]:
            for i, r in enumerate(json.loads(l) for l in open(src)):
                for s in rank.variants(r, rel, mr, drop=(15,)):
                    L, Aacc = T.exact(s)
                    res.append((L, Aacc, src, i, r['cx'], s))
        print(len(res), 'variants')
        res.sort(key=lambda x: x[0])
        for L, Aacc, src, i, cx, s in res[:15]:
            print(f'{L:.10e} acc {Aacc:.5f} dL {L - L36:+.3e} dA {Aacc - A36:+.5f} {src}#{i} cx={cx} init={s["init"]} checks={s["checks"]}')
        print('Pareto (acceptance-descending, strictly better loss):')
        front, best = [], 1e9
        for x in sorted(res, key=lambda x: (-x[1], x[0])):
            if x[0] < best - 1e-15:
                front.append(x); best = x[0]
        for L, Aacc, src, i, cx, s in sorted(front, key=lambda x: x[0])[:25]:
            rate = (L - L36) / (Aacc - A36) if Aacc != A36 else 0
            print(f'{L:.6e} acc {Aacc:.5f} dL {L - L36:+.3e} dA {Aacc - A36:+.5f} rate {rate:+.2e} {src}#{i} init={s["init"]} checks={s["checks"]} cx={s["cx"]}')
        sys.exit()
    lo, hi = (int(sys.argv[3]), int(sys.argv[4])) if mode == 'table' else (0, 0)
    base = HERE / 'cand' / 'drop15_base'
    assert enc.legal(SPEC) is None, enc.legal(SPEC)
    build.build(SPEC, base, drop=(15,))
    rel = dict(bmodel.REL); rel[15] = 38
    ev = evalx.Ev(base, procs, rel=rel, mreuse={1: 64}, check_rows=())
    print(json.dumps(dict(prep=ev.prep_seconds, region=len(ev.ext.region), comp=ev.ext.nflip)), flush=True)
    if mode == 'validate':
        Pt = enc.ptilde(SPEC)
        import allorders
        full = allorders.run(base, procs)
        r = ev.run_many({'dec': ev.dist_terms(Pt), 'perfect': ([], 1.0)})
        for tag, (A, O) in r.items():
            print(json.dumps(dict(tag=tag, loss=evalx.loss_of(A, O), acceptance=A, full=full['loss'], full_acc=full['acceptance'])), flush=True)
        sys.exit()
    comps = {0: ([], 1.0)} if lo == 0 else {}
    for c in range(max(lo, 1), hi):
        d, s, e = ev.ext.sig_of(*rep(c))
        comps[c] = ([(d, s, e, 1.0)], 0.0)
    t = time.time()
    rr = ev.run_many(comps)
    tab = {str(c): dict(A=rr[c][0], O=rr[c][1]) for c in comps}
    (HERE / f'table_drop15_{lo}_{hi}.json').write_text(json.dumps(dict(stem=str(base), table=tab, seconds=time.time() - t), indent=1))
    print('table done', time.time() - t, flush=True)
