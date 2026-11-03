import os,json
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import run_legacy_suffix,synth
from search_phase import singles
from qtools import price
from add_transient_checks import augment
H=synth.HERE;r=json.loads((H/'safe_w1_s1.network.json').read_text());out=[];best=1
for mode,seed in [('first',0),('last',0)]+[('random',i) for i in range(24)]:
 rec=dict(r,alap_init=True,pull_suffix=True,phase_mode=mode,phase_seed=seed)
 nn=f'final_phase_{mode}_{seed}';p=synth.build(rec,nn)
 c1,n=singles(p);a=dict(stem=str(p),c1=c1,harmful=n)
 if c1<1e-5:
  pr=price(p,1);a.update(loss=pr['loss'],acceptance=pr['acceptance'])
  if pr['loss']<best:best=pr['loss'];(H/'final_best.json').write_text(json.dumps(a,indent=2))
 print(json.dumps(a),flush=True);out.append(a);(H/'final_phase_results.json').write_text(json.dumps(out,indent=2))
