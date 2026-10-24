"""Necessary direct-contact footprint test, including all baseline star arms."""
import json
import itertools
from ortools.sat.python import cp_model
from grid import L,near,HERE
def fit(data,mask):
    m=cp_model.CpModel();choices={};bycell={q:[] for q in range(36)}
    free=set(range(36))-set(data)
    for i,d in enumerate(data):
        options=[]
        for a,b in itertools.permutations([q for q in free if near(q,d)],2):
            for c in free-{a,b}:
                if not near(b,c) or (mask>>i&1 and not near(a,c)):continue
                x=m.NewBoolVar(f'{i}_{a}_{b}_{c}');options.append((x,a,b,c))
                for q in (a,b,c):bycell[q].append(x)
        choices[i]=options;m.AddExactlyOne([o[0] for o in options])
    for vs in bycell.values():
        if vs:m.AddAtMostOne(vs)
    s=cp_model.CpSolver();s.parameters.num_workers=1;st=s.Solve(m)
    out=dict(mask=mask,data=data,status=s.StatusName(st))
    if st in (cp_model.OPTIMAL,cp_model.FEASIBLE):
        out['witness']={i:[a,b,c] for i,vs in choices.items() for x,a,b,c in vs if s.Value(x)}
    return out
if __name__=='__main__':
    names=json.loads((HERE/'readout_finalists.json').read_text())
    masks=sorted({int(n[6:]) for n in names if n.startswith('acmask')})
    results=[fit(data,mask) for data in ([0,20,7,4,3,15,8],L['d']) for mask in masks]
    (HERE/'mask_fit.json').write_text(json.dumps(results,indent=2)+'\n')
    print([(x['mask'],x['data']==L['d'],x['status']) for x in results])
