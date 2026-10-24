import os,sys,json,math
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import tick_build as tb
H=Path(__file__).resolve().parent
singles=json.loads((H/'tick_singles.json').read_text());pool={int(r['stem'][1:3]):r['gadgets'][0] for r in singles}
rows=json.loads((H/'multi_screen.json').read_text());audit=[]
for r in rows:
 if 'error' not in r:continue
 old=r['error'];gs=[pool[i] for i in r['ids']];stem=tb.emit(r['stem'],gs);ev=tb.Eval(stem.with_suffix('.qasm').read_text(),tb.DATA)
 a=math.exp(-float(ev.fp@(1-ev.a_single)));r.update(exp_minus_A1=a,previous_error=old,screened_acceptance=a<.5002,detectors=ev.m.n_det)
 if a<.5002:del r['error']
 audit.append({k:r[k] for k in ('stem','exp_minus_A1','previous_error','screened_acceptance','detectors')})
 print(json.dumps(audit[-1]),flush=True)
(H/'multi_capacity_audit.json').write_text(json.dumps(audit,indent=2));(H/'multi_screen.json').write_text(json.dumps(rows,indent=2))
