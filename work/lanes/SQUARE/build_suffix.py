"""Grid-free comparison retaining v37a's data prefix and its measured checks.

Extract the backwards causal cone of output data just before the first round
interaction plus all completed, deterministic prefix detectors. All reset
boundaries and barriers remain explicit. Replace the entire ancilla suffix.
"""
import sys,json,re,copy
from pathlib import Path
from build_rounds import Circuit,GENS,ENC,PIV,H
sys.path.insert(0,str(H/'sparse'))
from frontend import parse_current

BASE=H/'builds/v37a'
text=BASE.with_suffix('.qasm').read_text()
meta=json.loads(BASE.with_suffix('.json').read_text())
D=meta['data_qubits']
ops,dets=parse_current(text)
measure={o.bit:o for o in ops if o.bit is not None}
prefix_dets=[d for d in dets if max(measure[b].time for b in d)<44]
targetbits=set().union(*prefix_dets)
live=set(D); kept=[]
for o in reversed(ops):
    if o.time>=44:continue
    needed=o.bit in targetbits or bool(set(o.qs)&live)
    if needed:
        kept.append(o)
        if o.kind in ('R','RX'):live.difference_update(o.qs)
        else:live.update(o.qs)
kept.reverse()
release={q:max((o.time for o in kept if q in o.qs),default=-1)+1 for q in range(36)}
available=sorted((q for q in range(36) if q not in D),key=lambda q:(release[q],q))[:21]
# Give B the earliest released cells; A and C can reset at 40 for R44.
B,A,C=[available[j:j+7] for j in (0,7,14)]
assert max(release[q] for q in available)<=40,release

def prefix():
    c=Circuit();c.bit=max(measure)+1;c.dets=[sorted(d) for d in prefix_dets]
    for o in kept:
        if o.kind=='CX':c.cx(o.time,*o.qs)
        elif o.kind in ('R','RX'):c.reset(o.time,o.qs[0],o.kind=='RX')
        elif o.kind in ('M','MX'):
            if o.kind=='MX':c.add(o.time,f'h q[{o.qs[0]}];')
            c.add(o.time,f'measure q[{o.qs[0]}] -> c[{o.bit}];')
            if o.kind=='MX':c.add(o.time,f'h q[{o.qs[0]}];')
        else:c.add(o.time,f'{o.kind.lower()} q[{o.qs[0]}];')
    return c

def build(kind,R=44,verification=(0,1,2)):
    c=prefix()
    c.prep(A,R-4,kind!='eraser')
    c.prep(C,R-4,kind!='standard')
    if kind=='standard':c.prep(B,R-4,False)
    else:
        c.prep(B,R-7,False)
        helper=next(q for q in range(36) if q not in D+A+B+C and release[q]<=R-4)
        c.reset(R-4,helper)
        for j,i in enumerate(verification):c.cx(R-3+j,B[i],helper)
        c.dets.append([c.read(R,helper)])
    for d,a,b,cc in zip(D,A,B,C):
        c.cx(R,d,a);c.cx(R,b,cc);c.cx(R+1,b,d)
        if kind!='standard':c.cx(R+1,cc,a)
    c.readblock(R+1 if kind=='standard' else R+2,A)
    c.readblock(R+2,B,True)
    cb=c.readblock(R+1 if kind=='standard' else R+2,C,kind!='standard',kind!='eraser')
    if kind=='eraser':c.frames=['// FRAME_Z(0) '+' '.join(f'c[{b}]' for b in cb)]
    # Validate simultaneous use, after native-X folding, with the common parser.
    name=f'suffix_{kind}_R{R}'
    c.save(name,data_qubits_override=D,round_start=R,change=f'v37a causal prefix + grid-free {kind} suffix',
        roles=dict(D=D,A=A,B=B,C=C),release=release,logical_z_verification=list(verification) if kind!='standard' else None)
    p=H/'builds'/f'{name}.json';m=json.loads(p.read_text());m['data_qubits']=D;m.pop('data_qubits_override');p.write_text(json.dumps(m,indent=2)+'\n')
    oo,_=parse_current(p.with_suffix('.qasm').read_text());used=set()
    for o in oo:
        keys={(o.time,q) for q in o.qs}
        assert not used&keys,(name,o,used&keys)
        used|=keys
    return name

def counterfactuals():
    # Same saved QASM with explicit noise selectors; the hash-keyed results
    # ledger stores multiple experiments for a circuit instead of overwriting.
    p=H/'builds/v37a_round.qasm';p.write_text(text)
    units=[[o.time,list(o.qs)] for o in ops if o.time>=46 or o.time==45 and tuple(o.qs) in ((6,7),(2,8))]
    p.with_suffix('.json').write_text(json.dumps(dict(meta,noise_start=45,noisy_units=units,
        change='v37a round only: preparations perfect, early D->A at45; all waits from45 retained'),indent=2)+'\n')

if __name__=='__main__':
    counterfactuals()
    for kind in ('standard','square','eraser'):print(build(kind))
    (H/'prefix.json').write_text(json.dumps(dict(data_qubits=D,roles=dict(A=A,B=B,C=C),release=release,
        kept_operations=[dict(kind=o.kind,qs=o.qs,time=o.time,bit=o.bit) for o in kept],detectors=[sorted(d) for d in prefix_dets]),indent=2)+'\n')
