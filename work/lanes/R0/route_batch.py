import os,sys,subprocess,json
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).parent
for r,c in [(0,0),(1,0),(2,0),(0,1),(1,1),(2,1)]:
 stem=H/f'relax2_r{r}c{c}'
 cmd=[sys.executable,str(H/'route.py'),'--horizon','41','--dhops','2','--bhops','3','--transform',f'0,{r},{c}','--fast-b','--workers','4','--seconds','60','--out',str(stem)+'.json']
 with open(str(stem)+'.log','w') as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 print(stem.name,p.returncode,json.loads(Path(str(stem)+'.json').read_text()).get('status'),flush=True)
