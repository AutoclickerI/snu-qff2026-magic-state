import os,sys,json,hashlib
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'EVAL'))
from exact2 import Eval
from ledger import merge
for name in sys.argv[1:]:
    st=H/'builds'/name;md=json.loads(st.with_suffix('.json').read_text());ev=Eval(st.with_suffix('.qasm').read_text(),md['data_qubits'])
    sha=hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest();v=ev.fp*ev.n_single
    ids=[int(i) for i in v.argsort()[::-1] if v[i]>1e-12]
    top=[dict(loss=float(v[i]),fault=ev.fault_label(i)) for i in ids[:12]]
    out=dict(first_order_loss=float(v.sum()),harmful_faults=len(ids),top=top,scope='exact single-fault diagnostic at p=.001, not an all-orders ranking')
    merge(sha,dict(single_fault=out));print(name,json.dumps(out),flush=True)
