from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent
names=json.loads((H/'shortlist.json').read_text());seen={}
for name in names:
 p=H/f'{name}.qasm'
 if p.exists():seen[hashlib.sha256(p.read_bytes()).hexdigest()]=name
rows=json.loads((H/'refine_results_0.json').read_text());added=[]
for r in sorted(rows,key=lambda r:r['proxy']):
 name=r['name'];h=hashlib.sha256((H/f'{name}.qasm').read_bytes()).hexdigest()
 if h not in seen:seen[h]=name;added.append(name)
missing=[n for n in names if not (H/f'{n}.screen.json').exists()]
(H/'refine_shortlist.json').write_text(json.dumps(added+missing,indent=2));print(dict(refinements=len(rows),distinct_added=len(added),missing_screens=missing,names=added))
