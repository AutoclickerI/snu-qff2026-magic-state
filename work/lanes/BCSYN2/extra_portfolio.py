import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import concurrent.futures,json,subprocess,time
from pathlib import Path
H=Path(__file__).resolve().parent
jobs=[(14,74,301),(14,70,302),(13,82,303),(13,78,304)]
def job(z):
 d,c,s=z;tag=H/'runs'/f'helperx_d{d}_c{c}_s{s}';cmd=[sys.executable,str(H/'synth.py'),'--depth',str(d),'--cap',str(c),'--seed',str(s),'--seconds','7205','--helpers','18,24,30,31,32,33,34,35','--helper-x','--hint',str(H/'inputs/tom_ep_d14_c70_s2.endpoint.json'),'--eager','--out',str(tag)]
 with open(str(tag)+'.log','w') as log:
  p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT);Path(str(tag)+'.process.json').write_text(json.dumps(dict(pid=p.pid,cmd=cmd)));rc=p.wait()
 Path(str(tag)+'.exit.json').write_text(json.dumps(dict(exit_code=rc)));print(tag,rc,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as e:list(e.map(job,jobs))
