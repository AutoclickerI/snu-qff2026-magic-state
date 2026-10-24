"""Archive exact tested plans; keep only the two R45 finalists as loose circuits."""
from pathlib import Path
import json,gzip,hashlib
V=Path(__file__).resolve().parent;d=json.loads((V/'results.json').read_text());assert not d['pending'];keep={'commute_tail','sensitivity_tail'};archive={};removed=[]
for r in d['rows']:
 name=r['stem']
 if name in keep:continue
 st=V/name;archive[name]=dict(plan=json.loads(st.with_suffix('.plan.json').read_text()),build=r.get('build'),qasm_sha256=hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest())
 can=V/(name+'_detorder.qasm')
 if can.exists():archive[name]['analytical_reference_qasm']=can.read_text()
with gzip.open(V/'nonfinal_plans.json.gz','wt')as f:json.dump(archive,f)
for r in d['rows']:
 if r['stem']in keep:continue
 for ext in ('.qasm','.json','.plan.json','.build.json','.screen.json','_detorder.qasm','_detorder.json'):
  p=V/(r['stem']+ext)
  if p.exists():removed.append(p.name);p.unlink()
for name in ('baseline.qasm','baseline.json','baseline.plan.json','handoff_sensitivity.py','finish_sensitivity.py'):
 p=V/name
 if p.exists():removed.append(name);p.unlink()
(V/'cleanup_receipt.json').write_text(json.dumps(dict(kept=sorted(keep),removed=removed,negative_evidence='results.json and nonfinal_plans.json.gz; raw numerical verification receipts retained'),indent=2));print(len(removed),'nonfinal/redundant artifacts removed')
