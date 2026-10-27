"""Native GHZ cleanup with an early logical-X read and concurrent code prep."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,time
from pathlib import Path
from ortools.sat.python import cp_model
CELLS=[1,14,8,9,2,16,15]

def synth(depth=10,mid=4,seconds=60,seed=1,max_cx=20):
    st=time.perf_counter();m=cp_model.CpModel();one=m.NewBoolVar('one');m.Add(one==1)
    edges=[(u,v) for u in range(7) for v in range(7) if abs(CELLS[u]//6-CELLS[v]//6)+abs(CELLS[u]%6-CELLS[v]%6)==1]
    cols=[{(q,j):m.NewBoolVar(f'c0_{q}_{j}') for q in range(7) for j in range(4)}]
    for q in range(7):
        for j in range(4):m.Add(cols[0][q,j]==int(j==3))
    sels=[];injs=[];actions=[]
    for t in range(depth):
        sel={e:m.NewBoolVar(f'cx{t}_{e}') for e in edges};sels.append(sel)
        inj={(q,j):m.NewBoolVar(f'inj{t}_{q}_{j}') for q in range(7) for j in range(3)};injs.append(inj)
        act={}
        for q in range(7):
            aa=[s for (u,v),s in sel.items() if q in (u,v)]+[inj[q,j] for j in range(3)]
            m.AddAtMostOne(aa);act[q]=aa
        actions.append(act)
        nxt={}
        for q in range(7):
            ii=m.NewBoolVar('ii');m.Add(ii==sum(inj[q,j] for j in range(3)))
            if t==0:m.Add(ii==0)
            else:
                # One explicit Z measurement of the exposed zero immediately
                # precedes each new |+> variable. It must be a real idle slot.
                for j in range(4):m.Add(cols[t-1][q,j]==0).OnlyEnforceIf(ii)
                for a in actions[t-1][q]:m.Add(a==0).OnlyEnforceIf(ii)
            for j in range(4):
                m.Add(cols[t][q,j]==0).OnlyEnforceIf(ii)
                terms=[]
                for (u,v),s in sel.items():
                    if v!=q:continue
                    z=m.NewBoolVar('and');m.AddMultiplicationEquality(z,[s,cols[t][u,j]]);terms.append(z)
                b=m.NewBoolVar(f'c{t+1}_{q}_{j}');extra=[inj[q,j]] if j<3 else []
                m.AddBoolXOr([b,cols[t][q,j],*terms,*extra,one]);nxt[q,j]=b
        cols.append(nxt)
    for j in range(3):m.AddExactlyOne(inj[q,j] for inj in injs for q in range(7))
    m.Add(sum(cols[mid][q,3] for q in range(7))==1)
    for q in range(7):
        for a in actions[mid][q]:m.Add(a==0).OnlyEnforceIf(cols[mid][q,3])
    basis={(j,k):m.NewBoolVar(f'basis{j}_{k}') for j in range(4) for k in range(4)}
    for q in range(7):
        label=(q+1)|8
        for j in range(4):m.AddBoolXOr([cols[-1][q,j],*[basis[j,k] for k in range(4) if label>>k&1],one])
    ncx=sum(v for sel in sels for v in sel.values());m.Add(ncx<=max_cx)
    m.Minimize(1000*ncx+sum(t*v for t,sel in enumerate(sels) for v in sel.values()))
    s=cp_model.CpSolver();s.parameters.max_time_in_seconds=seconds;s.parameters.num_workers=1;s.parameters.random_seed=seed;s.parameters.cp_model_presolve=False
    status=s.Solve(m);out=dict(kind='hybrid',depth=depth,mid=mid,status=s.StatusName(status),seconds=time.perf_counter()-st,seed=seed)
    if status not in (cp_model.FEASIBLE,cp_model.OPTIMAL):return out
    root=next(CELLS[q] for q in range(7) if s.Value(cols[mid][q,3]))
    layers=[dict(cx=[(CELLS[u],CELLS[v]) for (u,v),b in sel.items() if s.Value(b)],rx=[(CELLS[q],j) for (q,j),b in inj.items() if s.Value(b)]) for sel,inj in zip(sels,injs)]
    out.update(cx=int(s.Value(ncx)),mx_root=root,layers=layers,basis=[[int(s.Value(basis[j,k])) for k in range(4)] for j in range(4)])
    rows={q:8 for q in CELLS};snap=[]
    for t,l in enumerate(layers):
        snap.append(rows.copy())
        if t==mid:assert [q for q in CELLS if rows[q]&8]==[root]
        for q,j in l['rx']:assert rows[q]==0 and snap[t-1][q]==0;rows[q]=1<<j
        for u,v in l['cx']:rows[v]^=rows[u]
    for i,q in enumerate(CELLS,1):
        label=i|8
        expected=sum((sum(out['basis'][j][k] for k in range(4) if label>>k&1)%2)<<j for j in range(4))
        assert rows[q]==expected
    out['map_verified']=True;return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--depth',type=int,default=10);ap.add_argument('--mid',type=int,default=4);ap.add_argument('--seconds',type=float,default=60);ap.add_argument('--seed',type=int,default=1);ap.add_argument('--max-cx',type=int,default=20);a=ap.parse_args()
    r=synth(a.depth,a.mid,a.seconds,a.seed,a.max_cx);Path(__file__).with_name(f'hybrid_d{a.depth}_m{a.mid}_s{a.seed}.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2),flush=True)
