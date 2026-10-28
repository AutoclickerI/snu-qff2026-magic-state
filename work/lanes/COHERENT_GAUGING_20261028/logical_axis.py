import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path[:0]=[str(R/'work/tools'),str(R/'upstream/snu-qff2026-problem'),str(R/'work/lanes/EXPAND2_20261027')]
import frontend_axis as f
from tprep.exact import run
P=H/'seed_t';ops,_=f.parse_current(P.with_suffix('.qasm').read_text());D=[0,11,9,26,12,21,14]
for kind in ('T','TDG'):
 oo=ops+[f.Op(kind,(q,),18)for q in D]+[f.Op('MX',(q,),19,4+i)for i,q in enumerate(D)];oo.sort(key=lambda o:o.time)
 native,_=f.native_text(oo);state,inv,records,_,wire=run(native,36)
 ps=state.stim.PauliString(state.n)
 for w in records[-7:]:ps[w]='Z'
 print(json.dumps({'rotation_before_MX':kind,'logical_parity_expectation':state.expectation(ps,inv)}))
