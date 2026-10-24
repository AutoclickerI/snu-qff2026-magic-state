"""Optimize retained joint-BC geometry in every non-equivalent prefix placement."""
import os,sys,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;os.chdir(H)
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
workers=int(sys.argv[1])
for r in range(3):
 for c in range(2):
  print('capacity',os.cpu_count(),'loadavg',Path('/proc/loadavg').read_text().strip(),flush=True)
  if os.getloadavg()[0]>=os.cpu_count():raise RuntimeError('host capacity')
  name=f'joint_safe_r{r}c{c}'
  cmd=[sys.executable,'co_design.py','--out',name,'--joint','--calibration','calibration.json','--alap-tie','--row',str(r),'--col',str(c),'--bhops','0','--dhops','3','--workers',str(workers),'--seconds','90']
  with (H/(name+'.log')).open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
