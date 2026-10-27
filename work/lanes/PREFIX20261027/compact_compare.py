import os,json,sys
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import run_legacy_suffix,synth
from search_phase import singles
from add_transient_checks import augment
from qtools import price
H=synth.HERE
for nn in ['network_f24_s0_first0','safe_w1_s1_first','safe_w1_s1_last']:
 p=H/'cand'/(nn+'.json')
 if not p.exists():continue
 r=json.loads(p.read_text())['synthesis'];r=dict(r,alap_init=True,pull_suffix=True)
 st=synth.build(r,nn+'_compact')
 for c in [False,True]:
  p,n=augment(st,'all') if c else (st,0)
  c1,h=singles(p);pr=price(p,1)
  ans=dict(stem=str(p),c1=c1,harmful=h,loss=pr['loss'],acceptance=pr['acceptance'],checks=n)
  print(json.dumps(ans),flush=True);p.with_suffix('.result.json').write_text(json.dumps(ans,indent=2))
