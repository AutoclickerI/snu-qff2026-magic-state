import os,sys,json,subprocess
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;layout=Path(sys.argv[1]);d=json.loads(layout.read_text());tag=H/layout.stem
cmd=[sys.executable,str(H/'exenc.py'),'--cells',','.join(map(str,d['a'])),'--type','plus','--helpers','--extra','1','--workers','4','--no-alternatives','--max-class','5000000','--out',str(tag)+'_A.json']
with open(str(tag)+'_A.log','w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
print('A',r.returncode,flush=True)
for depth in [24,30]:
 cmd=[sys.executable,str(H/'synthesis.py'),str(layout),'--depth',str(depth),'--cap','160','--seconds','180','--out',str(tag)+f'_BC{depth}']
 with open(str(tag)+f'_BC{depth}.log','w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 print('BC',depth,r.returncode,flush=True)
 if Path(str(tag)+f'_BC{depth}.prep.json').exists():break
