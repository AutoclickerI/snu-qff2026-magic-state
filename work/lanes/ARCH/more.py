"""Additional tested mechanisms: partial order, parallel hybrids, Knill, extra records."""
import sys
import json
import itertools
from pathlib import Path
from build import *

def mixed(mask):
    c=Circuit(); rev=[bool(mask>>i&1) for i in range(7)]
    c.prep(A,True,32); c.prep(B,False,31); c.prep(C,False,31)
    bits={}
    for i in range(7):
        a=34 if rev[i] else 33; b=33 if rev[i] else 34
        c.cx(a,D[i],A[i]); c.cx(b,B[i],D[i]); c.cx(b-1,B[i],C[i])
        bits['a',i]=c.read(a+1,A[i]); bits['b',i]=c.read(b+1,B[i],'X')
        bits['c',i]=c.read(b,C[i])
    for k in 'abc':
        for S in GENS+([list(range(7))] if k=='c' else []):
            c.dets.append(' '.join(f'c[{bits[k,i]}]' for i in S))
    return c.save(f'mix{mask:03d}',dict(mask=mask))

def hybrid_parallel(typ,perms):
    c=Circuit(); checks=C[:3]; flags=C[3:6]
    if typ=='Z':
        # All three six-CX flag gadgets overlap in six time steps.
        start=33
        c.prep(A,False,37); c.prep(B,False,37)
        for i in range(7): c.cx(38,A[i],B[i]); c.cx(39,A[i],D[i])
        c.readblock(39,B,'Z',True); c.readblock(40,A,'X')
    else:
        c.prep(A,True,32)
        for i in range(7): c.cx(33,D[i],A[i])
        c.readblock(34,A,'Z'); start=34
    slots=(0,2,3,5)
    for k,S in enumerate(perms):
        q,f=checks[k],flags[k]; plus=typ=='X'
        c.add(start-1,f'reset q[{q}];','prep'); c.add(start-1,f'reset q[{f}];','prep')
        c.add(start-1,f'h q[{q if plus else f}];','prep')
        for t,i in zip(slots,S): c.cx(start+t,q,D[i]) if plus else c.cx(start+t,D[i],q)
        for t in (1,4): c.cx(start+t,q,f) if plus else c.cx(start+t,f,q)
        x=c.read(start+6,q,'X' if plus else 'Z'); y=c.read(start+5,f,'Z' if plus else 'X')
        c.dets.extend([f'c[{x}]',f'c[{y}]'])
    return c

def permutations():
    for ps in itertools.product(*(list(itertools.permutations(S)) for S in GENS)):
        if all(len({p[k] for p in ps})==3 for k in range(4)): yield ps

def knill():
    c=Circuit()
    c.prep(A,True,23); c.prep(C,True,23)
    for i in range(7): c.cx(24,C[i],A[i],'prep')
    # Resource verification belongs to prep in this ablation.
    old=len(c.ops); c.readblock(25,C,'X',True)
    c.ops=[(t,s,'prep' if j>=old else r) for j,(t,s,r) in enumerate(c.ops)]
    c.prep(B,False,29); c.prep(C,False,29)
    for i in range(7): c.cx(30,B[i],C[i],'prep')
    old=len(c.ops); c.readblock(31,C,'Z',True)
    c.ops=[(t,s,'prep' if j>=old else r) for j,(t,s,r) in enumerate(c.ops)]
    for i in range(7): c.cx(32,A[i],B[i]); c.cx(33,D[i],B[i])
    db=c.readblock(34,D,'X'); bb=c.readblock(34,B,'Z')
    meta=c.save('knill',dict(data_qubits=A,round_start=32))
    p=HERE/'knill.qasm'
    p.write_text(p.read_text()+'// FRAME_X(0) '+' '.join(f'c[{b}]' for b in bb)+'\n// FRAME_Z(0) '+' '.join(f'c[{b}]' for b in db)+'\n')
    return meta

def ancilla_cross(direction):
    c=Circuit(); c.prep(A,True,32); c.prep(B,False,32); c.prep(C,False,32)
    for i in range(7):
        c.cx(33,D[i],A[i]); c.cx(33,B[i],C[i]); c.cx(34,B[i],D[i])
        c.cx(34,C[i],A[i]) if direction=='CA' else c.cx(34,A[i],C[i])
    ab=c.readblock(35,A,'Z'); cb=c.readblock(35,C,'Z',direction=='CA'); c.readblock(35,B,'X')
    # AC makes C logical Z = A logical Z; their XOR is deterministic.
    if direction=='AC': c.dets.append(' '.join(f'c[{b}]' for b in ab+cb))
    return c.save('cross'+direction)

def dummy_checked():
    c=Circuit(); c.prep(A,True,32); c.prep(B,False,31); c.prep(C,False,31)
    # Seven product zero controls in released pre-stage cells, reset33, verify
    # into C34 after C's original measurement33, final dummy CX35.
    # B->C must occur32, one step earlier than standard.
    P=[1,2,6,9,10,13,14]
    for i in range(7):
        c.cx(33,D[i],A[i]); c.cx(32,B[i],C[i]); c.cx(34,B[i],D[i])
    c.readblock(34,A,'Z'); c.readblock(33,C,'Z',True); c.readblock(35,B,'X')
    # C is now a random stabilizer codeword, so checking P with C gives a
    # correlated detector using both C readouts (no physical correction).
    for i,q in enumerate(P): c.add(33,f'reset q[{q}];','prep')
    # C's second read XOR first is the verifier; both readings have noise.
    first=list(range(21,28))  # A readblock allocated14..20; C21..27
    for i,q in enumerate(P):
        c.cx(34,q,C[i]); second=c.read(35,C[i]); c.dets.append(f'c[{first[i]}] c[{second}]')
        c.cx(35,q,D[i])
    return c.save('dummy_checked')

def postselect(source,block):
    p=HERE/(source+'.qasm'); name='post_'+block
    text=p.read_text()
    # base reads A14..20, C21..27, B28..34 (build.standard order).
    bs=list(range(14,21)) if block=='A' else list(range(28,35))
    text+='// POSTSELECT(0) '+' '.join(f'c[{b}]' for b in bs)+'\n'
    (HERE/(name+'.qasm')).write_text(text)
    meta=json.loads((HERE/(source+'.json')).read_text()); meta.update(name=name,postselection=block)
    (HERE/(name+'.json')).write_text(json.dumps(meta,indent=2)+'\n'); return meta

if __name__=='__main__':
    rows=[knill(),ancilla_cross('AC'),ancilla_cross('CA'),dummy_checked(),postselect('base','A'),postselect('base','B')]
    ps=list(permutations())
    # Exhaustion over flag data orders is handled by the analytic screen; these
    # representatives also cover both asymmetries with complete noisy gadgets.
    (HERE/'flag_permutations.json').write_text(json.dumps(ps))
    for typ in 'XZ':
        for k,ix in enumerate(sorted(set([0,len(ps)//4,len(ps)//2,3*len(ps)//4,len(ps)-1]))):
            rows.append(hybrid_parallel(typ,ps[ix]).save(f'hybridP{typ}{k}',dict(flag_orders=ps[ix])))
    rows += [mixed(m) for m in range(128)]
    (HERE/'more_manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
