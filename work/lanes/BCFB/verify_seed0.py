import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,time,hashlib
H=Path(__file__).resolve().parent;ROOT=H.parents[2];sys.path.insert(0,str(ROOT/'work'));os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
import fast_check,reorder
md=json.loads((H/'best_seed0.json').read_text());text=(H/'best_seed0.qasm').read_text();base=(H/'best.qasm').read_text();assert reorder.signature(text)==reorder.signature(base)
t=time.monotonic();r=fast_check.check(text,md['data_qubits'],shots=10**8,seed=0,procs=int(sys.argv[1]));assert r.passed and r.acceptance>=.505
assert abs(r.score-md['recorded_seed0_score'])<1e-15,(r.score,md['recorded_seed0_score']);assert r.acceptance==md['recorded_seed0_acceptance']
out=dict(passed=bool(r.passed),shots=10**8,seed=0,score=float(r.score),sem=float(r.sem),acceptance=float(r.acceptance),CX=int(r.n_2q),reorder_draw=md['reorder_draw'],bit_identical_score=bool(r.score==md['recorded_seed0_score']),noise_signature_equal=True,sha256=hashlib.sha256(text.encode()).hexdigest(),seconds=time.monotonic()-t)
(H/'SEED0_VERIFICATION.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
