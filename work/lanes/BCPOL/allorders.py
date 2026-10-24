"""Lane-owned runner for the reviewer's independently validated Walsh code."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
os.environ['QUANTUMN_REPO']=str(ROOT)
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
sys.path.insert(0,str(H/'audit'))
from fresh_exact_walsh import *
import argparse,hashlib
p=argparse.ArgumentParser();p.add_argument('stem',type=Path);a=p.parse_args();t=time.monotonic();m,e,groups,nd,ks,psi,where,elim=prepare(a.stem)
results=[];cache={}
for key in [None]+e.keys:
 pm=None if key is None else e.Qs[key]
 if pm not in cache:cache[pm]=kernel(e,ks,psi,where,key)
 mask=0 if key is None else emask_for(key);factors=[channel_factor(m,fs,nd,mask) for fs in groups.values()]+[cache[pm]];value=contract(factors,elim['order']);results.append(value)
 print(json.dumps(dict(key=key,value=value,seconds=time.monotonic()-t)),flush=True)
A=results[0];N=(A-sum(w*b*v for w,b,v in zip(e.W,e.beta,results[1:])))/2
out=dict(stem=str(a.stem),loss=N/A,numerator=N,acceptance=A,width=elim['width'],seconds=time.monotonic()-t,channels=len(m.chans),faults=len(m.faults),results=results,source='reviewer3 fresh_exact_walsh snapshot',sha256=hashlib.sha256((H/'audit/fresh_exact_walsh.py').read_bytes()).hexdigest())
a.stem.with_suffix('.allorders.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='results'}),flush=True)
