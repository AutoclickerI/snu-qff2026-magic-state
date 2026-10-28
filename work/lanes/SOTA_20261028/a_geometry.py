"""Construct actual nearest-neighbour A preparations on a selected geometry.

State-specific tree elimination generates proposals. The score here only
selects preparation depth/CX; complete circuit noise remains the decision.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse, json, random, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT/'work/lanes/NATIVE2_20261027'),
                str(ROOT/'work/lanes/END2_20261027')]
import a_factory as af
import a_factory_search as search
import stim


def verify(row, aa):
    sim = stim.TableauSimulator()
    for op in row['operations']:
        kind, qs = op['kind'], op['qs']
        if kind == 'RX':
            sim.reset(*qs); sim.h(*qs)
        elif kind == 'R': sim.reset(*qs)
        elif kind == 'CX': sim.cx(*qs)
        elif kind == 'H': sim.h(*qs)
        else: raise ValueError(kind)
    values = []
    for axis, masks in [('X', [85, 102, 120, 7]), ('Z', [85, 102, 120])]:
        for mask in masks:
            pauli = stim.PauliString(36)
            for i, q in enumerate(aa):
                if mask >> i & 1: pauli[q] = axis
            values.append(dict(axis=axis, mask=mask,
                               expectation=sim.peek_observable_expectation(pauli)))
    assert all(r['expectation'] == 1 for r in values), values
    return values


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--geometry', default=str(HERE/'tile_geometry_free2.json'))
    ap.add_argument('--release')
    ap.add_argument('--trials', type=int, default=4000)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--output', default=str(HERE/'a_geometry.json'))
    args = ap.parse_args()
    started = time.perf_counter()
    roles = json.loads(Path(args.geometry).read_text())['roles']
    aa = roles['A']
    af.A = aa
    af.CELLS = sorted(aa)
    af.ADJ = {q: [v for v in aa if abs(q//6-v//6)+abs(q%6-v%6)==1] for q in aa}
    af.TARGET = {q: aa.index(q)+1 for q in aa}
    releases = {q: 0 for q in aa}
    if args.release:
        doc = json.loads(Path(args.release).read_text())
        releases = {q: int(doc['release'][str(q)]) for q in aa}
    states = {q: {} for q in aa}  # Explicit noisy preparation for every input.
    rng = random.Random(args.seed)
    candidates, seen = [], set()
    for trial in range(args.trials):
        direct = bool(trial % 2)
        result = search.construct(rng, direct)
        if result is None: continue
        initial, gates = result
        row = search.schedule(initial, gates, releases, states, rng, direct)
        key = tuple((o['time'], o['kind'], tuple(o['qs'])) for o in row['operations'])
        if key in seen: continue
        seen.add(key)
        row.update(trial=trial, initial_rows=initial, A=aa)
        candidates.append(row)
        if len(candidates) > 250:
            candidates.sort(key=lambda r: (r['a_ready'], r['cx']))
            candidates = candidates[:100]
    candidates.sort(key=lambda r: (r['a_ready'], r['cx']))
    for row in candidates[:20]:
        gates = [tuple(o['qs']) for o in row['operations'] if o['kind']=='CX']
        opt = search.schedule(row['initial_rows'], gates, releases, states, rng,
                              row['direct'], cp_seconds=1)
        row.update(opt)
        row['stabilizers'] = verify(row, aa)
    candidates.sort(key=lambda r: (r['a_ready'], r['cx']))
    output = dict(geometry=args.geometry, roles=roles, release=releases,
                  trials=args.trials, seconds=time.perf_counter()-started,
                  candidates=candidates[:20],
                  scope='Actual native A modules; no complete circuit score claimed.')
    Path(args.output).write_text(json.dumps(output, indent=2)+'\n')
    print(json.dumps(dict(seconds=output['seconds'], proposals=len(seen),
         best=[{k:r[k] for k in ('a_ready','cx','direct','plus_inputs')} for r in candidates[:10]])), flush=True)

if __name__=='__main__': main()
