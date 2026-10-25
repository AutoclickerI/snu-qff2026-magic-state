import os,sys,json,hashlib,time
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'BUNDLE'))
from ev import price_stem,EVH
from ledger import merge
TAU=3.761821654835085e-5
def price(st):
    st=Path(st).resolve();sha=hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest()
    r=price_stem(st);md=json.loads(st.with_suffix('.json').read_text())
    r.update(sha256=sha,stem=str(st),data_qubits=md['data_qubits'],evaluator_hash=EVH,
             what_moved=md.get('source',md.get('complete_change','')),cx=md.get('cx'),depth=md.get('native_depth'))
    if 'loss' in r:r.update(J_tau=r['acceptance']*(r['loss']-TAU),tau=TAU)
    (H/'logs'/f'{st.name}.price.json').write_text(json.dumps(r,indent=2))
    merge(sha,r);print(json.dumps(r),flush=True)
    return r
if __name__=='__main__':
    for st in sys.argv[1:]:price(H/'builds'/st)
