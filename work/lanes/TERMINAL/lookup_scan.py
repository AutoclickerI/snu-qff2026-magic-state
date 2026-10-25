"""Exact sparse-state single-Pauli audit of decomposed reversible lookups.

All syndrome inputs, every native gate's Paulis, all preparation flips and
every idle Pauli are scanned. No Monte Carlo and no atomic Toffoli assumption.
The output controls are computational-basis states; tracing them after their
transversal correction gives the probability-weighted Steane decoded loss.
"""
import json, math, cmath, hashlib
from pathlib import Path
H=Path(__file__).resolve().parent

def ccx(a,b,c):
    return [('h',c),('cx',b,c),('tdg',c),('cx',a,c),('t',c),('cx',b,c),('tdg',c),
            ('cx',a,c),('t',b),('t',c),('h',c),('cx',a,b),('t',a),('tdg',b),('cx',a,b)]

def rccx(a,b,c):
    return [('h',c),('t',c),('cx',b,c),('tdg',c),('cx',a,c),('t',c),('cx',b,c),('tdg',c),('h',c)]

def onehot(relative=False):
    # q0..2 = syndrome, q3..9 = one-hot labels 1..7.
    f=lambda i:i+2
    gate=rccx if relative else ccx
    ops=gate(0,1,f(3))+gate(0,2,f(5))+gate(1,2,f(6))+gate(f(3),2,f(7))
    for s,terms in [(1,[0,f(3),f(5),f(7)]),(2,[1,f(3),f(6),f(7)]),(4,[2,f(5),f(6),f(7)])]:
        ops += [('cx',q,f(s)) for q in terms]
    ops += [('cx',f(7),f(s)) for s in (3,5,6)]
    return ops

def duplicated_or():
    ops=[]
    for temp,out in ((3,4),(5,6)):
        for a,b,t in ((0,1,temp),(temp,2,out)):
            ops += [('x',a),('x',b)]+rccx(a,b,t)+[('x',a),('x',b),('x',t)]
    return ops

def apply(v,op):
    kind,*qs=op
    if kind in ('t','tdg'):
        phase=cmath.exp((1 if kind=='t' else -1)*1j*math.pi/4)
        bit=1<<qs[0];return {k:a*(phase if k&bit else 1) for k,a in v.items()}
    if kind=='h':
        bit=1<<qs[0];out={}
        for k,a in v.items():
            lo=k&~bit;hi=lo|bit
            out[lo]=out.get(lo,0)+a/math.sqrt(2)
            out[hi]=out.get(hi,0)+(-1 if k&bit else 1)*a/math.sqrt(2)
        return {k:a for k,a in out.items() if abs(a)>1e-13}
    if kind=='cx':
        c,t=map(lambda q:1<<q,qs);return {(k^t if k&c else k):a for k,a in v.items()}
    if kind in 'xyz':
        bit=1<<qs[0]
        return {(k^bit if kind in 'xy' else k):a*((-1 if k&bit else 1) if kind in 'yz' else 1) for k,a in v.items()}
    raise ValueError(op)

def schedule(ops,n):
    free=[0]*n;times=[]
    for op in ops:
        t=max(free[q] for q in op[1:]);times.append(t)
        for q in op[1:]:free[q]=t+1
    return times,max(free)

def syndrome(mask):
    s=0
    for i in range(7):
        if mask>>i&1:s^=i+1
    return s

def audit(name,ops,n,mode):
    times,depth=schedule(ops,n)
    # Schedule order is topological: operations sharing a wire retain their order.
    order=sorted(range(len(ops)),key=lambda i:(times[i],i))
    ordered=[ops[i] for i in order];ot=[times[i] for i in order]
    faults=[]
    for q in range(n):faults.append((-1,[('x',q)],1.,f'initial X q{q}'))
    for j,(i,op) in enumerate(zip(order,ordered)):
        if op[0]=='cx':
            for p in 'ixyz':
                for r in 'ixyz':
                    if p+r!='ii':faults.append((j,[(x,q) for x,q in zip((p,r),op[1:]) if x!='i'],1/15,f'gate#{i} {op} {p+r}'))
        else:
            for p in 'xyz':faults.append((j,[(p,op[1])],1/3,f'gate#{i} {op} {p}'))
    for t in range(depth):
        busy={q for op,tt in zip(ordered,ot) if tt==t for q in op[1:]}
        j=max((j for j,tt in enumerate(ot) if tt<=t),default=-1)
        for q in set(range(n))-busy:
            for p in 'xyz':faults.append((j,[(p,q)],1/3,f'idle tick{t} q{q} {p}'))
    rows=[];witnesses=[]
    for s in range(8):
        prefixes=[{s:1.+0j}]
        for op in ordered:prefixes.append(apply(prefixes[-1],op))
        ideal=prefixes[-1]
        if mode=='onehot':
            assert set(ideal)=={s|((1<<(s-1))<<3 if s else 0)},(s,ideal)
        else:
            assert all(((k>>4)&1)==((k>>6)&1)==bool(s) for k in ideal),(s,ideal)
        coeff=0.;bad=0;reject=0;by_type={'initial':0.,'gate':0.,'idle':0.}
        for j,paulis,w,label in faults:
            v=prefixes[j+1]
            for pauli in paulis:v=apply(v,pauli)
            for op in ordered[j+1:]:v=apply(v,op)
            loss=0.;acc=0.
            for k,a in v.items():
                p=abs(a)**2
                if mode=='onehot':
                    mask=(k>>3)^((1<<(s-1)) if s else 0)
                    loss+=p*((mask.bit_count()%2)^bool(syndrome(mask)))
                    acc+=p
                else:
                    # Perfect recorded input, final syndrome-memory comparisons,
                    # duplicated output comparison. Physical correction was earlier.
                    if (k&7)!=s or ((k>>4)^(k>>6))&1:continue
                    acc+=p;loss+=p*(((k>>4)&1)^bool(s))
            coeff+=w*loss
            by_type[label.split()[0].split('#')[0]]+=w*loss
            if acc<1-1e-9:reject+=1
            if loss>1e-9:
                bad+=1
                if s==0 and len(witnesses)<30:witnesses.append(dict(label=label,loss_Z=loss,loss_X=loss/2,weight=w,output={str(k):round(abs(a)**2,12) for k,a in v.items()}))
        rows.append(dict(syndrome=s,coefficient_Z=coeff,coefficient_X=coeff/2,coefficient_Z_by_type=by_type,harmful=bad,rejected=reject))
        print(name,s,rows[-1],flush=True)
    out=dict(name=name,n_qubits=n,native_depth=depth,native_gates=len(ops),cx=sum(op[0]=='cx' for op in ops),
             t=sum(op[0] in ('t','tdg') for op in ops),faults_per_syndrome=len(faults),total_fault_cases=len(faults)*8,
             input_rows=rows,witnesses_syndrome_zero=witnesses,
             caveat='lookup plus initialization and idles only; incoming input/reference is perfect; output CX and final readout noise not in this scan')
    (H/'logs'/f'{name}.scan.json').write_text(json.dumps(out,indent=2)+'\n')
    return out

if __name__=='__main__':
    audit('c_onehot',onehot(),10,'onehot')
    audit('c_onehot_rccx',onehot(True),10,'onehot')
    audit('d_or_duplicate',duplicated_or(),7,'or')
