import os,sys,json,time,hashlib
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
os.environ['TMPDIR']=str(H/'tmp')
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
sys.path.insert(0,str(H.parents[1]));from fast_check import check
TAU=3.761821654835085e-5;TARGET=TAU-1e-7
def run():
    rs=json.loads((H/'results.json').read_text());known={}
    for f in (H/'logs').glob('*.judge.json'):
        j=json.loads(f.read_text())
        if 'qasm_sha256' in j:known[j['qasm_sha256']]=j
    candidates=[r for r in rs.values() if 'loss' in r and r['loss']<TARGET and r['acceptance']>=.5002 and Path(r['stem']).name.startswith('v37')]
    out=[]
    for r in sorted(candidates,key=lambda r:r['J_tau']):
        st=Path(r['stem']);sha=hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest();assert sha==r['sha256']
        if sha in known:j=known[sha]
        else:
            t=time.time();rep=check(st.with_suffix('.qasm').read_text(),r['data_qubits'],shots=10**6,procs=1)
            j=dict(gates_ok=bool(rep.correct_ok),passed=bool(rep.passed),shots=10**6,seed=0,sampled_loss=rep.score,sampled_acceptance=rep.acceptance,seconds=time.time()-t,qasm_sha256=sha)
            (H/'logs'/f'{st.name}.judge.json').write_text(json.dumps(j,indent=2))
        print(st.name,json.dumps(j),flush=True)
        if not j['gates_ok'] or j['seconds']>20:
            out.append(dict(stem=str(st),eligible=False,judge=j));continue
        dest=H/'cand'/('complete_'+st.name.removeprefix('v37_'))
        dest.with_suffix('.qasm').write_bytes(st.with_suffix('.qasm').read_bytes())
        md=json.loads(st.with_suffix('.json').read_text());md.update(all_orders=r,judge_1e6=j,sha256=sha,base='MAIN/v37a')
        dest.with_suffix('.json').write_text(json.dumps(md,indent=2))
        out.append(dict(stem=str(st),candidate=str(dest),eligible=True,loss=r['loss'],acceptance=r['acceptance'],J_tau=r['J_tau'],sha256=sha,judge=j))
    (H/'finalists_v37.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':run()
