"""Restore split readable JSON ledgers exactly; refuse differing local files."""
import hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[3]
INDEXES=[
 'work/lanes/GAUGE_SCHEDULE_20261028/shallow_parts/index.json',
 'work/lanes/MEASURED_BC_20261028/resource_ablations_parts/index.json',
 'work/lanes/EARLY_BOUNDARY_20261028/isometry_search_parts/index.json',
]
for name in INDEXES:
 ip=R/name;idx=json.loads(ip.read_text());combined=[] if idx['type'] in ('list','lines') else {}
 for row in idx['parts']:
  raw=(ip.parent/row['name']).read_bytes()
  assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],row['name']
  part=json.loads(raw);assert isinstance(part,type(combined))
  if isinstance(combined,list):combined.extend(part)
  else:
   assert not set(combined)&set(part);combined.update(part)
 assert len(combined)==idx['records']
 raw=(''.join(combined) if idx['type']=='lines' else json.dumps(combined,indent=2)+'\n').encode()
 assert len(raw)==idx['original_bytes'] and hashlib.sha256(raw).hexdigest()==idx['original_sha256']
 target=R/idx['original_path']
 if target.exists() and target.read_bytes()!=raw:raise SystemExit('Refusing to overwrite different '+str(target))
 target.write_bytes(raw);print(json.dumps({'restored':idx['original_path'],'bytes':len(raw),'sha256':idx['original_sha256']}))
