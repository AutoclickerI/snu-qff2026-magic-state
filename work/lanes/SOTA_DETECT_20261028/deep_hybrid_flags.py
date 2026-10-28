"""Jointly synthesize new 7-cat flag parities and local schedule."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,itertools,random,concurrent.futures
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'work/lanes/SOTA_20261028'),str(R/'work/lanes/CAT3_20261027'),str(R/'work/lanes/END2_20261027')]
import native_schedule as sc,smallcat as s
from joint import emit
base=H/'deep_hybrid/deep_007';out=H/'deep_hybrid_flags';out.mkdir(exist_ok=True)
def one(job):
 idx,pairs=job
 try:
  ops,dets=s.f.parse_current(base.with_suffix('.qasm').read_text())
  for shift,anc in [(21,[7,8,10]),(28,[14,15,17])]:
   for j,a in enumerate(anc):
    v=sorted([o for o in ops if o.kind=='CX' and o.qs[0] in range(shift,shift+7) and o.qs[1]==a and o.time<14],key=lambda o:o.time)
    assert len(v)==2
    for o,q in zip(v,pairs[j]):o.qs=(shift+q,a)
  inp=out/f'input_{idx:03}';inp.with_suffix('.qasm').write_text(emit(ops,dets));inp.with_suffix('.json').write_text(json.dumps({'data_qubits':list(range(7))}))
  res,info=sc.solve(inp,(6,17),idx,2,'lateprep')
  row={'idx':idx,'pairs':pairs}
  if res is None:row['error']='infeasible';return row
  ops,dets=res;text=emit(ops,dets);raw=s.ideal_contract_check(text,list(range(7)));row['raw']=raw['ok']
  if not raw['ok']:return row
  stem=out/f'variant_{idx:03}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps({'data_qubits':list(range(7)),'abstract':True,'pairs':pairs,'schedule':info}))
  val=s.exact(stem);row.update(loss=val['loss'],acceptance=val['acceptance'],stem=str(stem),clocks=max(o.time for o in ops)+1)
  return row
 except Exception as e:return {'idx':idx,'pairs':pairs,'error':str(e)}
rng=random.Random(1234);edges=list(itertools.combinations(range(7),2));comb=list(itertools.combinations(edges,3));jobs=[(i,p)for i,p in enumerate(rng.sample(comb,40))];rows=[]
with concurrent.futures.ProcessPoolExecutor(max_workers=2)as ex:
 for row in ex.map(one,jobs):
  rows.append(row)
  if 'loss'in row:print(json.dumps(row),flush=True)
  (H/'deep_hybrid_flags_results.json').write_text(json.dumps(rows,indent=2)+'\n')
print('DONE',len(rows),flush=True)
