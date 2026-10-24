import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import concurrent.futures,json,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;qs=[6,26,5,12]
args=[]
for m in range(16):
 pick=[q for i,q in enumerate(qs) if m>>i&1];args.append((f'p2134_mxmask{m:02d}',pick))
def job(x):
 tag,pick=x
 with (H/'full'/f'{tag}.price.log').open('w') as log:
  p=subprocess.Popen([sys.executable,str(H/'price.py'),str(H/'runs/lns_c81_s201_w0111.prep.json'),tag,'--mode','release_alap','--mx',','.join(map(str,pick))],stdout=log,stderr=subprocess.STDOUT,cwd=H);rc=p.wait()
 print(tag,rc,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as e:list(e.map(job,args))
