"""Lane-local exact native S/Sdg extension; no shared cache or source changes."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import hashlib,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'work/tools'))
import frontend_clifford as local
from qtools.evaluator import sparse_walsh as sw
from qtools.pricing import _calculate
from qtools.version import EVALUATOR_VERSION

def price(stem):
    t=time.perf_counter();stem=Path(stem);text=stem.with_suffix('.qasm').read_bytes()
    data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
    original=sw.fa;original_parser=sw.parse_current
    try:
        sw.fa=local;sw.parse_current=local.parse_current
        r=_calculate(text,data,1,save_basis=False)
        local.DATA=list(data);ops,dets=local.parse_current(text.decode());m=local.make_model(ops,dets);e=local.Engine(m)
        a,n=e.ntable(0,0);assert abs(a-1)<1e-12 and abs(n[0])<1e-12,(a,n[0])
    finally:sw.fa=original;sw.parse_current=original_parser
    r.update(qasm_sha256=hashlib.sha256(text).hexdigest(),data_qubits=data,
        evaluator='pinned sparse-Walsh contraction with lane-local native S/Sdg frontend',
        pinned_evaluator_version=EVALUATOR_VERSION,
        frontend_sha256=hashlib.sha256(Path(local.__file__).read_bytes()).hexdigest(),
        noiseless_model_acceptance=a,noiseless_model_loss_numerator=float(n[0]),seconds=time.perf_counter()-t)
    return r

if __name__=='__main__':print(json.dumps(price(sys.argv[1]),indent=2),flush=True)
