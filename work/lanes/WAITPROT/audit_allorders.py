import os,sys,json
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import allorders as aw
H=Path(__file__).resolve().parent;rows=[]
for p in H.glob('*.allorders.json'):
 r=json.loads(p.read_text());stem=Path(r['source']).name
 proof=aw.audit(H/stem);r['frontend_audit']=proof;p.write_text(json.dumps(r,indent=2));rows.append(dict(stem=stem,**proof));print(json.dumps(rows[-1]),flush=True)
(H/'allorders_audit.json').write_text(json.dumps(rows,indent=2))
