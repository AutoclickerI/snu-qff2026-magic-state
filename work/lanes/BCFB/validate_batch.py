import sys,os,time,json
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from evaluate import H,exact2
from moments import evaluate as old
from moments_batch import evaluate as new
fs=[H/'inputs/replay']+sorted({p.with_suffix('') for p in (H/'finalists').glob('*.qasm')})[:4]
rows=[]
for f in fs:
 ev=exact2.Eval(f.with_suffix('.qasm').read_text(),json.loads(f.with_suffix('.json').read_text())['data_qubits']);a=old(ev);b=new(ev);err=max(abs(a[k]-b[k]) for k in ('c1','second','third','total','exp_minus_A1','T3a','t3bc'));assert err<1e-15
 row=dict(stem=str(f),max_error=err,old_seconds=a['seconds'],new_seconds=b['seconds'],old=a,new=b);rows.append(row);print(json.dumps(row),flush=True)
(H/'batch_validation.json').write_text(json.dumps(rows,indent=2))
