import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json
from pathlib import Path
from moments import evaluate,exact2
H=Path(__file__).resolve().parent;rows=[]
for tag in ['replay82','cancel_1','cancel_2','cancel_3','lns_0000','lns_0001','lns_0002']:
 f=H/'full'/tag;ref=json.loads(f.with_suffix('.price.json').read_text());md=json.loads(f.with_suffix('.json').read_text());ev=exact2.Eval(f.with_suffix('.qasm').read_text(),md['data_qubits']);out=evaluate(ev)
 err={k:abs(out[k]-ref[k]) for k in ('c1','second','third','total','exp_minus_A1')};assert max(err.values())<1e-12,err
 rows.append(dict(tag=tag,error=err,moments=out,reference=dict((k,ref[k]) for k in err)));print(tag,err,flush=True)
(H/'moments_validation.json').write_text(json.dumps(rows,indent=2))
