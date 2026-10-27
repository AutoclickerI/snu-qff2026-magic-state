"""Lane-local extension of qtools to affine logical frames. No shared code edits."""
from pathlib import Path
import copy, hashlib, json, math, re, sys, time
from collections import defaultdict
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'work/tools'))
sys.path.insert(0,str(ROOT/'upstream/snu-qff2026-problem'))
from qtools.evaluator import frontend as f, sparse_walsh as sw
HERE=Path(__file__).resolve().parent
OUT=HERE/'cand';OUT.mkdir(exist_ok=True)

def load(stem):
    stem=Path(stem)
    text=stem.with_suffix('.qasm').read_text()
    ops,dets=f.parse_current(text)
    md=json.loads(stem.with_suffix('.json').read_text())
    return ops,dets,md

def emit(name,ops,dets,data,frame=None,metadata=None):
    used=set(q for o in ops for q in o.qs)
    maxbit=max([o.bit for o in ops if o.bit is not None]+[0])
    lines=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{maxbit+1}];']
    old=None
    for o in sorted(ops,key=lambda o:o.time):
        if old is not None and o.time!=old:
            lines.append('barrier '+','.join(f'q[{q}]' for q in sorted(used))+';')
        old=o.time
        q=o.qs[0]
        if o.kind in ('R','RX'):
            lines.append(f'reset q[{q}];')
            if o.kind=='RX':lines.append(f'h q[{q}];')
        elif o.kind in ('M','MX'):
            if o.kind=='MX':lines.append(f'h q[{q}];')
            lines.append(f'measure q[{q}] -> c[{o.bit}];')
            if o.kind=='MX':lines.append(f'h q[{q}];')
        elif o.kind=='CX':lines.append(f'cx q[{q}],q[{o.qs[1]}];')
        else:lines.append({'TDG':'tdg','T_DAG':'tdg','ID':'id'}.get(o.kind,o.kind.lower())+f' q[{q}];')
    lines+=['// DETECTOR '+' '.join(f'c[{b}]' for b in sorted(row)) for row in dets if row]
    if frame is not None:
        for P in 'XZ':
            c,bits=frame[P]
            lines.append(f'// FRAME_{P}({c}) '+' '.join(f'c[{b}]' for b in sorted(bits)))
    stem=OUT/name
    stem.with_suffix('.qasm').write_text('\n'.join(lines)+'\n')
    stem.with_suffix('.json').write_text(json.dumps({'data_qubits':data,'metadata':metadata or {}},indent=2)+'\n')
    return stem

def parse_frames(text):
    out={'X':(0,set()),'Z':(0,set())}
    for P,c,bits in re.findall(r'//\s*FRAME_([XZ])\(([01])\)([^\n]*)',text):
        row=set()
        for b in map(int,re.findall(r'c\[(\d+)\]',bits)):
            if b in row:row.remove(b)
            else:row.add(b)
        out[P]=(int(c),row)
    return out

def raw_check(text,data):
    from tprep.qasm import to_stim
    from tprep.parse import declarations
    from tprep.exact import verify,run
    stxt,errors=to_stim(text)
    if errors:return dict(ok=False,errors=errors,six_stabilizers=[])
    frames,post=declarations(stxt)
    assert not post,'lane frame engine does not handle postselection'
    result=verify(stxt,data,frame=frames)
    state,inv,_,_,wires=run(stxt,36)
    values=[]
    for P in 'XZ':
        for S in f.SUPPORTS:
            obs=state.stim.PauliString(state.n)
            for j in S:obs[wires[data[j]]]=P
            values.append(state.expectation(obs,inv))
    result.pop('detector_values',None)
    result['six_stabilizers']=values
    result['ok']=not result['errors'] and all(abs(v-1)<1e-9 for v in values)
    return result

def frame_model(ops,dets,data,frames,all_orders=True):
    f.DATA=list(data)
    original=f.noise_blocks
    if all_orders:f.noise_blocks=lambda text,p,first_order=True:original(text,p,first_order=False)
    try:m=f.make_model(ops,dets)
    finally:f.noise_blocks=original
    cx,xbits=frames['X'];cz,zbits=frames['Z']
    products={}
    for T,bits in [('X',zbits),('Y',xbits^zbits)]:
        p=(0,0,1)
        for b in sorted(bits):p=f.mul(p,m.record_ps[b])
        products[T]=p
    m.Q={key:f.mul(value,products[key[0]]) for key,value in m.Q.items()}
    m.cz=cz;m.cxz=cx^cz
    for fault in m.faults:
        flips=set(fault['record_flips'])
        fault['e']|=((len(flips&zbits)%2)<<8)|((len(flips&(xbits^zbits))%2)<<9)
    return m

def prepare(stem):
    text=stem.with_suffix('.qasm').read_text()
    ops,dets,md=load(stem)
    data=md['data_qubits'];frames=parse_frames(text)
    m=frame_model(ops,dets,data,frames)
    eng=f.Engine(m)
    changes=sw.canonicalize_detector_rows(m,eng)
    if changes:eng=f.Engine(m)
    nd,nr=len(dets),len(m.rots)
    active=[i for i,p in enumerate(eng.projs) if p[:2]!=(0,0)]
    assert all(p[0]==0 for p in eng.projs),'non-diagonal projector'
    assert all(v==0 for v in eng.v),'nonzero reference'
    assert nr<=20
    A0,N0=eng.ntable(0,0)
    assert A0>1-1e-10 and abs(N0[0])<1e-10,(A0,N0[0])
    ks=tuple(active+list(range(nd,nd+nr)))
    psi=np.zeros((1,eng.N),dtype=np.complex128);psi[:,0]=1
    for mj,wj,coef,theta in eng.rot:
        turn=(1j*math.sin(theta)*coef)*(psi*eng.sgn(wj)[None,:])[:,eng.idx.astype(int)^mj]
        psi=np.concatenate([np.cos(theta)*psi+turn,np.cos(theta)*psi-turn])
    dvals=np.zeros(eng.N,dtype=np.int32)
    for j,i in enumerate(active):
        dvals|=(np.bitwise_count(np.arange(eng.N)&eng.projs[i][1])%2)<<j
    where=[np.flatnonzero(dvals==v) for v in range(1<<len(active))]
    groups=defaultdict(list)
    for fault in m.faults:groups[fault['chan']].append(fault)
    return m,eng,groups,nd,ks,psi,where

def price(stem):
    start=time.perf_counter()
    stem=Path(stem).resolve();text=stem.with_suffix('.qasm').read_text()
    data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
    raw=raw_check(text,data)
    result={'stem':str(stem.relative_to(ROOT)),'raw':raw,'sha256':hashlib.sha256(text.encode()).hexdigest()}
    if not raw['ok']:return result
    m,eng,groups,nd,ks,psi,where=prepare(stem)
    compiled,elim=sw.compile_best(m,eng,groups,nd,ks,save=False)
    sw._CTX.update(eng=eng,ks=ks,psi=psi,where=where,compiled=compiled,elim=elim)
    try:
        rows=[sw._row(k) for k in [None]+eng.keys]
        A=rows[0]['value']
        obs=sum(w*b*r['value'] for w,b,r in zip(eng.W,eng.beta,rows[1:]))
        result.update(loss=float((A-obs)/(2*A)),acceptance=float(A),width=elim['width'],
            rank_rot=eng.rank_rot,rank_total=eng.r,seconds=time.perf_counter()-start,
            cx=sum(o.kind=='CX' for o in load(stem)[0]),
            kernel_omission_sum=sum(r['absolute_kernel_omission_bound'] for r in rows))
    finally:
        sw._CTX.clear();sw.COLUMNS.clear()
    Path(str(stem)+'.price.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

def singles(stem):
    ops,dets,md=load(stem);frames=parse_frames(stem.with_suffix('.qasm').read_text())
    m=frame_model(ops,dets,md['data_qubits'],frames,False);e=f.Engine(m)
    harm=[];cache={}
    for fault in m.faults:
        key=(fault['s'],fault['d'])
        if key not in cache:cache[key]=e.ntable(*key)
        a,n=cache[key]
        val=0 if n is None else fault['p']*n[fault['e']]
        if val>1e-14:harm.append({'weight':float(val),'acceptance':a,**fault})
    return {'first_order_loss':sum(v['weight'] for v in harm),'harmful_count':len(harm),
            'harmful':sorted(harm,key=lambda v:-v['weight'])}

if __name__=='__main__':
    print(json.dumps(price(Path(sys.argv[1])),indent=2),flush=True)

