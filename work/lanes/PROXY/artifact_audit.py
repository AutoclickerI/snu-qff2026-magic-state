"""Verify the retained review artifacts, then archive generated search candidates."""
from cycles import *
import tarfile,re
KEEP={'cycle_0058','neighbor_006','neighbor_048','neighbor_049','reference_r86'}
rows=[]
for name in sorted(KEEP):
 text=(HERE/f'{name}.qasm').read_text();meta=json.loads((HERE/f'{name}.json').read_text())
 if name=='reference_r86':assert text==SRC
 else:
  m=Cycle(meta['layout'],meta['leaves'],meta['orient']);assert text==m.text(meta['times']),(name,'text/meta mismatch')
 a=audit(text)
 r=tprep.check(text,meta['data_qubits'],shots=10**6,seed=0);assert r.passed,str(r)
 out=dict(name=name,sha256=hashlib.sha256(text.encode()).hexdigest(),prefix=a,passed=r.passed,shots=10**6,seed=0,acceptance=r.acceptance,score=r.score,n_2q=r.n_2q,report=str(r))
 (HERE/f'{name}.check.json').write_text(json.dumps(out,indent=2));rows.append(out)
paths=[p for p in HERE.iterdir() if re.fullmatch(r'(cycle_\d+|refine_\d+|neighbor_\d+)\.(qasm|json)',p.name) and p.stem not in KEEP]
if paths:
 archive=HERE/'generated_candidates.tar.gz'
 assert not archive.exists(),'Archive already exists; refusing to overwrite earlier evidence'
 with tarfile.open(archive,'w:gz') as tar:
  for p in paths:tar.add(p,arcname=p.name)
 with tarfile.open(archive,'r:gz') as tar:
  assert len(tar.getmembers())==len(paths)
  for p in paths:assert tar.extractfile(p.name).read()==p.read_bytes()
 for p in paths:p.unlink()
(HERE/'artifact_audit.json').write_text(json.dumps(dict(retained=rows,archived_files=len(paths),archive='generated_candidates.tar.gz'),indent=2));print(dict(retained=len(rows),archived=len(paths)),flush=True)
