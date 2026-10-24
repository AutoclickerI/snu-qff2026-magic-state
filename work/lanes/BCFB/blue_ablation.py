import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['BCFB_BLUE_DB']='neighbors.sqlite'
import json
from blue_evaluate import price,H
orig=json.loads((H.parent/'inputs/fb_s401_0035.prep.json').read_text());rows=[]
for c in ['v25k','v26n']:
 f=H/'finalists'/(c+'_ic_fast_d15_c105_s526_00356_11_19_preserve_rt1');md=json.loads(f.with_suffix('.json').read_text());moves=md['non_BC_time_changes'];opt=dict(context=c,timing='alap',mx=[q for q in orig['pivots'] if q!=19],force_times=moves)
 for checks in [[],[11,19]]:
  row=price(orig,dict(opt,init_checks=checks),'ablate_'+c+'_82_moved'+('_checked' if checks else ''),'blue_ablation',threshold=1);rows.append(row)
(H/'ablation.json').write_text(json.dumps(rows,indent=2))
