import os,sys,json
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path.cwd(); here=R/'work/lanes/SOTA_RESOURCE_20261028'
sys.path[:0]=[str(R/'work/tools'),str(R/'work/lanes/EXPAND2_20261027'),str(R/'work/lanes/END2_20261027')]
from qtools.validity import raw_check
from joint import emit
import frontend_axis as f
base=R/'work/lanes/EXPAND2_20261027/release_phase/native_incumbent_phase_late'
ops,dets=f.parse_current(base.with_suffix('.qasm').read_text()); spec=json.loads(base.with_suffix('.json').read_text()); data=spec['data_qubits']
rows=[]
for i,o in enumerate(ops):
 if o.kind!='CX' or not 30<=o.time<=46:continue
 text=emit(ops[:i]+ops[i+1:],dets)
 try: raw=raw_check(text,data)
 except Exception as e: rows.append({'index':i,'gate':str(o),'exception':str(e)}); continue
 row={'index':i,'gate':str(o),'raw':raw};rows.append(row)
 if raw['ok']:
  name=here/f'delete_{i}';name.with_suffix('.qasm').write_text(text);name.with_suffix('.json').write_text(json.dumps(spec,indent=2)+'\n')
 print(i,o.time,o.qs,raw['ok'],flush=True)
(here/'screen.json').write_text(json.dumps(rows,indent=2)+'\n')
