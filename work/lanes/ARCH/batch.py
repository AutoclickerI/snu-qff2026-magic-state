"""Bounded subprocess batch; every child exit is awaited."""
import os
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import sys
import json
import subprocess
import concurrent.futures
from pathlib import Path
HERE=Path(__file__).resolve().parent
def one(name):
    cmd=[sys.executable,str(HERE/'evaluate.py'),name]+sys.argv[2:]
    with (HERE/(name+('.third.log' if '--third' in cmd else '.screen.log'))).open('w') as f:
        r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,cwd=HERE,env=os.environ)
    print(name,r.returncode,flush=True)
    return r.returncode
names=json.loads((HERE/sys.argv[1]).read_text())
if names and isinstance(names[0],dict): names=[x['name'] for x in names]
with concurrent.futures.ThreadPoolExecutor(max_workers=24) as pool:
    results=list(pool.map(one,names))
sys.exit(bool(any(results)))
