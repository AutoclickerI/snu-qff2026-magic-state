"""C6 helper-X construction, with frame correction and full single-fault gate."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent
from synth import verify,Model,B,C
from build import build
from search import score
from moments_batch import evaluate,exact2
import json,copy,time
base=json.loads((H/'inputs/base.prep.json').read_text());rows=[]
for i in range(7):
 d=dict(copy.deepcopy(base),kind='c6',value=i,helper_x=True);v=verify(d);row=dict(position=i,verification=v)
 assert v['stim_target_pass']
 if not v['policy_pass']:row['status']='REJECTED_BY_PREDICATE';rows.append(row);continue
 try:
  text,md=build(d,dict(timing='alap'));ev=exact2.Eval(text,md['data_qubits']);c1=float(ev.fp@ev.n_single);row['c1']=c1
  if abs(c1)<1e-12:row.update(evaluate(ev))
  stem=H/'finalists'/f'c6_project_{i}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md,indent=2));stem.with_suffix('.screen.json').write_text(json.dumps(row,indent=2))
 except (ValueError,AssertionError) as e:row.update(status='INVALID',error=str(e))
 rows.append(row);print(json.dumps(row),flush=True)
(H/'c6_project.receipt.json').write_text(json.dumps(rows,indent=2))
