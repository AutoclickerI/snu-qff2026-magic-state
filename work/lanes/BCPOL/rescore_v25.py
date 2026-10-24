import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent
from boundary_api import *
import json
c=AllOrdersCache(H/'finalists/v25_cache_endpoint_5_902_02232_r19.boundary_allorders.npz');rows=[]
stems=sorted((H/'finalists').glob('v25_*_r19.qasm'))+sorted((H/'finalists').glob('v25_*_allrx.qasm'))
for p in sorted((H/'runs').glob('cache_v25k_endpoint_5_95*.best.json')):
 stems.append(H/'finalists'/(json.loads(p.read_text())['tag']+'.qasm'))
for qasm in stems:
 stem=qasm.with_suffix('')
 try:
  region=prepare_candidate(stem);row=c.score(region);row.update(source='validated all-orders boundary response',cache='v25_cache_endpoint_5_902_02232_r19.boundary_allorders.npz')
  if stem.with_suffix('.allorders.json').exists():
   ref=json.loads(stem.with_suffix('.allorders.json').read_text());assert abs(row['loss']-ref['loss'])<1e-13
  else:stem.with_suffix('.allorders.json').write_text(json.dumps(row,indent=2))
  row['compatible']=True
 except ValueError as e:row=dict(compatible=False,error=str(e))
 row['stem']=str(stem);rows.append(row);print(json.dumps(row),flush=True)
(H/'v25_cache_rescore.json').write_text(json.dumps(rows,indent=2))
