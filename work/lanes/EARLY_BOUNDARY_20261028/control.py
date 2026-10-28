import os,sys,json
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path(__file__).resolve().parents[3];H=Path(__file__).parent;sys.path[:0]=[str(R/'work/tools'),str(R/'work/lanes/END2_20261027')]
from qtools.evaluator import frontend as f
from qtools import write_stem,price
from qtools.validity import raw_check
from joint import emit
P=next((R/'work/lanes/SOTA_RESOURCE_20261028/geometry_cand').glob('six_measured_baseline*.qasm'));ops,dets=f.parse_current(P.read_text())
for o in ops:
 if o.time>=39:o.time+=4
text=emit(ops,dets);D=[6,20,19,10,2,22,16];stem=write_stem(text,D,H,'delay_only');raw=raw_check(text,D);p=price(stem,1);print(json.dumps(dict(raw=raw,loss=p['loss'],acceptance=p['acceptance'])),flush=True);stem.with_suffix('.result.json').write_text(json.dumps(dict(raw=raw,exact=p),indent=2)+'\n')
