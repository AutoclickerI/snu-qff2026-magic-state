import os,sys,json,subprocess,concurrent.futures
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent

def run(rc):
 r,c=rc;stem=H/f'bound38_{r}{c}';cmd=[sys.executable,str(H/'route.py'),'--horizon','39','--dhops','2','--bhops','3','--transform',f'0,{r},{c}','--workers','4','--seconds','90','--physical','--interleaved','--prep-components','--connect','--verify','--no-presolve','--out',str(stem)+'.json']
 with open(str(stem)+'.log','w') as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 d=json.loads(Path(str(stem)+'.json').read_text());return stem.name,d['status'],d['wall']
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
 for r in ex.map(run,[(r,c) for r in range(3) for c in range(2)]):print(r,flush=True)
