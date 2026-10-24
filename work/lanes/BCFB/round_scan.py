"""Keep every operation; price earlier/later rounds with bounded retiming."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,itertools,concurrent.futures
from evaluate import H,price

def job(x):d,opt,tag=x;return price(d,opt,tag,'round_shift')
def main():
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=4);a=p.parse_args();jobs=[]
 for name in ('base','fb_d14_c98_s517_00020','fast_d15_c105_s526_00356'):
  d=json.loads((H/'inputs/fb_s401_0035.prep.json').read_text()) if name=='base' else json.loads((H/'finalists'/name).with_suffix('.json').read_text())['prep']
  for shift in (-3,-2,-1,0,1,2):
   for w in (1,2,4,8):
    opt=dict(round_shift=shift,retime_window=w,timing='alap');jobs.append((d,opt,f'round_{name}_s{shift}_w{w}'))
 with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as e:rs=list(e.map(job,jobs))
 out=dict(status='COMPLETE',prices=len(rs),best=min((r.get('total',1) for r in rs),default=None));(H/'runs/round_scan.receipt.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
if __name__=='__main__':main()
