from common import *
import subprocess,concurrent.futures
names=['sepbc_v29c_q5_t37','sepbc_v29c_q5_t38','sepbc_v29c_q5_both']
def run(name):
 stem=H/name;env={**os.environ,'XTIM_TWIRL_CACHE_DIR':str(H/'.xtim_cache')};py=str(ROOT/'.venv/bin/python')
 for tool,args,suffix in [('work/lanes/SEPBC/speed_local.py',[str(stem)],'.speed_prediction.log'),('work/fast_check.py',[str(stem.with_suffix('.qasm')),str(stem.with_suffix('.json')),'1000000','1'],'.judge.log'),('work/lanes/EVAL/exact2.py',[str(stem.with_suffix('.qasm')),'--third','--top','30','--procs','4','--json',str(stem.with_suffix('.unchanged_exact.json'))],'.unchanged_exact.log')]:
  with stem.with_suffix(suffix).open('w')as f:r=subprocess.run([py,'-u',str(ROOT/tool),*args],cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
  append_result(name,dict(check=tool,returncode=r.returncode),'Unchanged verifier arithmetic; XTIM cache alone redirected to SEPBC.');print(name,tool,r.returncode,flush=True)
  if r.returncode:break
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(2)as pool:list(pool.map(run,names))
