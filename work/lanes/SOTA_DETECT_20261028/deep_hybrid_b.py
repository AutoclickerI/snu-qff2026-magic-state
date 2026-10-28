"""Rechoose terminal B parity and reschedule coupled square ending."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,itertools,concurrent.futures
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'work/lanes/SOTA_20261028'),str(R/'work/lanes/NATIVE20261027'),str(R/'work/lanes/CAT3_20261027'),str(R/'work/lanes/END2_20261027')]
import native_schedule as sc,rebuild,smallcat as s
from joint import emit
base=H/'deep_hybrid/deep_007';out=H/'deep_hybrid_b';out.mkdir(exist_ok=True)
def one(job):
 idx,seq=job
 try:
  ops,dets=s.f.parse_current(base.with_suffix('.qasm').read_text());taps=sorted([o for o in ops if o.kind=='CX' and o.qs[1]==35],key=lambda o:o.time);assert len(taps)==3
  for o,q in zip(taps,seq):o.qs=(7+q,35)
  inp=out/f'input_{idx:03}';inp.with_suffix('.qasm').write_text(emit(ops,dets));inp.with_suffix('.json').write_text(json.dumps({'data_qubits':list(range(7))}))
  res,info=sc.solve(inp,(10,19),idx,2,'lateprep');row={'idx':idx,'check':seq}
  if res is None:row['error']='infeasible';return row
  ops,dets=res;text=emit(ops,dets);raw=s.ideal_contract_check(text,list(range(7)));row['raw']=raw['ok']
  if not raw['ok']:return row
  stem=out/f'variant_{idx:03}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps({'data_qubits':list(range(7)),'abstract':True,'check':seq,'schedule':info}))
  val=s.exact(stem);row.update(loss=val['loss'],acceptance=val['acceptance'],stem=str(stem),clocks=max(o.time for o in ops)+1)
  return row
 except Exception as e:return {'idx':idx,'check':seq,'error':str(e)}
checks=[p for p in itertools.combinations(range(7),3) if all(sum((i in a)for i in p)%2==0 for a in rebuild.GENS)];jobs=[(i,p)for i,p in enumerate(p for q in checks for p in [q,tuple(reversed(q)),(q[1],q[0],q[2])])];rows=[]
with concurrent.futures.ProcessPoolExecutor(max_workers=2) as ex:
 for row in ex.map(one,jobs):
  rows.append(row)
  if 'loss'in row:print(json.dumps(row),flush=True)
  (H/'deep_hybrid_b_results.json').write_text(json.dumps(rows,indent=2)+'\n')
print('DONE',len(rows),flush=True)
