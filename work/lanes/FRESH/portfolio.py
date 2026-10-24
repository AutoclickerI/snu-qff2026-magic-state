"""Independent SAT seeds followed by complete-circuit cubic ranking."""
import os,sys,json,subprocess,concurrent.futures,time
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2];PY=ROOT/'.venv/bin/python'
os.environ.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',XTIM_TWIRL_CACHE_DIR=str(H/'.xtim_cache'))

def run(x):
 dep,cap,seed=x;tag=f'd{dep}_k{cap}_s{seed}'
 with (H/f'synth_{tag}.log').open('w') as f:
  r=subprocess.run([str(PY),str(H/'synth.py'),'--depth',str(dep),'--cap',str(cap),'--seed',str(seed),'--seconds','180','--count','4','--clean'],stdout=f,stderr=subprocess.STDOUT)
 files=sorted(H.glob(f'corr_{tag}_*.prep.json'))
 if not files:return dict(tag=tag,status='no_witness',returncode=r.returncode)
 with (H/f'portfolio_{tag}.log').open('w') as f:
  r=subprocess.run([str(PY),str(H/'assemble.py'),*[str(x) for x in files],'--base','freshbase','--base-path',str(H/'inputs/freshbase'),'--init-mode','measured'],stdout=f,stderr=subprocess.STDOUT)
  out=sorted(H.glob(f'corr_{tag}_*_freshbase_w0_mi.qasm'))
  if out:r=subprocess.run([str(PY),str(H/'price.py'),*[str(x) for x in out]],stdout=f,stderr=subprocess.STDOUT)
 return dict(tag=tag,resources=len(files),returncode=r.returncode)

if __name__=='__main__':
 jobs=[(11,57,s) for s in range(31,39)]+[(12,62,s) for s in range(39,43)]+[(13,67,s) for s in range(43,47)]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
  for f in concurrent.futures.as_completed([ex.submit(run,j) for j in jobs]):print(json.dumps(f.result()),flush=True)
