"""Price round shifts with every source operation and wire order retained."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['BCFB_BLUE_DB']='neighbors.sqlite'
import json,time
from blue_evaluate import price,H
stems=['blue_d15_c105_s706_00405','neighbor_blue_d15_c105_s706_00405_check_11_19','blue_d15_c90_s712_00074','neighbor_blue_d15_c90_s712_00074_check_19'];rows=[];start=time.monotonic()
for stem in stems:
 f=H/'finalists'/stem;md=json.loads(f.with_suffix('.json').read_text());base=json.loads(f.with_suffix('.screen.json').read_text())['total']
 for delta in [-3,-2,-1,1,2]:
  for window in [4,12]:
   opt=dict(md['options'],round_shift=delta,retime_window=window)
   rows.append(price(md['prep'],opt,'round_'+stem+'_'+str(delta)+'_w'+str(window),'blue_round',threshold=base))
rec=dict(status='COMPLETE',prices=len(rows),seconds=time.monotonic()-start,best=min((r.get('total',1) for r in rows),default=None));(H/'round_receipt.json').write_text(json.dumps(rec,indent=2));print(json.dumps(rec),flush=True)
