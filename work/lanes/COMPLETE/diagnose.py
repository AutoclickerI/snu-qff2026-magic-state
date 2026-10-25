"""Exact matched counterfactuals; never promoted as physical circuits."""
import os,sys,json,hashlib,re,io,contextlib,time
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'BUNDLE'))
from ev import sw,EVH
import frontend as fa
from ledger import merge
def run(name,kind):
    st=H/'builds'/name;p=json.loads(st.with_suffix('.plan.json').read_text())
    selected={(o['t'],tuple(map(int,re.findall(r'q\[(\d+)\]',o['lines'][0])))) for o in p['ops'] if o.get('stage') in ('completion','restore')}
    sha=hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest();t0=time.time()
    with contextlib.redirect_stdout(io.StringIO()):
        m,eng,groups,nd,ks,psi,where,dense=sw.prepare(st,True)
        prog,blocks=fa.noise_blocks(m.native,.001,first_order=False);_,_,gaps=fa.schedule(m.native)
        kidx=[b.index(ins.text) for ins,b in zip(prog,blocks)]
        gapstart={(i,q):(tt,n) for i,q,tt,n in gaps};keep={};removed=0
        for k,fs in groups.items():
            ch=m.chans[k];ii=ch['ins'];op=m.labels[ii]
            idle=ch['name']=='DEPOLARIZE1' and ch['jl']>=kidx[ii]+2
            hit=(not idle and (op.time,tuple(op.qs)) in selected) if kind=='completion_route_gates' else (idle and 23<=gapstart.get((ii,ch['qs'][0]),(-1,0))[0]<p['meta']['native_depth']-4)
            if hit:removed+=1
            else:keep[k]=fs
        compiled,elim=sw.compile_best(m,eng,keep,nd,ks);sw._CTX.update(eng=eng,ks=ks,psi=psi,where=where,compiled=compiled,elim=elim)
        rows=[sw._row(k) for k in [None]+eng.keys];A=rows[0]['value'];O=sum(w*b*r['value'] for w,b,r in zip(eng.W,eng.beta,rows[1:]))
    r=dict(loss=(A-O)/(2*A),acceptance=A,dropped_channels=removed,seconds=time.time()-t0,
      counterfactual=kind,qasm_sha256=sha,evaluator_hash=EVH,scope='operation noise only' if kind=='completion_route_gates' else 'all physical-qubit idle runs starting from23 until depth-4; overlapping diagnostic, not additive')
    merge(sha,dict(diagnostics={kind:r}));print(name,json.dumps(r),flush=True)
if __name__=='__main__':
    for name in ['swap8_2_restore','swap8_14_restore','swap8_9_restore']:
        for kind in ['completion_route_gates','preround_idle']:run(name,kind)
