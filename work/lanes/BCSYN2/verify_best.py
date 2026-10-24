import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import hashlib,json,re
from pathlib import Path
import tprep
from synth import verify
H=Path(__file__).resolve().parent;os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
a=json.loads((H/'best.json').read_text());text=(H/'best.qasm').read_text();src=H/'full/fb_s401_0035.qasm';assert src.read_text()==text
v=verify(a['prep']);assert v['stim_target_pass'] and v['clean_pass'];ck=tprep.check(text,a['data_qubits'],shots=10**6,seed=0)
r=dict(sha256=hashlib.sha256(text.encode()).hexdigest(),source=str(src.relative_to(H)),identical_to_MC_circuit=True,prep_verification=v,check=dict(passed=bool(ck.passed),format=bool(ck.format_ok),class_ok=bool(ck.class_ok),correctness=bool(ck.correct_ok),acceptance=float(ck.acceptance),score=float(ck.score),CX=int(ck.n_2q)),R=a['R'],data_qubits=a['data_qubits'])
assert ck.passed;(H/'BEST_VERIFICATION.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
