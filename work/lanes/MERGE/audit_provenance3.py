import json,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;R=H/'res37d';SP=H/'sparse_v37';dig=lambda p:hashlib.sha256(p.read_bytes()).digest()
cores={'original':H/'archive/sparse_walsh_before_best_warm.py','optimized':SP/'sparse_walsh.py'}
common=dig(SP/'frontend.py')+dig(SP/'fastfill.py');adapter=dig(H/'ev37.py');registry={}
for folder in [H/'res',H/'res37c',R,SP]:
 for f in folder.glob('basis*.json'):
  b=json.loads(f.read_text())
  if 'bases'not in b:continue
  for name,core in cores.items():
   pre=dig(core)+common+dig(f)+adapter
   configurations=[('default',b''),('configured',json.dumps(dict(warm=str(f.relative_to(H)),width=12),sort_keys=True).encode())]
   for mode,suffix in configurations:
    k=hashlib.sha256(pre+suffix).hexdigest()[:16];registry.setdefault(k,[]).append(dict(core=name,mode=mode,basis=str(f.relative_to(H)),core_sha256=dig(core).hex(),basis_sha256=dig(f).hex()))
checked=0;errors=[]
for f in R.glob('*.jsonl'):
 for i,ln in enumerate(f.read_text().splitlines(),1):
  r=json.loads(ln)
  if 'cache_key'not in r:continue
  checked+=1;k=r['evaluator_hash']
  if k not in registry:errors.append(dict(file=f.name,line=i,hash=k,error='unknown evaluator configuration'));continue
  expected=r['sha256']+'|'+','.join(map(str,r['data_qubits']))+'|'+k
  if r['cache_key']!=expected:errors.append(dict(file=f.name,line=i,error='cache key mismatch'))
  if 'basis_sha256'in r and dig(Path(r['evaluator_basis'])).hex()!=r['basis_sha256']:errors.append(dict(file=f.name,line=i,error='basis changed after receipt'))
  if 'provenance_correction'in r:
   claimed=r['provenance_correction']['actual_core_sha256']
   if not any(c['core_sha256']==claimed for c in registry[k]):errors.append(dict(file=f.name,line=i,error='correction does not bind actual old core'))
out=dict(checked_receipts=checked,errors=errors,configurations=registry)
(R/'provenance_audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(checked=checked,error_count=len(errors),unknown_hashes=sorted({r.get('hash','')for r in errors}),first_errors=errors[:3])))
assert not errors
