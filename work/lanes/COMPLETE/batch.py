import os,sys,json,hashlib,multiprocessing as mp,contextlib
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'BUNDLE'))
from ev import price_stem,EVH
from price import TAU
from ledger import merge
def job(name):
    st=H/'builds'/name;sha=hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest()
    r=price_stem(st);md=json.loads(st.with_suffix('.json').read_text())
    r.update(sha256=sha,stem=str(st),data_qubits=md['data_qubits'],evaluator_hash=EVH,
             what_moved=md.get('source',''),cx=md.get('cx'),depth=md.get('native_depth'))
    if 'loss' in r:r.update(J_tau=r['acceptance']*(r['loss']-TAU),tau=TAU)
    return r
def run(names,workers=3):
    unique={};outputs={};prior=json.loads((H/'results.json').read_text())
    for name in names:
        st=H/'builds'/name;sha=hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest()
        dq=json.loads(st.with_suffix('.json').read_text())['data_qubits']
        if sha in outputs:assert outputs[sha]==dq,('same QASM, different ordered outputs',name)
        outputs[sha]=dq
        unique.setdefault(sha,[]).append(name)
    pending=[]
    for sha,aliases in unique.items():
        old=prior.get(sha)
        if old:assert old.get('data_qubits',outputs[sha])==outputs[sha],('ledger output-mapping collision',sha)
        if old and old.get('evaluator_hash')==EVH and old.get('data_qubits')==outputs[sha]:
            update=dict(aliases=aliases)
            if 'loss' in old:update.update(tau=TAU,J_tau=old['acceptance']*(old['loss']-TAU))
            merge(sha,update)
        else:pending.append(aliases[0])
    with (mp.get_context('fork').Pool(workers) if workers else contextlib.nullcontext(None)) as pool:
        for r in (pool.imap_unordered(job,pending) if pool else map(job,pending)):
            r['aliases']=unique[r['sha256']]
            (H/'logs'/f'{Path(r["stem"]).name}.price.json').write_text(json.dumps(r,indent=2))
            merge(r['sha256'],r)
            print(json.dumps(r),flush=True)
if __name__=='__main__':
    if sys.argv[1]=='catalog':
        rows=json.loads((H/'a_catalog.json').read_text());names=[r['stem'] for fam in rows.values() for r in fam if 'stem' in r]
    else:names=sys.argv[1:]
    run(names)
