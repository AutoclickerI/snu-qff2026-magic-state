import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys;sys.path.insert(0,"/home/jihoon/competitions/quantumn/work/lanes/EVAL")
import exact2,json,math,time
from pathlib import Path
for s in sys.argv[1:]:
 p=Path(s);o=p.with_suffix('.third.json')
 try:
  ev=exact2.Eval(p.read_text(),json.loads(p.with_suffix('.json').read_text())['data_qubits']);t=time.time();x=exact2.run(ev,16,third=True); print('run',p.name,time.time()-t,flush=True)
  z={'name':p.stem,'c1':x['loss1'],'second':x['loss'],'A1':x['A1'],'exp_minus_A1':math.exp(-x['A1']),'acc1':x['acc1'],'acc2':x['acc2']}
  if abs(x['loss1'])<1e-12:
   t=time.time();tt=exact2.third_order(ev,16)[0]+x['t3bc'];print('triple',p.name,time.time()-t,flush=True);z.update(third=tt,total=x['loss']+tt)
  else:z.update(third=None,total=None)
 except Exception as e:z={'name':p.stem,'error':repr(e)}
 o.write_text(json.dumps(z));print(json.dumps(z),flush=True)
