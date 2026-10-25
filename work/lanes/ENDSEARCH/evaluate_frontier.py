import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,sys,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent
rows=json.loads((H/'manifest.json').read_text())
# Rank every frontier witness; process isolation is required to switch FRAME frontends.
for row in rows:
    name=row['name']
    if (H/'logs'/f'{name}.receipt.json').exists():continue
    p=subprocess.run([sys.executable,str(H/'price.py'),name,'1'],capture_output=True,text=True)
    (H/'logs'/f'{name}.process.log').write_text(p.stdout+p.stderr)
    if p.returncode:
        print('FAILED',name,p.stderr[-2000:],flush=True)
    else:print(p.stdout.strip(),flush=True)
