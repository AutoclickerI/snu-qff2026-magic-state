"""Joint seven-cat flags and terminal resource logical-check representative."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,itertools,concurrent.futures
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'work/lanes/NATIVE20261027'),str(R/'work/lanes/CAT3_20261027')]
import rebuild,smallcat as s
folder=H/'deep_bcheck';folder.mkdir(exist_ok=True)
checks=[p for p in itertools.combinations(range(7),3) if all(sum((i in a)for i in p)%2==0 for a in rebuild.GENS)]
def one(job):
 idx,seq=job
 try:
  c,data=rebuild.build_joint_flags(18,12,((0,1),(2,5),(4,6)))
  for j,q in enumerate(seq):
   t=15+j;old=f'cx q[{7+j}],q[35];';new=f'cx q[{7+q}],q[35];';assert old in c.ops[t];c.ops[t][c.ops[t].index(old)]=new
  text=c.text();raw=s.ideal_contract_check(text,data);row={'id':idx,'seq':seq,'raw':raw['ok']}
  if not raw['ok']:return row
  s.f.DATA=data;ops,dets=s.f.parse_current(text);audit=s.record_contract.singles(s.f.make_model(ops,dets));row['c1']=audit['c1']
  stem=folder/f'bcheck_{idx:03}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps({'data_qubits':data,'abstract':True,'check':seq},indent=2))
  if row['c1']<1e-10:
   val=s.exact(stem);row.update(loss=val['loss'],acceptance=val['acceptance'],stem=str(stem))
  return row
 except Exception as e:return {'id':idx,'seq':seq,'error':str(e)}
jobs=[(i,p)for i,p in enumerate(p for q in checks for p in itertools.permutations(q))];print('CHECKS',checks,'jobs',len(jobs),flush=True)
rows=[]
with concurrent.futures.ProcessPoolExecutor(max_workers=2)as ex:
 for row in ex.map(one,jobs):
  rows.append(row)
  if 'loss'in row:print(json.dumps(row),flush=True)
  (H/'deep_bcheck_results.json').write_text(json.dumps(rows,indent=2)+'\n')
print('DONE',len(rows),flush=True)
