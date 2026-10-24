import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import subprocess,json,time,socket
from pathlib import Path
H=Path(__file__).resolve().parent;D=H/'blue';stems=[c+'_'+s for c in ['v25k','v26n'] for s in ['fb_d14_c98_s517_00020_preserve','fb_d15_c105_s506_00008_preserve_rt1','fast_d15_c105_s526_00356_preserve_rt1']]
for stem in stems:
 pr=subprocess.run([sys.executable,str(H/'blue_verify.py'),stem,'--exact','--procs','6']);assert pr.returncode==0
print(json.dumps(dict(event='ALL_PORTS_EXACT_DONE')),flush=True)
