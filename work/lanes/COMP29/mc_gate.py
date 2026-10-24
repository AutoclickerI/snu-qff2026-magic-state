"""Run the requested unchanged MC script only after the actual speed/judge gate."""
import os,sys,subprocess,json
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1';os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
name=sys.argv[1];procs=sys.argv[2] if len(sys.argv)>2 else '8'
subprocess.run([str(ROOT/'.venv/bin/python'),str(H/'gate.py'),name],check=True)
gate=json.loads((H/(name+'.gate.json')).read_text())
assert gate['speed']['classification']=='FAST' and gate['passed'],gate
with (H/(name+'.mc.log')).open('w') as f:
    subprocess.run([str(ROOT/'.venv/bin/python'),str(H/'mc3.py'),str(H/name),'--procs',procs],stdout=f,stderr=subprocess.STDOUT,check=True)
print((H/(name+'.mc.log')).read_text(),flush=True)
