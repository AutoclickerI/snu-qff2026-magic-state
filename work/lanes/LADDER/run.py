"""Finite process pool; checks host headroom at every launch, waits on process exit."""
import os,sys,subprocess,json,time,concurrent.futures,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
ENV=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',XTIM_TWIRL_CACHE_DIR=str(HERE/'.xtim_cache'))
N=int(os.environ.get('LADDER_JOBS','4'))
def one(qasm):
 for suffix in ['.command.json','.exact.txt']:
  previous=qasm.with_suffix(suffix)
  if previous.exists():shutil.copy2(previous,qasm.with_suffix('.previous'+suffix))
 load=os.getloadavg()[0];cores=os.cpu_count();procs=subprocess.check_output(['ps','-u',str(os.getuid()),'-o','pcpu='],text=True);own=sum(float(s) for s in procs.split())/100
 assert load+1<=cores and own+1<=cores*.75,('Host capacity unavailable',load,own,cores)
 cmd=[str(ROOT/'.venv/bin/python'),str(HERE/'price.py'),str(qasm),'--third','--top','40','--procs','1','--json',str(qasm.with_suffix('.sens.json'))]
 receipt=dict(command=cmd,environment={k:ENV[k] for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','PYTHONDONTWRITEBYTECODE','XTIM_TWIRL_CACHE_DIR']},load=load,own_cpu_equivalents=own,cores=cores,start=time.time())
 with qasm.with_suffix('.exact.txt').open('w') as f:
  p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,env=ENV,cwd=ROOT);receipt['pid']=p.pid;receipt['returncode']=p.wait()
 receipt['seconds']=time.time()-receipt['start'];qasm.with_suffix('.command.json').write_text(json.dumps(receipt,indent=2))
 print(qasm.stem,receipt['returncode'],round(receipt['seconds'],2),flush=True)
 return receipt['returncode']
files=[HERE/(s+'.qasm') for s in sys.argv[1:]] if len(sys.argv)>1 else sorted(HERE.glob('f*.qasm'))+sorted(HERE.glob('r*.qasm'))
with concurrent.futures.ThreadPoolExecutor(max_workers=N) as pool:
 results=list(pool.map(one,files))
sys.exit(any(results))
