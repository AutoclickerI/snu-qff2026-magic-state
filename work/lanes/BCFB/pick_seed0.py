import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,random,hashlib
H=Path(__file__).resolve().parent;ROOT=H.parents[2];sys.path.insert(0,str(ROOT/'work'))
import reorder
sel=json.loads((H/'FINAL_SELECTION.json').read_text());tag=sel['selected'];rows={}
for name in json.loads((H/'redraw_manifest.json').read_text())[tag]:
 for l in (H/name).read_text().splitlines():
  if l.startswith('{"draw"'):
   r=json.loads(l);rows[r['draw']]=r
assert set(rows)==set(range(100))
k=min(rows,key=lambda k:rows[k]['score']);text=(H/'best.qasm').read_text();var='\n'.join(reorder.shuffle(text.split('\n'),random.Random(k)));assert reorder.signature(var)==reorder.signature(text)
md=json.loads((H/'best.json').read_text());md.update(reordered_from='best.qasm',reorder_draw=k,recorded_seed0_score=rows[k]['score'],recorded_seed0_acceptance=rows[k]['acceptance'],noise_signature_equal=True)
(H/'best_seed0.qasm').write_text(var);(H/'best_seed0.json').write_text(json.dumps(md,indent=2));print(json.dumps(dict(draw=k,recorded=rows[k],sha256=hashlib.sha256(var.encode()).hexdigest())))
