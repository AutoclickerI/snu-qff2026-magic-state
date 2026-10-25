"""Bounded current-v36g probe, not an exhaustive resource optimization.

Enumerates removal of one or two of r3's 56 B/C preparation CXs. Keeps the
exact rank-three pure endpoint and screens all proxy resource Pauli singles.
The proxy is diagnostic only; any retained physical circuit needs full-noise
whole-prefix pricing and official ideal/class checks.
"""
from pathlib import Path
from itertools import combinations
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(HERE/'source/work/lanes/T14'), str(HERE/'source/work/lanes/BFLAG')]
from qcirc import parse, emit
import proxy

base = ROOT/'quantumn_review11/work/lanes/MAIN/v36g.qasm'
units, dets = parse(base.read_text())
meta = json.loads(base.with_suffix('.json').read_text())
resource = json.loads((HERE/'source/work/lanes/BFLAG/syn/r3.json').read_text())
BC = proxy.B + proxy.C
indices = [i for i,u in enumerate(units) if u['k']=='CX' and 33<=u['t']<44 and set(u['q'])<=set(BC)]
assert len(indices) == 56
starts = {}
for q in BC:
    first = min(units[i]['t'] for i in indices if q in units[i]['q'])
    starts[q] = max(u['t'] for u in units if u['q']==(q,) and u['k'] in ('R','RX','M','MX') and u['t']<first)


def endpoint(removed):
    rows = {q: resource['pivots'].get(str(q),0) for q in BC}
    for i in indices:
        if i not in removed:
            a,b = units[i]['q']
            rows[b] ^= rows[a]
    return rows


target = endpoint(set())
assert target == {q:i+1 for group in (proxy.B,proxy.C) for i,q in enumerate(group)}
baseline = proxy.analyse(units, dets, starts=starts)[0]
rows = []
tested = 0
end_ok = 0
for count in (1,2):
    for deleted in combinations(indices,count):
        tested += 1
        deleted = set(deleted)
        if endpoint(deleted) != target:
            continue
        end_ok += 1
        candidate = [u for i,u in enumerate(units) if i not in deleted]
        score, faults, _ = proxy.analyse(candidate, dets, starts=starts)
        if score['c1'] > 1e-12:
            continue
        accepted_nonzero = sorted({proxy.sig(data) for _,_,(df,data) in faults if not df and proxy.sig(data)})
        rec = {'deleted': [dict(index=i, **units[i]) for i in sorted(deleted)],
               'proxy': score, 'accepted_nonzero_x_signatures': accepted_nonzero,
               'delta_proxy_X2_plus_X2leak': score['X2']+score['X2leak']-baseline['X2']-baseline['X2leak'],
               'delta_leak': score['leak']-baseline['leak'],
               'scope': 'Endpoint and local Pauli proxy only; not a full noisy gain.'}
        rows.append(rec)
rows.sort(key=lambda r:r['delta_proxy_X2_plus_X2leak'])
for rank,rec in enumerate(rows[:8]):
    deleted = {x['index'] for x in rec['deleted']}
    stem = HERE/f'resource_delete_{rank:02d}'
    stem.with_suffix('.qasm').write_text(emit([u for i,u in enumerate(units) if i not in deleted],dets))
    stem.with_suffix('.json').write_text(json.dumps({'data_qubits':meta['data_qubits'], 'base':'v36g', **rec},indent=2)+'\n')
    rec['candidate_stem'] = str(stem.relative_to(ROOT))
receipt = {'scope':'All one/two-CX deletions among fixed r3 56 preparation CXs only.',
           'total_tested':tested,'endpoint_preserved':end_ok,'proxy_c1_safe':len(rows),
           'baseline_proxy':baseline, 'starts':starts, 'candidates':rows}
(HERE/'resource_deletion_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='candidates'},indent=2))
for row in rows[:8]:
    print(json.dumps(row))
