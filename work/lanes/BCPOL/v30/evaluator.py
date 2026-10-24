"""Judge-model all-orders evaluation, including explicit logical FRAME records.

The sparse contraction is the unchanged MAIN implementation. Only its model
construction is replaced by exact2's complete judge frontend when requested.
"""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
V=Path(__file__).resolve().parent;H=V.parent;ROOT=H.parents[2]
os.environ.setdefault('XTIM_TWIRL_CACHE_DIR',str(H/'.xtim_cache'))
sys.path[:0]=[str(V/'sparse'),str(H),str(ROOT/'work/lanes/EVAL')]
import sparse_walsh as sw
import exact2
import numpy as np,json,math,collections,time,argparse

def prepare_model(stem,canonicalize=True,ev=None):
    md=json.loads(stem.with_suffix('.json').read_text())
    ev=ev or exact2.Eval(stem.with_suffix('.qasm').read_text(),md['data_qubits'])
    m,e=ev.m,ev.e
    for ch in m.chans:ch['p']=ch['prob']
    changes=sw.canonicalize_detector_rows(m,e) if canonicalize else {}
    if changes:e=type(e)(m)
    m.detector_row_changes=changes
    nd,nr=len(m.proj_m),len(m.rots);active=[i for i,p in enumerate(e.projs) if p[:2]!=(0,0)]
    assert nr<=20 and e.r<=8,(nr,e.r)
    assert all(p[0]==0 for p in e.projs) and all(v==0 for v in e.v),'unsupported projector/reference basis'
    A0,N0=e.ntable(0,0);assert A0>1-1e-10 and abs(N0[0])<1e-10,(A0,N0[0])
    ks=tuple(active+list(range(nd,nd+nr)));states=np.arange(1<<nr,dtype=np.uint32)
    psi=np.zeros((len(states),e.N),complex);psi[:,0]=1
    for j,(mj,wj,c,t) in enumerate(e.rot):
        signs=1-2*((states>>j)&1).astype(np.int8)
        psi=np.cos(t)*psi+(1j*math.sin(t)*c)*signs[:,None]*(psi*e.sgn(wj)[None,:])[:,e.idx.astype(int)^mj]
    dv=np.zeros(e.N,dtype=np.int32)
    for j,i in enumerate(active):dv|=(np.bitwise_count(np.arange(e.N)&e.projs[i][1])%2)<<j
    where=[np.flatnonzero(dv==v) for v in range(1<<len(active))]
    groups=collections.defaultdict(list)
    for f in m.faults:groups[f['chan']].append(f)
    scopes=[]
    for fs in groups.values():
        u=0
        for f in fs:u|=f['d']|(f['s']<<nd)
        scopes.append({i for i in range(u.bit_length()) if u>>i&1})
    return m,e,groups,nd,ks,psi,where,sw.minfill(scopes+[set(ks)])

def run(stem,judge=False):
    original=sw.prepare
    if judge:sw.prepare=prepare_model
    try:r=sw.run(stem,72,True)
    finally:sw.prepare=original
    r['judge_frontend']=judge
    r['qasm_sha256']=__import__('hashlib').sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest()
    stem.with_suffix('.allorders.json').write_text(json.dumps(r,indent=2)+'\n')
    return r

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stem',type=Path);p.add_argument('--judge-model',action='store_true');a=p.parse_args();run(a.stem,a.judge_model)
