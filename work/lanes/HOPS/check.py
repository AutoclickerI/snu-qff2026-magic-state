import os,sys,json
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
import tprep
OUT=Path(__file__).resolve().parent
for name in sys.argv[1:]:
 stem=OUT/name;r=tprep.check(stem.with_suffix('.qasm').read_text(),json.loads(stem.with_suffix('.json').read_text())['data_qubits'],shots=10**6,seed=0)
 row=dict(passed=r.passed,acceptance=r.acceptance,score=r.score,repr=str(r));stem.with_suffix('.check.json').write_text(json.dumps(row,indent=2)+'\n');print(name,row,flush=True)
