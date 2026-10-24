"""Unchanged exact2 CLI and ablations for every listed complete end-state build."""
from common import *
import argparse,subprocess,concurrent.futures
def run(stem):
 stem=Path(stem);py=str(ROOT/'.venv/bin/python');env={**os.environ,'XTIM_TWIRL_CACHE_DIR':str(H/'.xtim_cache')}
 for tool,args,suffix in [('work/lanes/SEPBC/endstate_ablate.py',[str(stem),'--procs','2'],'.ablation.log'),('work/lanes/EVAL/exact2.py',[str(stem.with_suffix('.qasm')),'--third','--top','30','--procs','2','--json',str(stem.with_suffix('.unchanged_exact.json'))],'.unchanged_exact.log')]:
  with stem.with_suffix(suffix).open('w')as f:r=subprocess.run([py,'-u',str(ROOT/tool),*args],env=env,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
  append_result(stem.name,dict(tool=tool,returncode=r.returncode),'Full end-state validation process exited.');print(stem.name,tool,r.returncode,flush=True)
  if r.returncode:break
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stems',nargs='+');p.add_argument('--jobs',type=int,default=2);a=p.parse_args()
 with concurrent.futures.ThreadPoolExecutor(a.jobs)as pool:list(pool.map(run,a.stems))
