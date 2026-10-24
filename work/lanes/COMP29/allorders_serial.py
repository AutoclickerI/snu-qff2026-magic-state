"""One-process orchestration of the unchanged validated contraction functions."""
import os,sys,json,time
from pathlib import Path
H=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
import allorders_general as a
stem=H/sys.argv[1];start=time.monotonic();a.G=a.prepare(stem);m,e,groups,nd,ks,psi,where,elim=a.G
vr=a.validate(stem,a.G);stem.with_suffix('.allorders_general.validation.json').write_text(json.dumps(vr,indent=2)+'\n');print(json.dumps(dict(event='validated',**vr)),flush=True)
rows=[]
for key in [None]+e.keys:
    r=a.one(key);rows.append(r);print(json.dumps(r),flush=True)
A=rows[0]['value'];N=.5*(A-sum(w*b*r['value'] for w,b,r in zip(e.W,e.beta,rows[1:])))
r=dict(loss=N/A,acceptance=A,numerator=N,width=elim['width'],active_projectors=vr['active_projectors'],seconds=time.monotonic()-start,procs=1,validated=True,source='BCPOL five-projector contraction, unchanged prepare/validate/one; sequential orchestration')
stem.with_suffix('.allorders.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
