"""Joint native preparation directly on the outer seven data cells."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,time
from pathlib import Path
from ortools.sat.python import cp_model
A=[1,14,8,9,2,16,15];D=[0,20,7,10,3,22,21];CELLS=A+D

def synth(depth=10,seconds=60,max_cx=26,seed=1):
    start=time.perf_counter();m=cp_model.CpModel();one=m.NewBoolVar('one');m.Add(one==1)
    old=json.loads(Path(__file__).with_name('linear_magic_d8_s1.json').read_text())
    init=dict(old['initial']);edges=[(u,v) for u in range(14) for v in range(14) if abs(CELLS[u]//6-CELLS[v]//6)+abs(CELLS[u]%6-CELLS[v]%6)==1]
    cols=[{(q,j):m.NewBoolVar(f'c0_{q}_{j}') for q in range(14) for j in range(4)}]
    for q in range(14):
        for j in range(4):m.Add(cols[0][q,j]==int(init.get(CELLS[q])==j))
    sels=[]
    for t in range(depth):
        sel={e:m.NewBoolVar(f's{t}_{e}') for e in edges};sels.append(sel)
        for q in range(14):m.AddAtMostOne(s for (u,v),s in sel.items() if q in (u,v))
        nxt={}
        for q in range(14):
            for j in range(4):
                terms=[]
                for (u,v),s in sel.items():
                    if v!=q:continue
                    z=m.NewBoolVar('and');m.AddMultiplicationEquality(z,[s,cols[t][u,j]]);terms.append(z)
                b=m.NewBoolVar(f'c{t+1}_{q}_{j}');m.AddBoolXOr([b,cols[t][q,j],*terms,one]);nxt[q,j]=b
        cols.append(nxt)
    basis={(j,k):m.NewBoolVar(f'basis{j}_{k}') for j in range(3) for k in range(3)};shift=[m.NewBoolVar(f'shift{k}') for k in range(3)]
    for q in range(14):
        if q<7:
            for j in range(4):m.Add(cols[-1][q,j]==0)
        else:
            label=q-6
            for j in range(3):m.AddBoolXOr([cols[-1][q,j],*[basis[j,k] for k in range(3) if label>>k&1],one])
            m.AddBoolXOr([cols[-1][q,3],*[shift[k] for k in range(3) if label>>k&1]])
    ncx=sum(v for sel in sels for v in sel.values());m.Add(ncx<=max_cx)
    m.Minimize(ncx*1000+sum(t*v for t,sel in enumerate(sels) for v in sel.values()))
    hint=[l['cx'] for l in old['layers'] if l['cx']]+[list(zip(A,D)),list(zip(D,A))]
    for t,sel in enumerate(sels):
        es=set(map(tuple,hint[t])) if t<len(hint) else set()
        for (u,v),b in sel.items():m.AddHint(b,int((CELLS[u],CELLS[v]) in es))
    s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=seconds;s.parameters.random_seed=seed;s.parameters.cp_model_presolve=False
    status=s.Solve(m);out=dict(kind='direct',depth=depth,status=s.StatusName(status),seconds=time.perf_counter()-start,seed=seed,cells=CELLS)
    if status not in (cp_model.FEASIBLE,cp_model.OPTIMAL):return out
    out.update(cx=int(s.Value(ncx)),initial=old['initial'],layers=[dict(cx=[(CELLS[u],CELLS[v]) for (u,v),b in sel.items() if s.Value(b)],rx=[]) for sel in sels],basis=[[int(s.Value(basis[j,k])) for k in range(3)] for j in range(3)],shift=[int(s.Value(b)) for b in shift])
    rows={q:0 for q in CELLS}
    for q,j in out['initial']:rows[q]=1<<j
    for l in out['layers']:
        for u,v in l['cx']:rows[v]^=rows[u]
    assert all(rows[q]==0 for q in A)
    for i,q in enumerate(D,1):
        expected=sum((sum(out['basis'][j][k] for k in range(3) if i>>k&1)%2)<<j for j in range(3))
        expected|=(1^(sum(out['shift'][k] for k in range(3) if i>>k&1)%2))<<3
        assert rows[q]==expected
    out['map_verified']=True;return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--depth',type=int,default=10);ap.add_argument('--seconds',type=float,default=60);ap.add_argument('--max-cx',type=int,default=26);ap.add_argument('--seed',type=int,default=1);a=ap.parse_args()
    r=synth(a.depth,a.seconds,a.max_cx,a.seed);Path(__file__).with_name(f'direct_d{a.depth}_s{a.seed}.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2),flush=True)
