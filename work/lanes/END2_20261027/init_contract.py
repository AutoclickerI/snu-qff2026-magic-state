"""Verified initializations for a jointly synthesized resource.

Use a literal M on known-zero inputs; otherwise prepare then herald in a free
earlier slot. Optional MX sources carry their phase into detector expressions.
"""
import argparse,copy,json,sys
from pathlib import Path
from joint import *
from tprep.exact import run

def expectation(ops,q,t,P):
    state,inv,_,_,wires=run(f.native_text([o for o in ops if o.time<t])[0],36)
    p=state.stim.PauliString(state.n);p[wires[q]]=P
    return state.expectation(p,inv)

def build_contract(sol,mode='zero'):
    stem=ROOT/sol['stem'];ops,dets=f.parse_current(stem.with_suffix('.qasm').read_text())
    initial_ops=copy.deepcopy(ops);nextbit=max(o.bit for o in ops if o.bit is not None)+1
    first={q:min(sol['T0']+t for t,layer in enumerate(sol['ops']) if any(q in e for e in layer)) for q in CELLS}
    changes=[];sources={}
    for q in CELLS:
        pivot=bool(int(sol['pivots'].get(str(q),0)))
        choices=[o for o in ops if o.qs==(q,) and o.kind in ('R','RX') and INIT_MIN[q]<=o.time<first[q]]
        o=max(choices,key=lambda o:o.time) if choices else None
        if pivot:
            if mode!='both':continue
            assert o is not None and o.kind=='RX'
            o.kind='MX';o.bit=nextbit;nextbit+=1;sources[o.bit]=q
            changes.append(dict(q=q,time=o.time,kind='MX affine phase source',bit=o.bit))
            continue
        if o is None:
            t=first[q]-1
            if any(q in u.qs and u.time==t for u in ops):continue
            ev=expectation(initial_ops,q,t,'Z')
            if abs(ev-1)>1e-9:continue
            o=f.Op('M',(q,),t,nextbit);nextbit+=1;ops.append(o);dets.append({o.bit})
            changes.append(dict(q=q,time=t,kind='direct known-zero M',bit=o.bit));continue
        assert o.kind=='R'
        ev=expectation(initial_ops,q,o.time,'Z')
        if abs(ev-1)<1e-9:
            how='direct known-zero M'
        else:
            occupied={u.time for u in ops if q in u.qs}
            t=o.time-1
            while t in occupied:t-=1
            if t<INIT_MIN[q]:continue
            ops.append(f.Op('R',(q,),t));how=f'R@{t} then herald M'
        o.kind='M';o.bit=nextbit;nextbit+=1;dets.append({o.bit})
        changes.append(dict(q=q,time=o.time,kind=how,bit=o.bit))
    frames={q:[set(),set()] for q in range(36)};corr={}
    for o in sorted(ops,key=lambda o:o.time):
        q=o.qs[0]
        if o.bit in sources:
            frames[q]=[set(),{o.bit}];continue
        if o.kind in ('R','RX'):frames[q]=[set(),set()]
        elif o.kind=='CX':
            a,b=o.qs;frames[b][0]^=frames[a][0];frames[a][1]^=frames[b][1]
        elif o.kind=='H':frames[q].reverse()
        elif o.kind in ('M','MX'):
            corr[o.bit]=set(frames[q][o.kind=='MX'])
        elif o.kind in ('T','TDG'):assert not frames[q][0]
    for q in D:assert not any(frames[q]),('physical output frame',q,frames[q])
    fixed=[]
    for row in dets:
        extra=set()
        for bit in row:extra^=corr.get(bit,set())
        fixed.append(row^extra)
    text=emit(ops,fixed)
    out=write_stem(text,D,HERE/'cand',Path(sol['stem']).name+'_init_'+mode,source={'base':sol['stem'],'initialization_changes':changes})
    return out,text,changes

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('solution');ap.add_argument('--mode',choices=['zero','both'],default='zero');ap.add_argument('--price',action='store_true');a=ap.parse_args()
    sol=json.loads(Path(a.solution).read_text());stem,text,changes=build_contract(sol,a.mode)
    out={'stem':str(stem.relative_to(ROOT)),'changes':changes,'raw':raw_check(text,D)}
    print(json.dumps(out),flush=True)
    if a.price and out['raw']['ok']:out['price']=price(stem,1,use_cache=False)
    (HERE/'sol'/f"{Path(a.solution).stem}_init_{a.mode}.json").write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out),flush=True)
