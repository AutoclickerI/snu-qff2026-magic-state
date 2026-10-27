"""Native 15-T arithmetic with measured, freshly restarted Clifford flags.

The five phase coordinates are unchanged. A sixth, unused phase coordinate can
be introduced on a zero cell, used by native parity arithmetic, and removed only
when it is a physically isolated plus factor. In forward time this is a fresh
RX preparation followed by MX and reset. Different periods have independent
records and need no coherent movement of the flag between available zero cells.
"""
import argparse, heapq, json, math, os, random, sys
from pathlib import Path
for _key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_key] = '1'
H = Path(__file__).resolve().parent
sys.path.insert(0, str(H.parent / 'PREFIX20261027'))
sys.path.insert(0, str(H.parent / 'T14'))
import synth
from qcirc import adjacent, save
from search_phase import singles
from qtools import price
from qtools.validity import raw_check
A, D = synth.A, synth.D
GOALS = synth.goals(24)
TARGET = set(GOALS)
GI = {v: i for i, v in enumerate(GOALS)}
CELLS = list(synth.CELLS)
INIT = synth.INIT
EDGES = synth.EDGES


def configure(n):
    global CELLS, INIT, EDGES
    CELLS = list(synth.CELLS) + ([10, 13] if n >= 11 else []) + ([4] if n >= 12 else [])
    INIT = tuple(9 + A.index(q) if q in A else 16 if q == 3 else 0 for q in CELLS)
    EDGES = [(a, b) for a, q in enumerate(CELLS) for b, r in enumerate(CELLS) if adjacent(q, r)]


def isolated(rows):
    carrying = [i for i, r in enumerate(rows) if r & 32]
    return carrying[0] if len(carrying) == 1 and rows[carrying[0]] == 32 else None


def allowed(r):
    return r == 0 or r in TARGET or (r & 32 and r != 40)


def apply_action(rows, action):
    out = list(rows)
    k, a, b = action
    if k == 'cx':
        out[b] ^= out[a]
    elif k == 'up':
        assert out[a] == 0 and not any(r & 32 for r in out)
        out[a] = 32
    elif k == 'down':
        assert isolated(out) == a
        out[a] = 0
    elif k == 'move':
        assert isolated(out) == a and out[b] == 0
        out[a], out[b] = 0, 32
    elif k == 'read':
        assert isolated(out) == a
    else:
        raise ValueError(action)
    return tuple(out)


def next_times(times, action):
    k, a, b = action
    tt = list(times)
    if k == 'cx':
        tt[a] = tt[b] = max(tt[a], tt[b]) + 1
    elif k == 'up':
        tt[a] += 2  # forward MX followed by reset
    elif k in ('down', 'read'):
        tt[a] += 1
    elif k == 'move':
        tt[a] += 1
        tt[b] += 2
    return tuple(tt)


def search(seed=0, width=1200, maxdepth=80, min_periods=2, depth_weight=.16):
    rng = random.Random(seed)
    cov = synth.coverage(INIT, GI)
    # rows, covered axes, backward actions, dirty flag, completed periods,
    # per-wire dependency depths, CX count, integrated exposed-row cost.
    front = [(INIT, cov, [], False, 0, (0,) * len(CELLS), 0, 0.)]
    seen = {}
    solutions = []
    first = None
    for depth in range(1, maxdepth + 1):
        keep = {}
        for rows, cov, path, dirty, periods, times, ncx, exposure in front:
            active = any(r & 32 for r in rows)
            iso = isolated(rows)
            actions = [('cx', a, b) for a, b in EDGES if rows[a] and allowed(rows[a] ^ rows[b])]
            if not active:
                actions += [('up', a, -1) for a, r in enumerate(rows) if not r]
            elif iso is not None and dirty:
                actions.append(('down', iso, -1))
                actions += [('move', iso, b) for b, r in enumerate(rows) if not r]
                actions.append(('read', iso, -1))
            for action in actions:
                k, a, b = action
                nr = apply_action(rows, action)
                nc = cov | synth.coverage(nr, GI)
                pp = path + [action]
                nt = next_times(times, action)
                ccx = ncx + (k == 'cx')
                ndirty = dirty or (k == 'cx' and bool((rows[a] | rows[b]) & 32))
                nperiods = periods
                if k in ('down', 'move', 'read'):
                    nperiods += 1
                    ndirty = False
                elif k == 'up':
                    ndirty = False
                # Count the cost of a qubit waiting while the dependency depth
                # grows. This is only a search proxy; all ranking uses price().
                extra_depth = max(nt) - max(times)
                nexp = exposure + extra_depth * sum(r != 0 for r in rows)
                missing = 15 - nc.bit_count()
                active2 = any(r & 32 for r in nr)
                rank = 6 if active2 else 5
                nz = sum(r != 0 for r in nr)
                if not missing and nz == 5 and not active2 and nperiods >= min_periods:
                    solutions.append(dict(rows=nr, actions=pp, goals=GOALS, seed=seed,
                                          cells=CELLS, source_cx=ccx, periods=nperiods,
                                          cx_depth=max(nt), exposure_proxy=nexp,
                                          dynamic_flag=True))
                    first = depth if first is None else first
                    continue
                key = (nr, nc, ndirty, min(nperiods, min_periods))
                value = ccx + .3 * max(nt) + .005 * nexp
                if seen.get(key, math.inf) <= value - 1e-9:
                    continue
                seen[key] = value
                xor = {nr[c] ^ nr[d] for c, d in EDGES}
                near = sum(v in xor for v in GOALS if not nc >> GI[v] & 1)
                spread = max(0, sum(bool(r & 32) for r in nr) - 1)
                score = (5 * missing + (nz - rank) * (.85 if missing else 3.5)
                         + .055 * ccx + depth_weight * max(nt) + .003 * nexp
                         + .16 * spread - .17 * near + .05 * active2
                         + .12 * max(0, min_periods - nperiods) + rng.random() * .55)
                if key not in keep or score < keep[key][0]:
                    keep[key] = (score, nr, nc, pp, ndirty, nperiods, nt, ccx, nexp)
        front = [(r, c, p, d, n, t, x, e) for _, r, c, p, d, n, t, x, e in
                 heapq.nsmallest(width, keep.values(), key=lambda z: z[0])]
        if depth % 5 == 0:
            lead = front[0] if front else None
            print('dynamic', len(CELLS), seed, depth, len(front), len(solutions),
                  (15 - lead[1].bit_count(), sum(r != 0 for r in lead[0]),
                   lead[4], lead[6], max(lead[5])) if lead else None, flush=True)
        if not front or first is not None and depth >= first + 5:
            break
        if len(seen) > 650000:
            seen = {(r, c, d, min(n, min_periods)): x + .3 * max(t) + .005 * e
                    for r, c, p, d, n, t, x, e in front}
    unique = {tuple(tuple(x) for x in r['actions']): r for r in solutions}
    return sorted(unique.values(), key=lambda r: (r['cx_depth'] + .12 * r['source_cx'],
                                                 r['exposure_proxy']))[:6]


def build(rec, name):
    configure(len(rec['cells']))
    rows = INIT
    states = [rows]
    for action in rec['actions']:
        rows = apply_action(rows, action)
        states.append(rows)
    assert sum(r != 0 for r in rows) == 5 and not any(r & 32 for r in rows)
    choices = {v: [] for v in GOALS}
    for k, rr in enumerate(states):
        for i, v in enumerate(rr):
            if v in choices:
                choices[v].append((k, i))
    rng = random.Random(rec.get('phase_seed', 0))
    mode = rec.get('phase_mode', 'first')
    chosen = {v: opts[0] if mode == 'first' else opts[-1] if mode == 'last' else rng.choice(opts)
              for v, opts in choices.items()}
    units = []
    last = {q: -1 for q in range(36)}
    dets = []
    records = []
    bit = 900

    def add(kind, qs, record=None):
        tick = max(last[q] for q in qs) + 1
        units.append(dict(k=kind, q=qs, t=tick, b=record))
        for q in qs:
            last[q] = tick

    for q, r in zip(CELLS, rows):
        add('RX' if r else 'R', (q,))
    previous = None
    for k in range(len(states) - 1, -1, -1):
        for v, (kk, i) in chosen.items():
            if k == kk:
                add('TDG', (CELLS[i],))
        if k == 0:
            break
        kind, a, b = rec['actions'][k - 1]
        if kind == 'cx':
            add('CX', (CELLS[a], CELLS[b]))
        elif kind == 'down':
            add('RX', (CELLS[a],))
            previous = None
        elif kind in ('up', 'move', 'read'):
            measured = b if kind == 'move' else a
            add('MX', (CELLS[measured],), bit)
            dets.append([bit] if previous is None else [previous, bit])
            records.append(dict(bit=bit, qubit=CELLS[measured], action=kind))
            previous = bit
            bit += 1
            if kind in ('up', 'move'):
                add('R', (CELLS[measured],))
                previous = None
            if kind == 'move':
                add('RX', (CELLS[a],))
        else:
            raise ValueError(kind)
    for u in units[:len(CELLS)]:
        touch = [v['t'] for v in units[len(CELLS):] if u['q'][0] in v['q']]
        if touch:
            u['t'] = min(touch) - 1
    flagt = max(last.values()) + 1
    for u in units[:len(CELLS)]:
        if not any(u['q'][0] in v['q'] for v in units[len(CELLS):]):
            u['t'] = flagt - 1
    units.append(dict(k='MX', q=(3,), t=flagt, b=500))
    dets.append([500])
    zeros = [q for q in CELLS if q not in A + [3]]
    for j, q in enumerate(zeros):
        units.append(dict(k='M', q=(q,), t=flagt, b=600 + j))
        dets.append([600 + j])
    hop = flagt + 1
    for d in D:
        units.append(dict(k='R', q=(d,), t=hop, b=None))
    for a, d in zip(A, D):
        units.append(dict(k='CX', q=(a, d), t=hop + 1, b=None))
        units.append(dict(k='CX', q=(d, a), t=hop + 2, b=None))
    _, suffix, sdets, _ = synth.split_suffix()
    dets += sdets
    end = hop + 2
    busy = {q: min(u['t'] for u in suffix if q in u['q']) for q in {q for u in suffix for q in u['q']}}
    shift = max([end + 1 - busy[q] for q in set(CELLS + D) if q in busy]
                + [-min(u['t'] for u in suffix)])
    for u in suffix:
        u['t'] += shift
    for j, a in enumerate(A):
        if end + 1 < busy.get(a, 999) + shift:
            units.append(dict(k='M', q=(a,), t=end + 1, b=502 + j))
            dets.append([502 + j])
    units += suffix
    start = min(u['t'] for u in units)
    for u in units:
        u['t'] -= start
    return save(H / 'cand' / name, units, dets, D,
                dict(source='15T native arithmetic with fresh measured Clifford flags',
                     synthesis=rec, phase_locations=chosen, flag_records=records))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cells', type=int, default=9, choices=[9, 11, 12])
    ap.add_argument('--seeds', type=int, default=3)
    ap.add_argument('--width', type=int, default=1200)
    ap.add_argument('--depth', type=int, default=80)
    a = ap.parse_args()
    configure(a.cells)
    prefix = f'dynamic{a.cells}'
    results = []
    best = 1.
    number = 0
    for seed in range(a.seeds):
        networks = search(seed, a.width, a.depth)
        (H / f'{prefix}_network_s{seed}.json').write_text(json.dumps(networks, indent=2) + '\n')
        for net in networks[:3]:
            for mode, phase_seed in [('first', 0), ('last', 0), ('random', 1), ('random', 2)]:
                rec = dict(net, phase_mode=mode, phase_seed=phase_seed)
                name = f'{prefix}_{number}_{mode}{phase_seed}'
                try:
                    st = build(rec, name)
                    raw = raw_check(st.with_suffix('.qasm').read_text(), D)
                    result = dict(stem=str(st), cells=a.cells, source_cx=net['source_cx'],
                                  periods=net['periods'], cx_depth=net['cx_depth'], raw=raw)
                    if raw['ok']:
                        c1, harmful = singles(st)
                        result.update(c1=c1, harmful=harmful)
                        if c1 < 1e-5:
                            p = price(st, 1)
                            result.update(loss=p['loss'], acceptance=p['acceptance'])
                            if p['acceptance'] >= .5002 and p['loss'] < best:
                                best = p['loss']
                                (H / f'{prefix}_best.json').write_text(json.dumps(result, indent=2) + '\n')
                    print(json.dumps(result), flush=True)
                    results.append(result)
                except Exception as ex:
                    print('ERROR', name, repr(ex), flush=True)
                    results.append(dict(name=name, error=repr(ex)))
                (H / f'{prefix}_results.json').write_text(json.dumps(results, indent=2) + '\n')
            number += 1


if __name__ == '__main__':
    main()
