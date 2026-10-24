"""Use the fifth noiseless C parity available at a rank-five endpoint."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent
from build import build
from moments_batch import exact2,evaluate
import json,math
names=['endpoint_5_s712_00138','endpoint_5_s712_00601','cache_endpoint_5_901_02799','cache_endpoint_5_902_02232','v25_cache_endpoint_5_902_02232_r19'];rows=[]
for name in names:
 md=json.loads((H/'finalists'/f'{name}.json').read_text());d=md['prep'];opt=dict(md['options'],endpoint_parity=True);text,meta=build(d,opt);ev=exact2.Eval(text,meta['data_qubits']);row=evaluate(ev);row.update(tag=name+'_parity',parent=name,zero_cells=[r['zero_cell'] for r in meta['endpoint_parity']],delta_loss=row['total']-json.loads((H/'finalists'/f'{name}.screen.json').read_text())['total'])
 out=H/'finalists'/row['tag'];out.with_suffix('.qasm').write_text(text);out.with_suffix('.json').write_text(json.dumps(meta,indent=2));out.with_suffix('.screen.json').write_text(json.dumps(row,indent=2));rows.append(row);print(json.dumps(row),flush=True)
(H/'endpoint_parity.receipt.json').write_text(json.dumps(rows,indent=2))
