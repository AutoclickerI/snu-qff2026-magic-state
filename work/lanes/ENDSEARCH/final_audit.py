import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent
ledger=json.loads((H/'results.json').read_text());checked=0
import sys
sys.path.insert(0,str(H/'sparse'))
import frontend as fa
for sha,z in ledger.items():
    assert len(sha)==64
    for path in z['qasm_paths']:
        p=H/path;src=p.read_text();assert hashlib.sha256(p.read_bytes()).hexdigest()==sha
        ops,dets=fa.parse_current(src);native,_=fa.native_text(ops);_,steps,_=fa.schedule(native)
        assert all(len(s)==1 and s[0][1]==o.time for s,o in zip(steps,ops)),p
        bits={o.bit for o in ops if o.bit is not None};assert all(set(d)<=bits for d in dets)
        checked+=1
for p in (H/'cand').glob('*.qasm'):
    assert hashlib.sha256(p.read_bytes()).hexdigest() in ledger
    assert p.with_suffix('.json').exists()
assert len((H/'REPORT.md').read_text().splitlines())<=100
rows=[r for p in (H/'logs').glob('oracle*.jsonl') for r in map(json.loads,p.read_text().splitlines())]
mins=dict(overall=min(r['lower_bound_p2'] for r in rows),tree=min(r['lower_bound_p2'] for r in rows if r['graph']=='tree'),unmeasured=min(r['lower_bound_p2'] for r in rows if r['terminal']=='unmeasured'))
assert abs(mins['overall']-25.6666666666667)<1e-10,mins
assert abs(mins['tree']-27.2066666666667)<1e-10,mins
assert abs(mins['unmeasured']-28.7466666666667)<1e-10,mins
out=dict(hash_entries=len(ledger),qasm_paths_checked=checked,candidate_files=len(list((H/'cand').glob('*'))),oracle_minima=mins,report_lines=len((H/'REPORT.md').read_text().splitlines()))
(H/'final_audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
