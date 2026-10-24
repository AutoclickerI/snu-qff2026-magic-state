import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import multiprocessing as mp,sys,json,math,time
from pathlib import Path
sys.path.insert(0,'/home/jihoon/competitions/quantumn/work/lanes/EVAL');import exact2
def one(p):
 p=Path(p);o=p.with_suffix('.thirdtop.json')
 try:
  ev=exact2.Eval(p.read_text(),json.loads(p.with_suffix('.json').read_text())['data_qubits']);x=exact2.run(ev,1,third=True);tt=exact2.third_order(ev,1)[0]+x['t3bc'] if abs(x['loss1'])<1e-12 else None
  z={'name':p.stem,'c1':x['loss1'],'second':x['loss'],'third':tt,'total':x['loss']+tt if tt is not None else None,'A1':x['A1'],'exp_minus_A1':math.exp(-x['A1'])}
 except Exception as e:z={'name':p.stem,'error':repr(e)}
 o.write_text(json.dumps(z));return z
if __name__=='__main__':
 with mp.Pool(int(os.environ.get('WORKERS','20'))) as pool:
  for z in pool.imap_unordered(one,sys.argv[1:]):print(json.dumps(z),flush=True)
