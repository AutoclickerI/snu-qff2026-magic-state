"""Whole-circuit prices. Grid-free runs relax adjacency explicitly and only here."""
import os, sys, json, time, argparse
from pathlib import Path
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent; ROOT=H.parents[2]
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
sys.path[:0]=[str(H),str(ROOT/'work/lanes/EVAL')]
import moments, exact2

def price(stem,grid_free=False):
 import tprep.qasm as tq
 original=tq.adjacent
 if grid_free:tq.adjacent=lambda a,b:True
 try:
  stem=Path(stem);md=json.loads(stem.with_suffix('.json').read_text());t=time.monotonic()
  ev=exact2.Eval(stem.with_suffix('.qasm').read_text(),md['data_qubits'])
  c1=float(ev.fp@ev.n_single)
  if abs(c1)<1e-12:r=moments.evaluate(ev)
  else:r={'c1':c1,'rejected':'first-order logical loss; no cubic rank'}
  r.update(stem=str(stem),grid_free=grid_free,wall_seconds=time.monotonic()-t)
  stem.with_suffix('.price.json').write_text(json.dumps(r,indent=2)+'\n')
  with (H/'REPORT.md').open('a') as f:f.write('\nCompleted price `'+stem.name+'`: '+json.dumps(r)+'\n')
  print(json.dumps(r),flush=True);return r
 finally:tq.adjacent=original

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stems',nargs='+');p.add_argument('--grid-free',action='store_true');a=p.parse_args()
 for s in a.stems:price(s,a.grid_free)
