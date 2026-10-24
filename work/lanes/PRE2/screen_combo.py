import json, os, subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
rows=[]
for i in range(31):
 n=f'compact_dropcombo_{i:02d}_31_32'; q=HERE/(n+'_m.qasm')
 out=subprocess.run(['/home/jihoon/competitions/quantumn/.venv/bin/python','work/lanes/EVAL/exact2.py',str(q),'--procs','8','--top','0','--json',str(HERE/(n+'_m.exact2.json'))],cwd=HERE.parents[2],env=env,capture_output=True,text=True,check=True).stdout
 row={'name':n}
 for l in out.splitlines():
  if l.startswith('second order:'): row['second']=float(l.split(':',1)[1].split()[0])
  if l.startswith('acceptance:'): row['exp_A1']=float(l.split('exp(-A1) = ')[1].split()[0])
 rows.append(row); print(row,flush=True)
(HERE/'combo_screen.json').write_text(json.dumps(rows,indent=2)+'\n')
