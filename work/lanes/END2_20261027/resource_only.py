"""Fresh14-cell B/C resource synthesis for NATIVE2's compact footprint.

All cells begin unused in |0>. Nonpivot M preparations are literal detectors;
MX pivot results are propagated as Z frames into the eventual B-X checks.
The returned module includes the complete affine readout contract.
"""
import argparse,json,itertools
from pathlib import Path
import joint as j
from ortools.sat.python import cp_model

B=[6,26,13,11,4,23,27]
C=[12,25,19,17,5,29,28]
HERE=Path(__file__).resolve().parent

def old_hint():
    ops,_=j.f.parse_current((j.ROOT/'work/lanes/PREFIX20261027/cand/final_phase_random_1.qasm').read_text())
    selected=[o for o in ops if set(o.qs)<=set(B+C) and o.time<=28]
    r={q:0 for q in B+C};piv={};v=1
    for o in selected:
        q=o.qs[0]
        if o.kind in ('MX','RX'):r[q]=v;piv[q]=v;v<<=1
        elif o.kind=='R':r[q]=0
        elif o.kind=='CX':r[o.qs[1]]^=r[q]
        elif o.kind=='M':assert r[q]==0,(o,r[q])
    assert v==8 and all(r[q]==0 for q in C),(v,r)
    transform=None
    for a,b,c in itertools.product(range(1,8),repeat=3):
        def trans(v):return (a if v&1 else 0)^(b if v&2 else 0)^(c if v&4 else 0)
        if all(trans(r[q])==i+1 for i,q in enumerate(B)):
            transform=(a,b,c);break
    assert transform is not None
    a,b,c=transform
    tr=lambda v:(a if v&1 else 0)^(b if v&2 else 0)^(c if v&4 else 0)
    return {'ops':[[list(o.qs) for o in selected if o.kind=='CX' and o.time==16+t] for t in range(13)],'pivots':{str(q):tr(piv.get(q,0)) for q in B+C}}

def contract(sol):
    ops=[];frames={q:set() for q in B+C};nextbit=0;detectors=[];inits=[]
    first={q:min(t for t,layer in enumerate(sol['ops']) if any(q in e for e in layer)) for q in B+C}
    for q in B+C:
        bit=nextbit;nextbit+=1;t=first[q]-1;pivot=sol['pivots'][str(q)]!=0
        assert t>=0
        inits.append({'time':t,'kind':'MX' if pivot else 'M','q':q,'bit':bit})
        if pivot:frames[q]={bit}
        else:detectors.append([bit])
    for layer in sol['ops']:
        for a,b in layer:frames[a]^=frames[b]
    bx=[]
    for support in j.f.SUPPORTS:
        correction=set()
        for i in support:correction^=frames[B[i]]
        bx.append({'B_indices':sorted(support),'initial_record_xor':sorted(correction)})
    gauge=sol.get('gauge',[]);checks=[];basis={}
    for row in sorted(range(1,128),key=lambda v:(v.bit_count(),v)):
        if any((row&g).bit_count()%2 for g in gauge):continue
        v=row
        for k,b in sorted(basis.items(),reverse=True):
            if v>>k&1:v^=b
        if v:basis[v.bit_length()-1]=v;checks.append({'C_indices':[i for i in range(7) if row>>i&1]})
    assert len(checks)==7-len(gauge)
    cx=[]
    for g in gauge:
        support=[i for i in range(7) if g>>i&1];correction=set()
        for i in support:correction^=frames[C[i]]
        cx.append({'C_indices':support,'initial_record_xor':sorted(correction)})
    return {'B':B,'C':C,'layers':sol['ops'],'initializations':inits,'initial_zero_detectors':detectors,
            'B_X_checks':bx,'C_Z_checks':checks,'C_X_generators':cx,'C_gauge_basis':gauge,'logical_frame':'zero',
            'first_layer_time':0,'last_layer_time':len(sol['ops'])-1,
            'prerequisite':'Every B/C cell unused and ideal |0> before first initialization; no external interactions until module ends.'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('name');ap.add_argument('--depth',type=int,default=13);ap.add_argument('--seconds',type=float,default=180);ap.add_argument('--seed',type=int,default=1);ap.add_argument('--wbad',type=int,default=200);ap.add_argument('--wunflag',type=int,default=500);ap.add_argument('--gauge',default='');a=ap.parse_args()
    gauge=[int(v) for v in a.gauge.split(',') if v]
    j.B=B;j.C=C;j.CELLS=B+C;j.COL={q:i+1 for i,q in enumerate(B)}
    j.EDGES=[(q,r) for q in B+C for r in B+C if abs(q//6-r//6)+abs(q%6-r%6)==1]
    j.INIT_MIN={q:0 for q in B+C};j.split_base=lambda:([],[],[])
    hint=old_hint()
    if a.depth>len(hint['ops']):hint['ops']=[[] for _ in range(a.depth-len(hint['ops']))]+hint['ops']
    m,sel,x,ncx,bad,risk=j.build(0,a.depth,wx=5,wz=1,wbad=a.wbad,wunflag=a.wunflag,source_zero=True,hint=hint,verified_init=True,gauge=gauge)
    s=cp_model.CpSolver();s.parameters.max_time_in_seconds=a.seconds;s.parameters.num_search_workers=1;s.parameters.random_seed=a.seed
    status=s.Solve(m);out={'status':s.StatusName(status),'seconds':s.WallTime(),'depth':a.depth,'seed':a.seed,'gauge':gauge}
    if status in (cp_model.FEASIBLE,cp_model.OPTIMAL):
        out.update(ops=[[list(e) for e,v in row.items() if s.Value(v)] for row in sel],pivots={str(q):sum(s.Value(b)<<k for k,b in enumerate(x[0][q])) for q in B+C},cx=s.Value(ncx),bad=s.Value(bad),unflagged=s.Value(risk),objective=s.ObjectiveValue(),bound=s.BestObjectiveBound())
        out['module']=contract(out)
    (HERE/'sol').mkdir(exist_ok=True);(HERE/'sol'/f'{a.name}.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out),flush=True)
