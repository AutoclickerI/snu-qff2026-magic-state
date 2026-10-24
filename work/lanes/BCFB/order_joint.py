"""Joint earlier/later BC check with bounded retiming and the data round fixed."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,concurrent.futures
from evaluate import H,price

def job(x):
 d,opt,tag=x;return price(d,opt,tag,'joint_order')
def main():
 jobs=[]
 for name in ('fb_d14_c98_s517_00020','fb_d15_c105_s506_00008'):
  md=json.loads((H/'finalists'/name).with_suffix('.json').read_text());d=md['prep']
  for delta in (-3,-2,-1,2):
   for early in (False,True):
    for window in (1,2,4):
     opt=dict(timing='alap',check_delta=delta,read_early=early,retime_window=window);jobs.append((d,opt,f'jo_{name}_d{delta}_e{int(early)}_w{window}'))
 with concurrent.futures.ProcessPoolExecutor(max_workers=4) as ex:rs=list(ex.map(job,jobs))
 r=dict(status='COMPLETE',prices=len(rs),best=min((r.get('total',1) for r in rs),default=None));(H/'runs/joint_order.receipt.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
if __name__=='__main__':main()
