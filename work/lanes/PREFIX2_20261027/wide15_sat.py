"""Joint 15-cell native encoder / one-layer T block / flagged decoder synthesis.

Five free product-plus inputs are encoded into all15 affine phase forms at once.
The decoder restores seven zero cells and one plus flag beside the Steane data.
Every row and every selected-CX-supported Z hook avoids logicalZ. Decoder X hooks
are constrained independently by their final syndrome and restored-zero record
signatures. Final candidates are still screened against the complete noisy model.
"""
import os,sys,json,time,argparse
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
from ortools.sat.python import cp_model
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'PREFIX20261027'));sys.path.insert(0,str(H.parent/'T14'))
from search_phase import singles
import synth
from qcirc import adjacent,save
from qtools import price
from qtools.validity import raw_check
A=synth.A;D=synth.D
CELLS=[1,2,3,4,5,7,8,9,10,11,13,14,15,16,17]
EDGES=[(a,b) for a in range(15) for b in range(15) if adjacent(CELLS[a],CELLS[b])]
TARGET=synth.goals(24)
FINAL=[9+A.index(q) if q in A else 16 if q==3 else 0 for q in CELLS]
ZEROS=[q for q in CELLS if q not in A+[3]]

def solve(pre=10,post=10,seconds=120,seed=0,max_cx=76,xhooks=True):
    started=time.time();m=cp_model.CpModel();one=m.NewConstant(1);depth=pre+post
    rows=[[[m.NewBoolVar(f'r{t}_{q}_{j}') for j in range(5)] for q in range(15)] for t in range(depth+1)]
    vals=[]
    for t in range(depth+1):
        vv=[]
        for q in range(15):
            domain=TARGET if t==pre else [0]+TARGET if t==0 else [x for x in range(32) if x!=8]
            v=m.NewIntVarFromDomain(cp_model.Domain.FromValues(domain),f'v{t}_{q}')
            m.Add(v==sum((1<<j)*rows[t][q][j] for j in range(5)));vv.append(v)
        vals.append(vv)
    m.AddAllDifferent(vals[pre])
    nz=[]
    for q in range(15):
        b=m.NewBoolVar(f'nz{q}');m.Add(vals[0][q]>0).OnlyEnforceIf(b);m.Add(vals[0][q]==0).OnlyEnforceIf(b.Not());nz.append(b)
        m.Add(vals[-1][q]==FINAL[q])
    m.Add(sum(nz)==5)
    sels=[]
    for t in range(depth):
        ss={e:m.NewBoolVar(f'cx{t}_{e[0]}_{e[1]}') for e in EDGES};sels.append(ss)
        for q in range(15):m.AddAtMostOne(b for (a,c),b in ss.items() if q in (a,c))
        for q in range(15):
            for j in range(5):
                terms=[]
                for (a,b),g in ss.items():
                    if b!=q:continue
                    z=m.NewBoolVar('and');m.AddMultiplicationEquality(z,[g,rows[t][a][j]]);terms.append(z)
                m.AddBoolXOr([rows[t+1][q][j],rows[t][q][j],*terms,one])
    if xhooks:
        # Signatures at the output: three Steane X-error syndrome bits, odd
        # logical-X parity, and one bit per restored-zero measurement.
        sig=[]
        for q in CELLS:
            sig.append((A.index(q)+1)|8 if q in A else 0 if q==3 else 1<<(4+ZEROS.index(q)))
        nx=4+len(ZEROS)
        xs=[[[m.NewBoolVar(f'x{t}_{q}_{j}') for j in range(nx)] for q in range(15)] for t in range(post+1)]
        for q in range(15):
            for j in range(nx):m.Add(xs[-1][q][j]==((sig[q]>>j)&1))
        for t in range(post+1):
            for q in range(15):
                v=m.NewIntVar(0,(1<<nx)-1,'xval');m.Add(v==sum((1<<j)*xs[t][q][j] for j in range(nx)));m.Add(v!=8)
        for t in range(post):
            ss=sels[pre+t]
            for q in range(15):
                for j in range(nx):
                    terms=[]
                    for (a,b),g in ss.items():
                        if a!=q:continue
                        z=m.NewBoolVar('andx');m.AddMultiplicationEquality(z,[g,xs[t+1][b][j]]);terms.append(z)
                    m.AddBoolXOr([xs[t][q][j],xs[t+1][q][j],*terms,one])
    ncx=sum(g for ss in sels for g in ss.values());m.Add(ncx<=max_cx)
    m.Minimize(ncx*100+sum(t*g for t,ss in enumerate(sels) for g in ss.values()))
    solver=cp_model.CpSolver();solver.parameters.num_search_workers=1
    solver.parameters.max_time_in_seconds=seconds;solver.parameters.random_seed=seed
    solver.parameters.cp_model_presolve=False;solver.parameters.log_search_progress=False
    status=solver.Solve(m)
    out=dict(pre=pre,post=post,seed=seed,xhook_constraints=xhooks,max_cx=max_cx,
             status=solver.StatusName(status),seconds=time.time()-started,
             conflicts=solver.NumConflicts(),branches=solver.NumBranches())
    if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE):return out
    out.update(cx=int(solver.Value(ncx)),initial=[solver.Value(v) for v in vals[0]],
               phase=[solver.Value(v) for v in vals[pre]],
               layers=[[[a,b] for (a,b),g in ss.items() if solver.Value(g)] for ss in sels])
    replay=list(out['initial'])
    assert sum(v!=0 for v in replay)==5
    for t,layer in enumerate(out['layers']):
        for a,b in layer:replay[b]^=replay[a]
        if t+1==pre:assert sorted(replay)==sorted(TARGET)
    assert replay==FINAL
    return out

def build(rec,name,early_heralds=False,early_transfers=False):
    pre=[x for x in rec['layers'][:rec['pre']] if x]
    post=[x for x in rec['layers'][rec['pre']:] if x]
    units=[];first={q:999 for q in CELLS};t=1
    for layer in pre:
        for a,b in layer:
            qs=(CELLS[a],CELLS[b]);units.append(dict(k='CX',q=qs,t=t,b=None))
            for q in qs:first[q]=min(first[q],t)
        t+=1
    for q in CELLS:units.append(dict(k='TDG',q=(q,),t=t,b=None));first[q]=min(first[q],t)
    for q,row in zip(CELLS,rec['initial']):units.append(dict(k='RX' if row else 'R',q=(q,),t=first[q]-1,b=None))
    t+=1
    for layer in post:
        for a,b in layer:units.append(dict(k='CX',q=(CELLS[a],CELLS[b]),t=t,b=None))
        t+=1
    flagt=t
    last={q:max(u['t'] for u in units if q in u['q']) for q in CELLS}
    readtimes={q:(last[q]+1 if early_heralds else flagt) for q in ZEROS+[3]}
    units.append(dict(k='MX',q=(3,),t=readtimes[3],b=500));dets=[[500]]
    for j,q in enumerate(ZEROS):units.append(dict(k='M',q=(q,),t=readtimes[q],b=600+j));dets.append([600+j])
    h=flagt+1
    transfer_end={}
    for a,d in zip(A,D):
        copy=max(last[a]+1,readtimes.get(d,-2)+2) if early_transfers else h+1
        units.append(dict(k='R',q=(d,),t=copy-1,b=None))
        units.append(dict(k='CX',q=(a,d),t=copy,b=None));units.append(dict(k='CX',q=(d,a),t=copy+1,b=None))
        transfer_end[a]=transfer_end[d]=copy+1
    original,suf,sdets,pre_indices=synth.split_suffix();end=h+2;dets+=sdets
    busy={q:min(u['t'] for u in suf if q in u['q']) for q in {q for u in suf for q in u['q']}}
    release={q:(transfer_end[q]+1 if q in A+D else readtimes[q]+1) for q in set(CELLS+D)}
    shift=max([release[q]-busy[q] for q in release if q in busy]+[-min(u['t'] for u in suf)])
    for u in suf:u['t']+=shift
    for j,a in enumerate(A):
        at=transfer_end[a]+1
        if at<busy.get(a,999)+shift:units.append(dict(k='M',q=(a,),t=at,b=502+j));dets.append([502+j])
    units+=suf
    return save(H/'cand'/name,units,dets,D,dict(source='15 native cells simultaneous15T',synthesis=rec,suffix_shift=shift,
                early_heralds=early_heralds,early_transfers=early_transfers))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--pre',type=int,default=10);ap.add_argument('--post',type=int,default=10)
    ap.add_argument('--seconds',type=float,default=120);ap.add_argument('--seed',type=int,default=0);ap.add_argument('--max-cx',type=int,default=76)
    ap.add_argument('--no-xhooks',action='store_true');args=ap.parse_args()
    r=solve(args.pre,args.post,args.seconds,args.seed,args.max_cx,not args.no_xhooks)
    name=f'wide15_p{args.pre}_d{args.post}_s{args.seed}_x{int(not args.no_xhooks)}'
    (H/f'{name}.network.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
    if r['status'] in ('FEASIBLE','OPTIMAL'):
        st=build(r,name);raw=raw_check(st.with_suffix('.qasm').read_text(),D);ans=dict(stem=str(st),raw=raw)
        if raw['ok']:
            c1,n=singles(st);ans.update(c1=c1,harmful=n)
            if c1<1e-5:ans['price']=price(st,1)
        print(json.dumps(ans),flush=True);(H/f'{name}.result.json').write_text(json.dumps(ans,indent=2)+'\n')
