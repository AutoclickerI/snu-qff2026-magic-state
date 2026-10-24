import os,sys,json
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
os.environ['XTIM_TWIRL_CACHE_DIR']=str(OUT/'.xtim_cache')
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.path.insert(0,str(OUT))
from audit import exact2,evaluate,model
import tprep.qasm
# Only relax adjacency; no noise strengths or timing changes.
tprep.qasm.adjacent=lambda a,b:True
st=OUT/sys.argv[1];data=json.loads(st.with_suffix('.json').read_text())['data_qubits'];row=evaluate(exact2.Eval(st.with_suffix('.qasm').read_text(),data));st.with_suffix('.moments.json').write_text(json.dumps(row,indent=2));print(json.dumps(row))
