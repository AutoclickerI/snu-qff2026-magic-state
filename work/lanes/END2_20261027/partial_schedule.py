"""Schedule commuting native resource CXs, then recheck both-axis fault safety.

Only mathematically commuting gates may reorder. First-order safety is audited
again because changing physical fault locations can change a noisy circuit.
"""
import argparse
import json
from pathlib import Path
from ortools.sat.python import cp_model
from partial_contract import HERE, COLS, CELLS, HELPERS, fault_signature


def unsafe(layers, cells):
    hs=[q for q in cells if q in HELPERS]
    hx={q:fault_signature(q,'X',hs) for q in cells}
    hz={q:fault_signature(q,'Z',hs) for q in cells}
    def bad(sig):
        s=sig&7;p=(sig>>3)&1
        return not(sig>>4) and p!=bool(s)
    out=[]
    for t in range(len(layers)-1,-1,-1):
        for a,b in layers[t]:
            for axis,h in [('X',hx),('Z',hz)]:
                v=h[a]^h[b]
                if bad(v):out.append(dict(layer=t,edge=[a,b],axis=axis,signature=v))
            hx[a]^=hx[b]
            hz[b]^=hz[a]
    return out


def schedule(path,release=None,seconds=20,tag='schedule'):
    source=json.loads(Path(path).read_text())
    oldlayers=source.get('layers',source.get('ops'))
    ops=[tuple(e) for layer in oldlayers for e in layer]
    cells=source['cells'];release={int(q):int(v) for q,v in (release or {}).items()}
    pivots=source.get('pivots') or dict(zip(cells,source['initial_rows']))
    ready={q:release.get(q,-1)+1 for q in cells};hint=[]
    for a,b in ops:
        t=max(ready[a],ready[b]);hint.append(t);ready[a]=ready[b]=t+1
    upper=max(ready.values());m=cp_model.CpModel()
    starts=[m.NewIntVar(max(release.get(a,-1),release.get(b,-1))+1,upper-1,f's{i}') for i,(a,b) in enumerate(ops)]
    ends=[m.NewIntVar(1,upper,f'e{i}') for i in range(len(ops))]
    for s,e in zip(starts,ends):m.Add(e==s+1)
    intervals=[m.NewIntervalVar(s,1,e,f'g{i}') for i,(s,e) in enumerate(zip(starts,ends))]
    for q in cells:m.AddNoOverlap([iv for iv,gate in zip(intervals,ops) if q in gate])
    critical=[];pairs=0
    for i,(a,b) in enumerate(ops):
        preds=[j for j,(c,d) in enumerate(ops[:i]) if b==c or d==a]
        for j in preds:m.Add(starts[i]>=ends[j])
        pairs+=len(preds)
        critical.append(max([max(release.get(a,-1),release.get(b,-1))+1]+[critical[j] for j in preds])+1)
    last=m.NewIntVar(1,upper,'last');m.AddMaxEquality(last,ends)
    m.Minimize(last)
    for s,v in zip(starts,hint):m.AddHint(s,v)
    m.AddHint(last,max(hint)+1)
    sol=cp_model.CpSolver();sol.parameters.num_search_workers=1;sol.parameters.max_time_in_seconds=seconds
    status=sol.Solve(m)
    out=dict(source=str(path),status=sol.StatusName(status),seconds=sol.WallTime(),
             commutation_precedences=pairs,old_depth=len(oldlayers),hint_end=max(hint)+1,
             critical_path_bound=max(critical),release=release,cells=cells,pivots=pivots)
    if status in (cp_model.OPTIMAL,cp_model.FEASIBLE):
        R=sol.Value(last);layers=[[] for _ in range(R)]
        for gate,t in zip(ops,starts):layers[sol.Value(t)].append(gate)
        out.update(T0=0,depth=R,ops=layers,cx=len(ops),unsafe_axis_pairs=unsafe(layers,cells),
                   objective=sol.ObjectiveValue(),bound=sol.BestObjectiveBound())
    dest=HERE/'sol'/f'{tag}_{Path(path).stem}.json';dest.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('ops','pivots','cells','release','unsafe_axis_pairs')}),
          'unsafe',len(out.get('unsafe_axis_pairs',[])),flush=True)
    return dest,out


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('source');ap.add_argument('--release')
    ap.add_argument('--seconds',type=float,default=20);ap.add_argument('--tag',default='schedule')
    a=ap.parse_args();rel=json.loads(Path(a.release).read_text()) if a.release else None
    if rel and 'release' in rel:rel=rel['release']
    schedule(a.source,rel,a.seconds,a.tag)
