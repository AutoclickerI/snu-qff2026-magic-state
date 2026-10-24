"""Validate every completed built circuit through the exact2 CLI sums."""
from portfolio import H,ROOT,PY
import concurrent.futures,subprocess,os,json,time,argparse
def one(p):
 stem=p.with_suffix('');out=stem.with_suffix('.exact.log');start=time.monotonic();load=os.getloadavg()[0]
 if load>60:raise RuntimeError(f'Host over capacity: {load}')
 env={**os.environ,'XTIM_TWIRL_CACHE_DIR':str(H/'.xtim_cache')}
 with out.open('w')as f:
  done=subprocess.run([PY,'-u',str(H/'price.py'),str(p),'--third','--top','30','--procs','1','--json',str(stem.with_suffix('.exact.json'))],stdout=f,stderr=subprocess.STDOUT,env=env,cwd=ROOT)
 rec=dict(stem=stem.name,returncode=done.returncode,seconds=time.monotonic()-start,load_before=load)
 stem.with_suffix('.exact.exit.json').write_text(json.dumps(rec,indent=2));print(json.dumps(rec),flush=True)
 return rec
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--procs',type=int,default=14);a=p.parse_args()
 paths=[p for p in H.glob('*.qasm')if p.with_suffix('.screen.json').exists()and not p.with_suffix('.price.json').exists()]
 # Finalist and complete separate-BC witnesses go first.
 paths.sort(key=lambda p:(not p.name.startswith(('zero_','interleave_')),p.name))
 print('exact circuits',len(paths),flush=True)
 with concurrent.futures.ThreadPoolExecutor(a.procs)as pool:list(pool.map(one,paths))
