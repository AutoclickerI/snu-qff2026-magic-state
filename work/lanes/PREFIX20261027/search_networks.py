import os,sys,json,time
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import run_legacy_suffix,synth
from search_phase import singles
from qtools import price
H=synth.HERE
out=[];best=1
for f in [24,8,9,25,10,26,11,27,12,28,13,29,14,30,15,31]:
    for seed in range(2):
        r=synth.synth(seed,f,beam=240,depth=40)
        if r is None:
            print('FAILED_SYNTH',f,seed,flush=True);continue
        name=f'network_f{f}_s{seed}'
        (H/(name+'.network.json')).write_text(json.dumps(r,indent=2))
        for mode in ['first','last']:
            for ps in ([0] if mode!='random' else range(4)):
                rr=dict(r,phase_mode=mode,phase_seed=ps)
                nn=name+'_'+mode+str(ps)
                stem=synth.build(rr,nn)
                try:
                    c1,n=singles(stem)
                    ans=dict(name=nn,c1=c1,harmful=n,cx=r['depth']+112)
                    if c1<2e-5:
                        p=price(stem,1);ans.update(loss=p['loss'],acceptance=p['acceptance'])
                        if p['loss']<best:
                            best=p['loss'];(H/'network_best.json').write_text(json.dumps(dict(stem=str(stem),**ans),indent=2))
                    print(json.dumps(ans),flush=True);out.append(ans)
                    (H/'network_results.json').write_text(json.dumps(out,indent=2))
                except Exception as ex:print('ERROR',nn,repr(ex),flush=True)
