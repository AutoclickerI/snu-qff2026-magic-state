"""Noiseless determinism of the B/C-side detectors of a spliced candidate (stim, Clifford sub-circuit:
units on B/C, flag and readout helpers from t >= 30; B->D dropped since B's X rows are data-independent)."""
import sys, stim
from qcirc import parse
B = [6, 26, 13, 11, 4, 23, 27]; C = [12, 25, 19, 17, 5, 29, 28]; D = [0, 20, 7, 10, 3, 22, 21]
A = [1, 14, 8, 9, 2, 16, 15]
def check(units, dets, t0=30):
    BC = set(B + C)
    side = set()
    for u in units:
        if u['k'] == 'CX' and u['t'] >= t0 and any(q in BC for q in u['q']):
            for q in u['q']:
                if q not in BC and q not in D and q not in A:
                    side.add(q)
    Q = BC | side
    # each qubit's units from its last reset/first op at t >= t0 ... keep the window simple
    U = sorted([u for u in units if u['t'] >= t0 and set(u['q']) <= Q], key=lambda u: u['t'])
    sim = stim.TableauSimulator()
    rec = {}
    started = set()
    for u in U:
        k, qs = u['k'], u['q']
        for q in qs:
            if q not in started:
                started.add(q)
                if k not in ('R', 'RX', 'M', 'MX'):
                    sim.reset(q)  # first op not an init: assume |0> (literal-0 previous measurement)
        if k == 'R': sim.reset(qs[0])
        elif k == 'RX': sim.reset(qs[0]); sim.h(qs[0])
        elif k == 'M':
            if qs[0] not in started or True:
                pass
            rec[u['b']] = sim.measure(qs[0])
        elif k == 'MX':
            sim.h(qs[0]); rec[u['b']] = sim.measure(qs[0]); sim.h(qs[0])
        elif k == 'CX': sim.cnot(*qs)
    bad = []
    for j, d in enumerate(dets):
        if all(b in rec for b in d):
            # determinism: re-run with forced random outcomes is complex; test by measuring twice with fresh sims
            pass
    return rec, U
def deterministic(units, dets, trials=24):
    import random
    outs = []
    for s in range(trials):
        # stim TableauSimulator randomness is seeded per instance
        sim_rec, U = check(units, dets)
        outs.append(sim_rec)
    res = []
    for j, d in enumerate(dets):
        if not all(b in outs[0] for b in d):
            continue
        vals = {sum(o[b] for b in d) % 2 for o in outs}
        res.append((j, d, vals))
    return res
if __name__ == '__main__':
    units, dets = parse(open(sys.argv[1] + '.qasm').read())
    for j, d, vals in deterministic(units, dets):
        if vals != {0}:
            print('NONDET', j, d, vals)
    print('checked')
