"""Route the small CSS encoders backwards from fixed square-round cells.

The initial assignment is free: reverse SABRE's output, prepare its resulting
input permutation, and ASAP schedule against the retained prefix releases.
All routing SWAPs become three legal CXs. Empty routing wires are reset and
measured as zero checks. No noiseless regions are used in the resulting build.
"""
import os
os.environ['RAYON_NUM_THREADS']='1'
os.environ['QISKIT_NUM_PROCS']='1'
import sys,json,copy
from pathlib import Path
from qiskit import QuantumCircuit
from qiskit.transpiler import CouplingMap,PassManager
from qiskit.transpiler.passes import SabreSwap
from build_rounds import ENC,PIV,GENS,H
import build_suffix as S

def nb(a,b):return abs(a//6-b//6)+abs(a%6-b%6)==1

def build(seed,eraser=False,compact=False,fenced=False):
    lay=json.loads((H/('layout_compact.json' if compact else 'layout_joint.json')).read_text())
    D,A,B,C=[lay[k] for k in ('D','A','B','C')]
    c=S.prefix();release=S.release.copy()
    for i,path in lay['paths'].items():
        t=44
        for a,b in zip(path,path[1:]):
            t=max(t,release[b]+1)
            c.reset(t-1,b);c.cx(t,a,b);c.cx(t+1,b,a)
            c.dets.append([c.read(t+2,a)]);release[a]=t+3;t+=2
    sites=[q for q in range(36) if q not in D]
    edges=[(i,j) for i,a in enumerate(sites) for j,b in enumerate(sites) if nb(a,b)]
    helpers=[q for q in sites if q not in A+B+C]
    # A short logical-Z representative of B. Choose its readout helper by
    # shortest-distance cost on the actual non-data routing graph.
    from collections import deque
    distance={}
    for q in sites:
        ds={q:0};todo=deque([q])
        while todo:
            a=todo.popleft()
            for b in sites:
                if nb(a,b) and b not in ds:ds[b]=ds[a]+1;todo.append(b)
        distance[q]=ds
    logical=[s for s in __import__('itertools').combinations(range(7),3) if all(len(set(s)&g)%2==0 for g in GENS)]
    _,flag,support=min((sum(distance[B[i]][f] for i in s),f,s) for f in helpers for s in logical)
    forward=[]
    for layer in ENC:
        for block,plus in ((A,not eraser),(B,False),(C,True)):
            forward += [(block[b],block[a]) if plus else (block[a],block[b]) for a,b in layer]
    forward += [(B[i],flag) for i in support]
    inv=QuantumCircuit(len(sites))
    for j,(a,b) in enumerate(reversed(forward)):
        if fenced and j==3:inv.barrier(*[sites.index(q) for q in B+[flag]])
        inv.cx(sites.index(a),sites.index(b))
    routed=PassManager(SabreSwap(CouplingMap(edges),heuristic='decay',seed=seed,trials=1)).run(inv)
    labels=list(sites);inverse=[];swaps=0
    for ins in routed.data:
        if ins.operation.name=='barrier':
            inverse.append(dict(barrier=[sites[routed.find_bit(q).index] for q in ins.qubits]));continue
        a,b=[sites[routed.find_bit(q).index] for q in ins.qubits]
        if ins.operation.name=='swap':
            ia,ib=sites.index(a),sites.index(b);labels[ia],labels[ib]=labels[ib],labels[ia]
            inverse += [(a,b),(b,a),(a,b)];swaps+=1
        else:
            assert ins.operation.name=='cx';inverse.append((a,b))
    # labels[physical index] names the un-routed input wire at that location.
    pluslabels=set()
    for block,plus in ((A,not eraser),(B,False),(C,True)):
        pluslabels.update(block[i] for i in range(7) if (i not in PIV if plus else i in PIV))
    plus={q for q,label in zip(sites,labels) if label in pluslabels}
    end={q:release[q]+1 for q in sites};first={};last={};scheduled=[]
    for op in reversed(inverse):
        if isinstance(op,dict):
            t=max(end[q] for q in op['barrier'])
            for q in op['barrier']:end[q]=t
            continue
        a,b=op
        t=max(end[a],end[b]);c.cx(t,a,b);scheduled.append((t,a,b))
        for q in (a,b):first.setdefault(q,t);last[q]=t;end[q]=t+1
    for q,t in first.items():c.reset(t-1,q,q in plus)
    for q in A+B+C:
        if q not in first:
            c.reset(release[q],q,q in plus);end[q]=release[q]+1
    R=max(max(end[q] for q in A+B+C),max(lay['arrival'].values()))
    # The verification flag is read strictly before the round. All other
    # routing helpers return to zero and are checked at their final use.
    R=max(R,last.get(flag,release[flag])+2)
    for q in helpers:
        if q in last:c.dets.append([c.read(last[q]+1,q)])
    for d,a,b,cc in zip(D,A,B,C):
        c.cx(R,d,a);c.cx(R,b,cc);c.cx(R+1,b,d);c.cx(R+1,cc,a)
    c.readblock(R+2,A);c.readblock(R+2,B,True)
    cb=c.readblock(R+2,C,True,not eraser)
    if eraser:c.frames=['// FRAME_Z(0) '+' '.join(f'c[{b}]' for b in cb)]
    name=f'grid_{"compact" if compact else "eraser" if eraser else "square"}{"_fenced" if fenced else ""}_s{seed}'
    c.save(name,roles=dict(D=D,A=A,B=B,C=C),round_start=R,grid_free_override=False,
        change='square layout; backwards-routed CSS preparations, B logical-Z check, all waits',
        swaps=swaps,prep_cx=sum(not isinstance(o,dict) for o in inverse),seed=seed,logical_z_verification=list(support),flag=flag,
        preparation_ops=scheduled,preparation_sequence=list(reversed(inverse)),initial_plus=sorted(plus),initial_mapping=labels,fenced=fenced)
    p=H/'builds'/f'{name}.json';md=json.loads(p.read_text());md['data_qubits']=D;md['grid_free']=False;md.pop('grid_free_override');p.write_text(json.dumps(md,indent=2)+'\n')
    oo,_=S.parse_current(p.with_suffix('.qasm').read_text());used=set()
    for o in oo:
        keys={(o.time,q) for q in o.qs};assert not used&keys,(name,o,used&keys);used|=keys
        if o.kind=='CX':assert nb(*o.qs)
    return dict(name=name,R=R,prep_cx=len(inverse),swaps=swaps)

if __name__=='__main__':
    rows=[build(seed,eraser='eraser' in sys.argv,compact='compact' in sys.argv,fenced='fenced' in sys.argv) for seed in range(int(sys.argv[1]) if len(sys.argv)>1 else 32)]
    rows.sort(key=lambda r:(r['R'],r['prep_cx']))
    (H/('fenced_manifest.json' if 'fenced' in sys.argv else 'compact_manifest.json' if 'compact' in sys.argv else 'route_manifest.json')).write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps(rows[:10]),flush=True)
