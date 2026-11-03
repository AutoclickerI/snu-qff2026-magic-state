"""Reconstruct FLAGH shared 7-cat architecture: noisy abstract schedule search."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,random,traceback,concurrent.futures
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'work/lanes/SOTA_20261028'),str(R/'work/lanes/CAT3_20261027'),str(R/'work/lanes/END2_20261027'),str(R/'work/tools')]
import native_schedule as sched,smallcat as s
from joint import emit
base=H/'deep_flag/flags_005'
out=H/'deep_flag_schedule';out.mkdir(exist_ok=True)
def run(job):
 idx,mode,window=job
 try:
  res,info=sched.solve(base,window,idx,3,mode)
  if res is None:return {'idx':idx,'error':'infeasible','info':info}
  ops,dets=res;text=emit(ops,dets);raw=s.ideal_contract_check(text,list(range(7)))
  stem=out/f'deep_{idx:03}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps({'data_qubits':list(range(7)),'abstract':True,'schedule':info},indent=2))
  row={'idx':idx,'mode':mode,'window':window,'raw':raw['ok'],'clocks':max(o.time for o in ops)+1,'stem':str(stem)}
  if raw['ok']:
   val=s.exact(stem);row.update(loss=val['loss'],acceptance=val['acceptance'])
  return row
 except Exception as e:return {'idx':idx,'error':str(e),'traceback':traceback.format_exc()}
if __name__=='__main__':
 modes=['random','lateprep','earlyread','early'];windows=[(0,20),(7,20),(11,20),(3,17)]
 jobs=[(i,modes[(i//4)%4],windows[i%4])for i in range(24)]
 rows=[]
 with concurrent.futures.ProcessPoolExecutor(max_workers=2)as ex:
  for row in ex.map(run,jobs):
   rows.append(row);(H/'deep_flag_schedule_results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
