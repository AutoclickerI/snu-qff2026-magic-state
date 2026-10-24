"""One eight-core lane shard; process completion controls every next launch."""
import os,sys,subprocess,json
from pathlib import Path
H=Path(__file__).resolve().parent;shard=int(sys.argv[1]);os.chdir(H)
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
cases=[(r,c,opt) for r in range(3) for c in range(2) for opt in ['l5_11','l5_12']]
for ix,(r,c,opt) in enumerate(cases):
 if ix%3!=shard:continue
 cap=os.cpu_count();load=os.getloadavg()[0];print('capacity',cap,'loadavg',Path('/proc/loadavg').read_text().strip(),flush=True)
 # Three shards jointly use <=24 cores; prevent a fresh launch if shared load rose.
 workers=min(8,max(1,int(cap-load)))
 if load>=cap:raise RuntimeError('host at capacity; no dependent job launched')
 name=f'free2d_r{r}c{c}_{opt}';cmd=[sys.executable,'co_design.py','--out',name,'--row',str(r),'--col',str(c),'--option',opt,'--bhops','1','--dhops','2','--seconds','90','--workers',str(workers)]
 with (H/(name+'.log')).open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
