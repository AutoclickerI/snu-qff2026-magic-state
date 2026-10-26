"""Relabel the old-module receipts emitted after its source file was updated.
Numerical values are untouched; original metadata and the correction are archived.
Run only while all pass3 workers are stopped.
"""
import json,hashlib,shutil
from pathlib import Path
H=Path(__file__).resolve().parent;R=H/'res37d';SP=H/'sparse_v37';ARCH=H/'archive/provenance_fix3';ARCH.mkdir(exist_ok=True)
digest=lambda p:hashlib.sha256(p.read_bytes()).digest()
oldcore=digest(H/'archive/sparse_walsh_before_best_warm.py');newcore=digest(SP/'sparse_walsh.py')
common=digest(SP/'frontend.py')+digest(SP/'fastfill.py');adapter=digest(H/'ev37.py');changes=[]
def fix(r):
 changed=False
 if isinstance(r,dict):
  if 'evaluator_basis'in r and 'evaluator_hash'in r and 'cache_key'in r:
   bp=Path(r['evaluator_basis']);settings=json.dumps(dict(warm=str(bp.relative_to(H)),width=12),sort_keys=True).encode()
   suffix=common+digest(bp)+adapter+settings
   before=hashlib.sha256(newcore+suffix).hexdigest()[:16];after=hashlib.sha256(oldcore+suffix).hexdigest()[:16]
   if r['evaluator_hash']==before:
    r['evaluator_hash']=after;r['cache_key']=r['cache_key'].rsplit('|',1)[0]+'|'+after
    r['provenance_correction']=dict(reason='live process retained old imported evaluator while configure hashed new on-disk file',original_hash=before,actual_core_sha256=oldcore.hex())
    changes.append(dict(sha256=r.get('sha256'),from_hash=before,to_hash=after));changed=True
  for x in r.values():changed=fix(x)or changed
 elif isinstance(r,list):
  for x in r:changed=fix(x)or changed
 return changed
for f in list(R.glob('*.json'))+list(R.glob('*.jsonl')):
 raw=f.read_text();islines=f.suffix=='.jsonl';data=[json.loads(l)for l in raw.splitlines()]if islines else json.loads(raw)
 if fix(data):
  shutil.copyfile(f,ARCH/f.name);f.write_text(('\n'.join(json.dumps(x)for x in data)if islines else json.dumps(data,indent=2))+'\n')
for f in (H/'cache37d').glob('*.json'):
 r=json.loads(f.read_text())
 if fix(r):
  shutil.copyfile(f,ARCH/('cache_'+f.name));new=f.with_name(hashlib.sha256(r['cache_key'].encode()).hexdigest()+'.json');new.write_text(json.dumps(r,indent=2)+'\n');f.unlink()
(R/'provenance_correction.json').write_text(json.dumps(dict(changes=changes,numerical_values_changed=False,old_core_sha256=oldcore.hex(),new_core_sha256=newcore.hex()),indent=2)+'\n')
print(json.dumps(dict(corrected_receipts=len(changes),unique_hashes=len({r['sha256']for r in changes}))))
