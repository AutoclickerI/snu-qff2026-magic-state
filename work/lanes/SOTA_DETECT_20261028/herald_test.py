import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,itertools
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'work/tools'),str(ROOT/'work/lanes/EXPAND2_20261027'),str(ROOT/'work/lanes/END2_20261027')]
import frontend_axis as f
from axis_echo import exact
from qtools.validity import raw_check
from qtools import write_stem
from joint import emit
BASE=HERE/'accept_cand/one_0'
text=BASE.with_suffix('.qasm').read_text();data=json.loads(BASE.with_suffix('.json').read_text())['data_qubits'];orig,ds=f.parse_current(text)
specs=[('M',13,34),('M',31,41),('M',33,39),('MX',14,35)]
results=[]
for n in range(1,5):
 for combo in itertools.combinations(specs,n):
  ops=list(orig);dets=[set(x) for x in ds];b=max(o.bit or 0 for o in ops)+1
  for i,(kind,q,t) in enumerate(combo):ops.append(f.Op(kind,(q,),t,b+i));dets.append({b+i})
  text=emit(ops,dets);raw=raw_check(text,data)
  if not raw['ok']:print('invalid',combo,flush=True);continue
  stem=write_stem(text,data,HERE/'heralds','h'+'_'.join(f'{q}t{t}' for _,q,t in combo),source={'parent':str(BASE),'heralds':combo})
  score=exact(stem);row={'combo':combo,'stem':str(stem),'loss':score['loss'],'acceptance':score['acceptance'],'raw':raw};results.append(row)
  (HERE/'heralds.json').write_text(json.dumps(results,indent=2)+'\n')
  print(json.dumps({k:row[k] for k in ('combo','loss','acceptance')}),flush=True)
