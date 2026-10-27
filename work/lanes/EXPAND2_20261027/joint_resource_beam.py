"""Native backward arithmetic for the corrected six-square resource.

The initial product-state basis is free. Optional first-order constraints use
the exact terminal CSS fault signatures, not a gate-count proxy. A returned
network is a standalone resource witness; prefix scheduling and complete noisy
pricing remain necessary before it can be a complete candidate.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse,heapq,json,random,sys,time
from pathlib import Path
import stim
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/lanes/END2_20261027'))
import partial_contract as pc


def safe(sig):
    return bool(sig>>4) or (sig&15) in (0,9,10,11,12,13,14,15)


def nullspace(rows,n):
    piv={}
    for v in rows:
        while v:
            h=v.bit_length()-1
            if h not in piv:piv[h]=v;break
            v^=piv[h]
    for h in sorted(piv):
        for k in piv:
            if k!=h and piv[k]>>h&1:piv[k]^=piv[h]
    ans=[]
    for j in range(n):
        if j in piv:continue
        w=1<<j
        for h,v in piv.items():
            if v>>j&1:w|=1<<h
        ans.append(w)
    return ans


def finish(cells,state,path,seed,f1,elapsed,late_plus=()):
    rows,xs,zs=state
    sim=stim.TableauSimulator();sim.set_num_qubits(36)
    plus=[q for q,v in zip(cells,rows) if v]
    for q in plus:sim.h(q)
    gates=[(cells[a],cells[b]) for a,b in reversed(path)]
    last={q:-1 for q in cells};layers=[]
    for a,b in gates:
        t=max(last[a],last[b])+1
        while len(layers)<=t:layers.append([])
        layers[t].append([a,b]);last[a]=last[b]=t
        sim.cx(a,b)
    for q in late_plus:
        sim.reset(q);sim.h(q)
    checks=[]
    target_rows=getattr(pc,'FULL_ROWS',pc.ROWS) if late_plus else pc.ROWS
    for support in target_rows:
        p=stim.PauliString(36)
        for q in support:p[q]='X'
        checks.append(sim.peek_observable_expectation(p))
    rmask=[sum(1<<cells.index(q) for q in support) for support in target_rows]
    for mask in nullspace(rmask,len(cells)):
        p=stim.PauliString(36)
        for i,q in enumerate(cells):
            if mask>>i&1:p[q]='Z'
        checks.append(sim.peek_observable_expectation(p))
    assert len(checks)==len(cells) and set(checks)=={1},checks
    out=dict(seed=seed,first_order_constraints=f1,cells=cells,initial_rows=list(rows),
             initial_plus_qubits=plus,layers=layers,cx=len(gates),depth=len(layers),
             backward_path=[[cells[a],cells[b]] for a,b in path],
             late_plus_qubits=list(late_plus),
             stabilizers_verified=len(checks),seconds=elapsed,
             scope='Standalone native resource preparation; no prefix or noisy-score claim.')
    folder=HERE/'joint_resource';folder.mkdir(exist_ok=True)
    name=f'beam_h{len(cells)-21}_f{int(f1)}_s{seed}'
    (folder/(name+'.json')).write_text(json.dumps(out,indent=2)+'\n')
    print('FOUND',json.dumps(out),flush=True)
    return out


def run(seed=0,beam=800,depth=100,helpers=False,f1=True):
    start=time.perf_counter();rng=random.Random(seed)
    cells=sorted(pc.CELLS+(pc.HELPERS if helpers else []))
    edges=[(i,j) for i,a in enumerate(cells) for j,b in enumerate(cells)
           if abs(a//6-b//6)+abs(a%6-b%6)==1]
    rows=tuple(pc.COLS[q] for q in cells)
    xs=tuple(pc.fault_signature(q,'X',pc.HELPERS if helpers else []) for q in cells)
    zs=tuple(pc.fault_signature(q,'Z',pc.HELPERS if helpers else []) for q in cells)
    assert all(map(safe,xs+zs))
    # Changing the 11-dimensional coordinate basis leaves the target state
    # unchanged and diversifies the arithmetic heuristic without changing it.
    weights=list(range(11))
    rng.shuffle(weights)
    def pop(v):
        return sum((1.+weights[k]/22) for k in range(11) if v>>k&1)
    pops=[pop(v) for v in range(2048)]
    state=(rows,xs,zs);front=[(state,[],0.)];seen={state:0}
    best_nz=len(cells)
    for d in range(1,depth+1):
        candidates=[]
        for (rows,xs,zs),path,exposure in front:
            for a,b in edges:
                if not rows[a]:continue
                xx=xs[a]^xs[b];zz=zs[a]^zs[b]
                if f1 and (not safe(xx) or not safe(zz)):continue
                nr=list(rows);nr[b]^=nr[a];nr=tuple(nr)
                nx=list(xs);nx[a]=xx;nx=tuple(nx)
                nzs=list(zs);nzs[b]=zz;nzs=tuple(nzs)
                nxt=(nr,nx,nzs)
                if seen.get(nxt,999)<=d:continue
                seen[nxt]=d
                nz=sum(v!=0 for v in nr);pp=path+[(a,b)]
                if nz==11:return finish(cells,nxt,pp,seed,f1,time.perf_counter()-start)
                eq=sum(nr[i]!=0 and nr[i]==nr[j] for i,j in edges)//2
                risky=sum((s&15)!=0 and s>>4==0 for s in nx+nzs)
                ep=exposure+risky
                score=(nz-11)*6+sum(pops[v] for v in nr)*.23-eq*.9+ep*.0003+rng.random()*2.2
                candidates.append((score,nxt,pp,ep))
        if not candidates:
            print('NO_FRONT',d,flush=True);return None
        front=[(s,p,e) for _,s,p,e in heapq.nsmallest(beam,candidates,key=lambda r:r[0])]
        best_nz=min(best_nz,min(sum(v!=0 for v in s[0]) for s,_,_ in front))
        if d%5==0:print('depth',d,'best_nonzero',best_nz,'top_nonzero',sum(v!=0 for v in front[0][0][0]),'seen',len(seen),flush=True)
        if len(seen)>500000:seen={s:d for s,_,_ in front}
    print('EXHAUSTED',seed,best_nz,time.perf_counter()-start,flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--seed',type=int,default=0)
    ap.add_argument('--beam',type=int,default=800);ap.add_argument('--depth',type=int,default=100)
    ap.add_argument('--helpers',action='store_true');ap.add_argument('--no-f1',action='store_true')
    a=ap.parse_args();run(a.seed,a.beam,a.depth,a.helpers,not a.no_f1)
