import os,sys
sys.dont_write_bytecode=True
from pathlib import Path
H=Path(__file__).resolve().parent
from boundary_api import *
import json
full=AllOrdersCache(H/'inputs/replay_policy.boundary_allorders.npz');cubic=CubicCache(H/'boundary.cache.npz');rows=[]
for stem in ['replay_policy','cache_cancel_10_11','cache_cancel_11_12']:
 p=prepare_candidate(H/'inputs'/stem);a=full.score(p);c=cubic.score(p);row=dict(stem=stem,all_orders=a,cubic=c)
 ref=H/'inputs'/f'{stem}.allorders.json'
 if ref.exists():
  value=json.loads(ref.read_text());row['full_reference_delta']=a['loss']-value['loss'];assert abs(row['full_reference_delta'])<1e-13
 rows.append(row);print(json.dumps(row),flush=True)
# A changed endpoint must be rejected, since its exterior records differ.
p=prepare_candidate(H/'finalists/endpoint_5_s712_00601')
try:full.score(p)
except ValueError as e:rows.append(dict(incompatible_endpoint_rejected=True,error=str(e)))
else:raise AssertionError('Changed ideal/exterior was accepted')
(H/'cache.api.validation.json').write_text(json.dumps(rows,indent=2))
