"""Merge content-addressed receipts and completed raw evaluations; verify saved QASM hashes."""
import hashlib,json
from pathlib import Path
H=Path(__file__).resolve().parent;TAU=3.761821654835085e-5
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records={}
for p in [H/'results.json',H/'results.jerry.snapshot.json']:
    if p.exists():records.update(json.loads(p.read_text()))
for p in (H/'priced').glob('*.json'):
    r=json.loads(p.read_text());records[r['sha256']]=r
recovered=0;missing=[]
for dirname in ['sparse','sparse40','sparse_fast','sparse_r45','sparse_mi','sparse_bc','sparse_repair','sparse_port','sparse_checked','sparse_joint','sparse_cjoint']+[p.name for p in H.glob('ev_*') if p.is_dir()]:
    ev=H/dirname
    if not ev.exists():continue
    hashes={f:sha(ev/f) for f in ['sparse_walsh.py','frontend.py','fastfill.py','basis_warm.json']}
    for p in ev.glob('*_canonical_sparse_result.json'):
        out=json.loads(p.read_text());stem=Path(out['source'])
        if not stem.is_absolute():
            choices=[H/stem,ev/stem,H.parents[2]/stem]
            stem=next((s.resolve() for s in choices if s.with_suffix('.qasm').exists()),choices[0])
        if not stem.with_suffix('.qasm').exists():missing.append(str(stem));continue
        digest=sha(stem.with_suffix('.qasm'));log=H/'logs'/f'{stem.name}_{digest[:12]}.allorders.txt'
        if digest in records:
            meta=json.loads(stem.with_suffix('.json').read_text())
            assert records[digest]['data_qubits']==meta['data_qubits'],('metadata collision',digest)
            continue
        if not log.exists():missing.append(str(log));continue
        try:last=json.loads(log.read_text().splitlines()[-1])
        except (ValueError,IndexError):continue
        if 'loss' not in last or abs(last['loss']-out['loss'])>1e-14:continue
        meta=json.loads(stem.with_suffix('.json').read_text())
        if digest in records:
            assert records[digest]['data_qubits']==meta['data_qubits'],('metadata collision',digest)
            continue
        records[digest]=dict(path=str(stem.with_suffix('.qasm').relative_to(H)),sha256=digest,data_qubits=meta['data_qubits'],evaluator=hashes,phantom=dirname=='sparse40',loss=out['loss'],acceptance=out['acceptance'],J_tau=out['acceptance']*(out['loss']-TAU),seconds=out['seconds'],log=str(log.relative_to(H)),moved=meta.get('global_change','phantom reference' if dirname=='sparse40' else 'saved full-circuit edit'),kernel_omission_bound=out.get('conditional_loss_kernel_omission_bound'))
        recovered+=1
for digest,r in records.items():
    r['J_v36h']=r['acceptance']*(r['loss']-3.815473322483099e-5)
    r['J_tau']=r['acceptance']*(r['loss']-TAU);r['tau']=TAU
    p=H/r['path']
    if not p.exists():missing.append(str(p));continue
    assert sha(p)==digest,('priced QASM overwritten',str(p),digest,sha(p))
runtime=json.loads((H/'runtime_eligibility.json').read_text()) if (H/'runtime_eligibility.json').exists() else {}
for digest,r in records.items():
    if digest in runtime:r['runtime_screen']=runtime[digest]
tmp=H/'results.collect.tmp.json';tmp.write_text(json.dumps(records,indent=2)+'\n');tmp.replace(H/'results.json')
(H/'logs/collection.json').write_text(json.dumps(dict(records=len(records),recovered=recovered,missing=sorted(set(missing))),indent=2)+'\n')
print(json.dumps(dict(records=len(records),recovered=recovered,missing=len(set(missing)))))
