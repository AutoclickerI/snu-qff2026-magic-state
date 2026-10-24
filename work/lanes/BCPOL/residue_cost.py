"""Exterior mixed-fault cost of each accepted correctable B residue."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent
from cache import setup
from boundary import audit,pack
from synth import B,C
import json,numpy as np
stem=H/'inputs/replay_policy';ev,b,classes,prep,ext,hh=setup(stem);_,_,rec=audit(stem);z=np.load(H/'boundary.cache.npz',allow_pickle=True);assert hh==str(z['ext_hash'])
g={(r['q'],r['pauli']):r['packed'] for r in rec['generators']};rows=[]
for i in range(7):
 k=b.express(g[B[i],'X']^g[C[i],'X']);N,A=z['response'];rows.append(dict(class_signature=9+i,boundary_class=k,ideal_N=float(N[0,k]),ideal_A=float(A[0,k]),external_first_N=float(N[1,k]),external_second_N=float(N[2,k])))
(H/'residue_cost.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows),flush=True)
