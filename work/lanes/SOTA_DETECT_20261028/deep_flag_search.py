"""Whole-check 7-cat flag-parity search with real noise, abstract geometry."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,itertools,random,concurrent.futures
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'work/lanes/NATIVE20261027'),str(R/'work/lanes/CAT3_20261027')]
import rebuild,smallcat as s
folder=H/'deep_flag';folder.mkdir(exist_ok=True)
def one(job):
 idx,pairs=job
 try:
  c,data=rebuild.build_joint_flags(18,12,pairs);text=c.text();raw=s.ideal_contract_check(text,data)
  row={'id':idx,'pairs':pairs,'raw':raw['ok']}
  if not raw['ok']:return row
  ops,dets=s.f.parse_current(text);s.f.DATA=data;a=s.record_contract.singles(s.f.make_model(ops,dets));row.update(c1=a['c1'],harmful=len(a['harmful_faults']))
  stem=folder/f'flags_{idx:03}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps({'data_qubits':data,'abstract':True,'pairs':pairs},indent=2))
  if a['c1']<1e-10:
   val=s.exact(stem);row.update(loss=val['loss'],acceptance=val['acceptance'],stem=str(stem))
  return row
 except Exception as ex:return {'id':idx,'pairs':pairs,'error':str(ex)}
edges=list(itertools.combinations(range(7),2));rng=random.Random(617);jobs=[(0,((0,1),(1,2),(2,3)))];picks=rng.sample(list(itertools.combinations(edges,3)),90)
jobs += [(i+1,x) for i,x in enumerate(picks)]
rows=[]
with concurrent.futures.ProcessPoolExecutor(max_workers=2) as ex:
 for row in ex.map(one,jobs):
  rows.append(row)
  if 'loss'in row:print(json.dumps(row),flush=True)
  (H/'deep_flag_results.json').write_text(json.dumps(rows,indent=2)+'\n')
print('DONE',len(rows),flush=True)
