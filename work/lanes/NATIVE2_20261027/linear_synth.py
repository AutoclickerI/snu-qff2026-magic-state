"""State-specific native encoding and coherent GHZ-to-Steane conversion.

The GHZ converter preserves its unknown logical qubit. New |+> variables may
be injected only into a wire proven identically zero by the current linear
map, so no existing coherence is discarded in the ideal circuit.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,time
from pathlib import Path
from ortools.sat.python import cp_model

CELLS=[1,14,8,9,2,16,15]

def synth(kind='magic',depth=7,seconds=60,max_cx=None,seed=1):
    start=time.perf_counter();m=cp_model.CpModel();one=m.NewBoolVar('one');m.Add(one==1)
    n=len(CELLS);edges=[(u,v) for u in range(n) for v in range(n) if abs(CELLS[u]//6-CELLS[v]//6)+abs(CELLS[u]%6-CELLS[v]%6)==1]
    initial={(q,j):m.NewBoolVar(f'initial{q}_{j}') for q in range(n) for j in range(4)}
    if kind=='magic':
        for j in range(4):m.AddExactlyOne(initial[q,j] for q in range(n))
        for q in range(n):m.AddAtMostOne(initial[q,j] for j in range(4))
    else:
        for q in range(n):
            for j in range(4):m.Add(initial[q,j]==int(j==3))
    col=[initial];selections=[];injections=[]
    for t in range(depth):
        sel={e:m.NewBoolVar(f'cx{t}_{e}') for e in edges};selections.append(sel)
        inj={(q,j):m.NewBoolVar(f'inj{t}_{q}_{j}') for q in range(n) for j in range(3)} if kind=='cat' else {}
        injections.append(inj)
        for q in range(n):
            actions=[s for (u,v),s in sel.items() if q in (u,v)]+[v for (u,j),v in inj.items() if q==u]
            m.AddAtMostOne(actions)
        nxt={}
        for q in range(n):
            anyinj=m.NewBoolVar(f'anyinj{t}_{q}')
            m.Add(anyinj==sum(v for (u,j),v in inj.items() if q==u))
            for j in range(4):
                m.Add(col[t][q,j]==0).OnlyEnforceIf(anyinj)
                terms=[]
                for u,v in edges:
                    if v!=q:continue
                    z=m.NewBoolVar('and');m.AddMultiplicationEquality(z,[sel[u,v],col[t][u,j]]);terms.append(z)
                b=m.NewBoolVar(f'col{t+1}_{q}_{j}')
                extra=[inj[q,j]] if (q,j) in inj else []
                m.AddBoolXOr([b,col[t][q,j],*terms,*extra,one]);nxt[q,j]=b
        col.append(nxt)
    if kind=='cat':
        for j in range(3):m.AddExactlyOne(inj[q,j] for inj in injections for q in range(n))
    # Stabilizer generator basis is free, but the old logical variable is kept
    # in the logical-one coset. Rank preservation forces the 3x3 basis invertible.
    basis={(j,k):m.NewBoolVar(f'basis{j}_{k}') for j in range(3) for k in range(3)}
    shift=[m.NewBoolVar(f'shift{k}') for k in range(3)]
    for q in range(n):
        label=q+1
        for j in range(3):m.AddBoolXOr([col[-1][q,j],*[basis[j,k] for k in range(3) if label>>k&1],one])
        m.AddBoolXOr([col[-1][q,3],*[shift[k] for k in range(3) if label>>k&1]])
    ncx=sum(v for sel in selections for v in sel.values())
    if max_cx is not None:m.Add(ncx<=max_cx)
    # Mild late-idle tie breaker; fidelity is evaluated on completed circuits.
    m.Minimize(1000*ncx+sum(t*v for t,sel in enumerate(selections) for v in sel.values()))
    solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=seconds;solver.parameters.num_workers=1;solver.parameters.random_seed=seed;solver.parameters.cp_model_presolve=False
    status=solver.Solve(m);out=dict(kind=kind,depth=depth,status=solver.StatusName(status),seconds=time.perf_counter()-start,cells=CELLS,seed=seed)
    if status not in (cp_model.FEASIBLE,cp_model.OPTIMAL):return out
    layers=[]
    for sel,inj in zip(selections,injections):
        layers.append(dict(cx=[(CELLS[u],CELLS[v]) for (u,v),b in sel.items() if solver.Value(b)],rx=[(CELLS[q],j) for (q,j),b in inj.items() if solver.Value(b)]))
    out.update(cx=int(solver.Value(ncx)),layers=layers,initial=[(CELLS[q],j) for (q,j),b in initial.items() if solver.Value(b)],basis=[[int(solver.Value(basis[j,k])) for k in range(3)] for j in range(3)],shift=[int(solver.Value(b)) for b in shift])
    # Independently verify the exact binary map and every coherent injection.
    rows={q:0 for q in CELLS}
    for q,j in out['initial']:rows[q]|=1<<j
    for layer in layers:
        for q,j in layer['rx']:
            assert rows[q]==0;rows[q]=1<<j
        for u,v in layer['cx']:rows[v]^=rows[u]
    expected=[]
    for q in range(n):
        label=q+1;bits=sum((sum(out['basis'][j][k] for k in range(3) if label>>k&1)%2)<<j for j in range(3))
        bits|=(1^(sum(out['shift'][k] for k in range(3) if label>>k&1)%2))<<3;expected.append(bits)
    assert [rows[q] for q in CELLS]==expected
    out['map_verified']=True;return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--kind',choices=['magic','cat'],default='magic');ap.add_argument('--depth',type=int,default=7);ap.add_argument('--seconds',type=float,default=60);ap.add_argument('--max-cx',type=int);ap.add_argument('--seed',type=int,default=1);args=ap.parse_args()
    out=synth(args.kind,args.depth,args.seconds,args.max_cx,args.seed)
    p=Path(__file__).with_name(f'linear_{args.kind}_d{args.depth}_s{args.seed}.json');p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2),flush=True)

if __name__=='__main__':main()
