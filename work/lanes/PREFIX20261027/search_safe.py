import os,sys,json,time
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import run_legacy_suffix,synth
from search_phase import singles
from qtools import price
from add_transient_checks import augment
H=synth.HERE;out=[];best=1
for w in [1.,2.,4.,8.]:
 for seed in range(4):
  r=synth.synth(seed,24,beam=350,depth=50,unsafe_weight=w,safe_start=True)
  if r is None:print('FAILED_SYNTH',w,seed,flush=True);continue
  name=f'safe_w{int(w)}_s{seed}'
  (H/(name+'.network.json')).write_text(json.dumps(r,indent=2))
  for mode in ['first','last']:
   rr=dict(r,phase_mode=mode)
   stem=synth.build(rr,name+'_'+mode)
   st,n=augment(stem,'all')
   try:
    c1,h=singles(st);ans=dict(name=st.name,c1=c1,harmful=h,cx=r['depth']+112,exposure=r['unsafe_exposure'])
    if c1<1e-5:
     p=price(st,1);ans.update(loss=p['loss'],acceptance=p['acceptance'])
     if p['loss']<best:best=p['loss'];(H/'safe_best.json').write_text(json.dumps(dict(stem=str(st),**ans),indent=2))
    print(json.dumps(ans),flush=True);out.append(ans);(H/'safe_results.json').write_text(json.dumps(out,indent=2))
   except Exception as ex:print('ERROR',st.name,repr(ex),flush=True)
