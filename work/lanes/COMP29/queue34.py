"""Finite sparse-evaluation queue; stream complete receipts on child exit."""
import os,sys,json,subprocess,concurrent.futures
from pathlib import Path
H=Path(__file__).resolve().parent
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
names=json.loads((H/sys.argv[1]).read_text());workers=int(sys.argv[2]);procs=int(sys.argv[3]) if len(sys.argv)>3 else 1
def job(n):
    with (H/(n+'.allorders.log')).open('w') as f:
        p=subprocess.run([sys.executable,str(H/'price34.py'),n,str(procs)],stdout=f,stderr=subprocess.STDOUT)
    receipt=H/(n+'.allorders.json')
    r=json.loads(receipt.read_text()) if receipt.exists() else dict(error='no receipt')
    return dict(stem=n,result=r,exit_code=p.returncode)
with concurrent.futures.ThreadPoolExecutor(workers) as pool:
    fs=[pool.submit(job,n) for n in names]
    for f in concurrent.futures.as_completed(fs):print(json.dumps(f.result()),flush=True)
