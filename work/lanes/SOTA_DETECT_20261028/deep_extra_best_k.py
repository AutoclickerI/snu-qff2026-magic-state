"""Use genuine spare ancilla for a physical extra GHZ parity flag."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,itertools
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'work/lanes/CAT3_20261027'),str(R/'work/lanes/END2_20261027')]
import smallcat as s
from joint import emit
base=H/'deep_hybrid/deep_007';orig,dets=s.f.parse_current(base.with_suffix('.qasm').read_text());used={(o.time,q)for o in orig for q in o.qs}
out=H/'deep_extra_best_k';out.mkdir(exist_ok=True);rows=[]
for begin in range(8,10):
 for u,v in itertools.permutations(range(7),2):
  add=[s.f.Op('R',(35,),begin),s.f.Op('CX',(28+u,35),begin+1),s.f.Op('CX',(28+v,35),begin+2),s.f.Op('M',(35,),begin+3,max(o.bit or 0 for o in orig)+1)]
  if any((o.time,q)in used for o in add for q in o.qs):continue
  d=dets+[{add[-1].bit}];text=emit(orig+add,d);raw=s.ideal_contract_check(text,list(range(7)))
  if not raw['ok']:continue
  stem=out/f'flag_{begin}_{u}_{v}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps({'data_qubits':list(range(7)),'abstract':True,'extra_flag':[begin,u,v]}))
  val=s.exact(stem);row={'begin':begin,'u':u,'v':v,'loss':val['loss'],'acceptance':val['acceptance'],'stem':str(stem)};rows.append(row)
  (H/'deep_extra_best_k_results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(row),flush=True)
print('DONE',len(rows),flush=True)
