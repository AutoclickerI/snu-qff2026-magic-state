"""Remove nonfinal complete-circuit artifacts after exact evidence is reconciled."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent
p=H/'current_results.json';d=json.loads(p.read_text())
assert not d['missing_unchanged']
keep={'sepbc_v29c_q5_t37','sepbc_v29c_q5_t38','sepbc_v29c_q5_both','es_joint_a12_v29_2'}
removed=[]
for row in d['rows']:
 s=row['stem'];row['circuit_files_retained']=s in keep
 if s in keep:continue
 for ext in ('.qasm','.json','.plan.json','.build.json','.screen.json'):
  f=H/(s+ext)
  if f.exists():
   removed.append(dict(path=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),bytes=f.stat().st_size));f.unlink()
p.write_text(json.dumps(d,indent=2))
(H/'current_cleanup.json').write_text(json.dumps(dict(keep=sorted(keep),removed=removed,scope='Only nonfinal complete-circuit artifacts; numerical evidence, input fragments, code and prior accepted delivery retained.'),indent=2))
print('removed',len(removed),'artifacts')
