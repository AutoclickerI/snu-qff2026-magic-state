import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
import sys,json,contextlib,traceback
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'quantumn_snapshot/work/lanes/MAIN/sparse'))
import sparse_walsh as sw

def price(name):
 st=ROOT/'schedule_probes'/name
 try:
  with st.with_suffix('.log').open('w') as log,contextlib.redirect_stdout(log):
   result=sw.run(st,72,True,1)
  return {k:v for k,v in result.items() if k!='results'}
 except Exception as e:
  return {'source':str(st),'error':repr(e),'trace':traceback.format_exc()}

if __name__=='__main__':
 names=sys.argv[1:] or ['remove_all','remove_11','remove_after_36','remove_after_40','remove_after_43']
 results=[]
 with ProcessPoolExecutor(max_workers=3) as pool:
  jobs={pool.submit(price,n):n for n in names}
  for f in as_completed(jobs):
   r=f.result();results.append(r);print(json.dumps(r),flush=True)
   (ROOT/'schedule_probes/prices.json').write_text(json.dumps(results,indent=2)+'\n')
