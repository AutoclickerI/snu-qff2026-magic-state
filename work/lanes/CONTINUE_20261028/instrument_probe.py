"""Exact boundary-fault response; no other noise and no candidate mutations.

A virtual identity clock supplies fault signatures only. The resulting table
tests the measurement instrument, which raw target-state correctness alone
does not specify. This is not a finite-p score or a full equivalence proof.
"""
import os
for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[k] = '1'
import copy, hashlib, itertools, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT/'work/tools'), str(ROOT/'work/lanes/EXPAND2_20261027'),
                str(ROOT/'work/lanes/FRAME20261027')]
import frontend_axis as f
import frame_tools as ft
ft.f = f

def probe(stem, cut=41):
    text = stem.with_suffix('.qasm').read_text()
    data = json.loads(stem.with_suffix('.json').read_text())['data_qubits']
    ops, dets = f.parse_current(text)
    ops = copy.deepcopy(ops)
    for op in ops:
        if op.time >= cut: op.time += 1
    ops += [f.Op('ID', (q,), cut, line=-1) for q in data]
    ops.sort(key=lambda o: (o.time, o.kind, o.qs))
    m = ft.frame_model(ops, dets, data, ft.parse_frames(text), False)
    eng = f.Engine(m)
    assert abs(eng.A0-1) < 1e-10
    faults = {}
    for q in data:
        rows = [x for x in m.faults if m.labels[x['ins']].line == -1 and x['qs'] == [q]]
        after = max(x['jl'] for x in rows)
        rows = [x for x in rows if x['jl'] == after]
        assert {x['pauli'] for x in rows} == set('XYZ')
        faults.update({(q, x['pauli']): x for x in rows})
    cache = {}
    def response(pattern):
        s = d = e = 0
        for q, p in pattern:
            x = faults[q, p]
            s ^= x['s']; d ^= x['d']; e ^= x['e']
        if (s, d) not in cache: cache[s, d] = eng.ntable(s, d)
        a, nums = cache[s, d]
        n = 0.0 if nums is None else float(nums[e])
        return dict(errors=pattern, acceptance=float(a), loss_numerator=n,
                    conditional_loss=n/a if a > 1e-12 else None)
    singles = [response([(q, p)]) for p in 'XYZ' for q in data]
    pairs = [response([(a, p), (b, p)]) for p in 'XYZ' for a, b in itertools.combinations(data, 2)]
    summary = {}
    for p in 'XYZ':
        ss = [r for r in singles if r['errors'][0][1] == p]
        pp = [r for r in pairs if r['errors'][0][1] == p]
        summary[p] = dict(accepted_singles=sum(r['acceptance'] > 1e-10 for r in ss),
                          accepted_pairs=sum(r['acceptance'] > 1e-10 for r in pp),
                          harmful_pairs=sum(r['loss_numerator'] > 1e-10 for r in pp))
    return dict(stem=str(stem.relative_to(ROOT)), qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),
                before_original_clock=cut, summary=summary, singles=singles, same_axis_pairs=pairs,
                scope='Only the stated boundary Pauli errors, all other noise absent. Not a score or full instrument-equivalence proof.')

if __name__ == '__main__':
    stems = [next((ROOT/'work/lanes/SOTA_20261028/native_best').glob('*.qasm')).with_suffix(''),
        ROOT/'work/lanes/MEASURED_BC_20261028/bczero_0_4_2c86d935cb2c4c71_d6_20_19_10_2_22_16',
        ROOT/'work/lanes/MEASURED_BC_20261028/restore_bc_89941548f8d603e1_d6_20_19_10_2_22_16']
    results = [probe(s) for s in stems]
    (HERE/'instrument_probe.json').write_text(json.dumps(results, indent=2)+'\n')
    print(json.dumps([dict(stem=r['stem'], summary=r['summary']) for r in results], indent=2))
