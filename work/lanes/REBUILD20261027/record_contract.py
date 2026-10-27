"""Exact deterministic-record completion using the magic-state Pauli quotient.

Enumerates the Pauli stabilizers of the rotation state (rank <= 8), then
finds record relations modulo those stabilizers. No Clifford surrogate.
Supports zero-frame/no-postselection qtools circuits. Full noisy ranking
remains separate from noiseless equivalence and single-fault diagnostics.
"""
import argparse, hashlib, json, os, sys
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'work/tools'))
import numpy as np
from qtools.evaluator import frontend as fa
from qtools import price, write_stem
from qtools.validity import raw_check

def reduce(v,basis):
    for p in sorted(basis,reverse=True):
        if v>>p&1: v^=basis[p]
    return v

def insert(v,basis):
    v=reduce(v,basis)
    if v: basis[v.bit_length()-1]=v
    return v

def model(text,data):
    fa.DATA=list(data)
    ops,dets=fa.parse_current(text)
    return fa.make_model(ops,dets),dets

def complete(m,dets):
    B=fa.Basis()
    for x,*_ in m.rots: B.add(x)
    r=len(B.vecs)
    if r>8: raise ValueError('4^rank enumeration budget exceeded')
    idx=np.arange(1<<r,dtype=np.uint64)
    def zcoord(z): return sum(((v&z).bit_count()&1)<<j for j,v in enumerate(B.vecs))
    def signs(w): return 1.-2.*(np.bitwise_count(idx&np.uint64(w))&1).astype(float)
    phi=np.zeros(len(idx),complex);phi[0]=1
    for x,z,c,theta,_ in m.rots:
        phi=np.cos(theta)*phi+1j*np.sin(theta)*c*(signs(zcoord(z))*phi)[idx^np.uint64(B.express(x))]
    def expect(x,w,c=1): return np.vdot(phi[idx^np.uint64(x)],c*signs(w)*phi)
    bits=sorted(m.record_ps)
    n=max([x.bit_length() for x,_,_ in m.record_ps.values()]+[v.bit_length() for v in B.vecs]+[1])
    stabs={}
    for xb in range(1<<r):
        physical=0
        for j,v in enumerate(B.vecs):
            if xb>>j&1: physical^=v
        for w in range(1<<r):
            if abs(abs(expect(xb,w,1j**((xb&w).bit_count())))-1)<1e-10:
                insert(physical|(w<<n),stabs)
    rb={};relations=[]
    for j,b in enumerate(bits):
        x,z,_=m.record_ps[b];v=reduce(x|(zcoord(z)<<n),stabs);wit=1<<j
        while v:
            lead=v.bit_length()-1
            if lead not in rb: rb[lead]=(v,wit);break
            vv,ww=rb[lead];v^=vv;wit^=ww
        if not v: relations.append(wit)
    supplied={};pos={b:j for j,b in enumerate(bits)}
    for row in dets: insert(sum(1<<pos[b] for b in row),supplied)
    rank0=len(supplied);missing=[]
    for wit in relations:
        if not insert(wit,supplied): continue
        row=[b for j,b in enumerate(bits) if wit>>j&1];p=(0,0,1)
        for b in row: p=fa.mul(p,m.record_ps[b])
        xb=B.express(p[0]);assert xb is not None
        ev=expect(xb,zcoord(p[1]),p[2])
        assert abs(abs(ev)-1)<1e-10 and abs(ev.imag)<1e-10,(row,ev)
        missing.append(dict(bits=row,reference=int(ev.real<0),expectation=float(ev.real)))
    return dict(rotation_rank=r,rotation_state_stabilizer_rank=len(stabs),records=len(bits),
                declared_rank=rank0,complete_rank=len(relations),missing=missing)

def singles(m):
    eng=fa.Engine(m);cache={};bad=[];c1=0.
    for f in m.faults:
        key=f['s'],f['d']
        if key not in cache: cache[key]=eng.table(*key)
        out=cache[key]
        if out is None: continue
        a,ev=out;n=float(.5*(a-eng.SG[f['e']]@ev))
        if n>1e-10:
            weight=f['p']/.001;c1+=weight*n;o=m.labels[f['ins']]
            bad.append(dict(label=f['label'],channel=f['chan'],time=o.time,operation=o.kind,
                            qubits=list(o.qs),pauli=f['pauli'],acceptance=a,loss_numerator=n,
                            c1_contribution=weight*n,record_flips=f['record_flips']))
    return dict(c1=c1,harmful_faults=bad,fault_components=len(m.faults))

def audit(stem,output,add_missing=False,exact=False):
    stem,output=Path(stem),Path(output);text=stem.with_suffix('.qasm').read_text()
    data=json.loads(stem.with_suffix('.json').read_text())['data_qubits'];raw=raw_check(text,data)
    if not raw['ok']: raise ValueError(raw)
    m,dets=model(text,data)
    result=dict(stem=str(stem),qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),data_qubits=data,
                raw=raw,record_contract=complete(m,dets),singles=singles(m))
    if add_missing:
        rows=result['record_contract']['missing']
        if any(row['reference'] for row in rows):
            result['completion_status']='Nonzero reference requires generalized evaluator'
        else:
            text+=''.join('// DETECTOR '+' '.join(f'c[{b}]' for b in row['bits'])+'\n' for row in rows)
            new=write_stem(text,data,output.parent/'candidates',stem.name+'_complete_records')
            result['completed_stem']=str(new);result['completed_raw']=raw_check(text,data)
            mm,_=model(text,data);result['completed_singles']=singles(mm)
            if exact: result['completed_exact']=price(new,processes=1)
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('stem');ap.add_argument('output')
    ap.add_argument('--add-missing',action='store_true');ap.add_argument('--exact',action='store_true');a=ap.parse_args()
    r=audit(a.stem,a.output,a.add_missing,a.exact)
    print(json.dumps({k:r[k] for k in ('stem','record_contract','singles')},indent=2))
