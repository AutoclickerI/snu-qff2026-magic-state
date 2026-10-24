"""Hill-climb / SA on the proxy objective J with exhaustive small neighbourhoods (full FT model, F1 hard).
Neighbourhood: a run of consecutive path cells (optionally with adjacent helpers) x a layer window; every
completion with window CX <= incumbent + extra is enumerated (up to N) and scored by the proxy.
usage: lns3.py <start.json> <out_prefix> <seconds> <seed> [helpers comma] [KZ KA]"""
import sys, json, random, time, math, os
from pathlib import Path
from ortools.sat.python import cp_model
import synth_bc as S
import lns, mkcand, splice, proxy

PATH = [4, 5, 11, 17, 23, 29, 28, 27, 26, 25, 19, 13, 12, 6]
HADJ = {18: [12, 19, 24], 24: [18, 25, 30], 30: [24, 31], 31: [25, 30, 32], 32: [26, 31, 33], 33: [27, 32, 34], 34: [28, 33, 35], 35: [29, 34]}

# BFLAG_BASE=v36d: score on the v36d incumbent (q11 busy until 31 by an INTEG pair, q12 is an echo helper -> R init)
BASE_NAME = os.environ.get('BFLAG_BASE', 'v36c')
OLD = None
NONFRESH = mkcand.BASE_NONFRESH[BASE_NAME]
if BASE_NAME != 'v36c':
    lns.BASE = splice.load(Path(__file__).parent / BASE_NAME)
    also, absent = mkcand.BASE_ALSO[BASE_NAME]
    OLD = splice.prep_by_keys(lns.BASE[0], splice.load(Path(__file__).parent / 'v36c')[0], also, absent)
    lns.FIRST_TICK.update({11: 33, 12: 33, 25: 34})  # q25: echo reset R@32 in v36d


def score(state, KZ, KA):
    sol = dict(T0=state['T0'], ops=state['ops'], pivots={str(q): v for q, v in state['pivots'].items()})
    try:
        spec = mkcand.spec_from(sol, 'default', NONFRESH)
        u, d, nb = splice.build(lns.BASE[0], lns.BASE[1], spec, old=OLD)
    except AssertionError:
        return None, None
    s, _, _ = proxy.analyse(u, d, flags=sorted({e[2] for e in spec['extra'] if e[2] not in mkcand.CELLS}), starts=mkcand.starts_of(spec))
    if s['c1'] > 1e-12:
        return None, s
    return s['X2'] + KZ * s['RZ'] + KA * s['acc1'], s


def neighbourhood(state, helpers, sub, a, b, extra, N, seconds, seed, KZ, KA):
    D = len(state['ops']); T0 = state['T0']
    allc = S.CELLS + list(helpers)
    avail = {q: max(0, lns.FIRST_TICK.get(q, 0) - T0) for q in allc}
    m, sel, x, nz, E, ncx, zexp = S.build(D, avail, robust=False, helpers=helpers)
    m.ClearObjective()
    cur = {(t, tuple(e)) for t, layer in enumerate(state['ops']) for e in layer}
    free = []
    for t in range(D):
        for e in E:
            if a <= t < b and e[0] in sub and e[1] in sub:
                free.append(sel[t][e])
                m.AddHint(sel[t][e], int((t, e) in cur))
            else:
                m.Add(sel[t][e] == int((t, e) in cur))
    n0 = sum(1 for t in range(a, b) for e in E if (t, e) in cur and e[0] in sub and e[1] in sub)
    m.Add(sum(free) <= n0 + extra)
    out = []
    class CB(cp_model.CpSolverSolutionCallback):
        def on_solution_callback(self):
            ops = [[list(e) for e in E if self.Value(sel[t][e])] for t in range(D)]
            piv = {q: sum(self.Value(x[0][q][k]) << k for k in range(3)) for q in allc}
            st = dict(T0=T0, ops=ops, pivots={q: v for q, v in piv.items() if v})
            j, s = score(st, KZ, KA)
            if j is not None:
                out.append((j, st, s))
            if len(out) >= N:
                self.StopSearch()
    sv = cp_model.CpSolver()
    sv.parameters.cp_model_presolve = False
    sv.parameters.enumerate_all_solutions = True
    sv.parameters.num_search_workers = 1
    sv.parameters.max_time_in_seconds = seconds
    sv.parameters.random_seed = seed
    sv.Solve(m, CB())
    return out


def run(start, prefix, seconds, seed, helpers=(), KZ=8e-5, KA=2.6e-5):
    rng = random.Random(seed)
    state = json.loads(Path(start).read_text())
    state['pivots'] = {int(q): (v if isinstance(v, int) else sum(b << k for k, b in enumerate(v))) for q, v in state['pivots'].items()}
    D = len(state['ops'])
    J, s = score(state, KZ, KA)
    print(json.dumps(dict(start=J, **(s or {}))), flush=True)
    if J is None:
        print(json.dumps(dict(done=True, error='start state invalid on ' + BASE_NAME)), flush=True)
        return
    best = (J, state, s)
    cur = (J, state, s)
    T = 3e-8
    t0 = time.time(); it = 0
    while time.time() - t0 < seconds:
        it += 1
        k = rng.randint(4, 10)
        i = rng.randint(0, len(PATH) - k)
        sub = set(PATH[i:i + k])
        if helpers and rng.random() < 0.5:
            sub |= {h for h in helpers if any(c in sub for c in HADJ[h])}
            sub |= {h for h in helpers if any(c in sub for c in HADJ[h])}
        w = rng.randint(3, 8)
        a = rng.randint(0, D - w); b = a + w
        extra = rng.choice([0, 0, 1, 2, 3])
        res = neighbourhood(cur[1], helpers, sub, a, b, extra, 3000, 20, rng.randrange(1 << 30), KZ, KA)
        if not res:
            continue
        res.sort(key=lambda r: r[0])
        j, st, ss = res[0]
        if len(res) > 1 and abs(j - cur[0]) < 1e-15:
            # prefer a different equal-J solution for diversity
            alts = [r for r in res if abs(r[0] - j) < 1e-15 and r[1]['ops'] != cur[1]['ops']]
            if alts:
                j, st, ss = rng.choice(alts)
        if j < cur[0] or rng.random() < math.exp(-(j - cur[0]) / T):
            cur = (j, st, ss)
        if j < best[0] - 1e-13:
            best = (j, st, ss)
            o = dict(st); o['pivots'] = {str(q): v for q, v in st['pivots'].items()}; o['J'] = j; o['proxy'] = ss
            o['helpers'] = list(helpers)
            Path(prefix + '.json').write_text(json.dumps(o))
            print(json.dumps(dict(it=it, t=round(time.time() - t0), J=j, X2=ss['X2'], RZ=ss['RZ'], acc1=ss['acc1'],
                                  cx=sum(map(len, st['ops'])), nsol=len(res), sub=sorted(sub), win=[a, b])), flush=True)
        T = max(5e-9, T * 0.995)
    print(json.dumps(dict(done=True, best=best[0], iters=it)), flush=True)


if __name__ == '__main__':
    a = sys.argv
    hs = [int(q) for q in a[5].split(',')] if len(a) > 5 and a[5] not in ('', '-') else []
    kz = float(a[6]) if len(a) > 6 else 8e-5
    ka = float(a[7]) if len(a) > 7 else 2.6e-5
    run(a[1], a[2], float(a[3]), int(a[4]), hs, kz, ka)
