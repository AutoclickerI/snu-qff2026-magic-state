"""Re-synthesize both 7-cat trees against their flags, full noisy score."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,random,concurrent.futures
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'work/lanes/NATIVE20261027'),str(R/'work/lanes/CAT3_20261027')]
import rebuild,smallcat as s
out=H/'deep_tree';out.mkdir(exist_ok=True)
def run(job):
 idx,p1,p2=job
 try:
  def cat(c,block,t,tree=0):
   p=p1 if block[0]==21 else p2
   for j,q in enumerate(block):c.reset(t,q,j==p[0])
   layers=[[(0,1)],[(0,2),(1,3)],[(0,4),(1,5),(2,6)]]
   for k,layer in enumerate(layers):
    for a,b in layer:c.cx(t+1+k,block[p[a]],block[p[b]])
  old=rebuild.Circuit.cat;rebuild.Circuit.cat=cat
  try:c,data=rebuild.build_joint_flags(18,12,((0,1),(2,5),(4,6)))
  finally:rebuild.Circuit.cat=old
  for j,q in enumerate([6,4,1]):
   t=15+j;old=f'cx q[{7+j}],q[35];';new=f'cx q[{7+q}],q[35];';c.ops[t][c.ops[t].index(old)]=new
  text=c.text();raw=s.ideal_contract_check(text,data);row={'idx':idx,'p1':p1,'p2':p2,'raw':raw['ok']}
  if not raw['ok']:return row
  stem=out/f'tree_{idx:03}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps({'data_qubits':data,'abstract':True,'p1':p1,'p2':p2}))
  val=s.exact(stem);row.update(loss=val['loss'],acceptance=val['acceptance'],stem=str(stem))
  return row
 except Exception as e:return {'idx':idx,'error':str(e)}
rng=random.Random(12635);jobs=[]
for i in range(80):
 a=list(range(7));b=list(range(7));rng.shuffle(a);rng.shuffle(b);jobs.append((i,a,b))
rows=[]
with concurrent.futures.ProcessPoolExecutor(max_workers=2)as ex:
 for row in ex.map(run,jobs):
  rows.append(row)
  if 'loss'in row:print(json.dumps(row),flush=True)
  (H/'deep_tree_results.json').write_text(json.dumps(rows,indent=2)+'\n')
print('DONE',len(rows),flush=True)
