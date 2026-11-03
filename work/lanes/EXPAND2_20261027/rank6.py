"""Native six-coordinate phase-network search with two measured flag axes."""
import argparse,heapq,json,random,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/lanes/PREFIX20261027'))
import synth as old
from qcirc import save,adjacent
A=old.A;D=old.D;CELLS=old.CELLS;EDGES=old.EDGES
INIT=tuple(9+A.index(q) if q in A else 16 if q==3 else 32 for q in CELLS)


def goals(w):
    assert (w&8).bit_count()==1
    gs=[v for v in range(1,64) if (v&w).bit_count()%2 and v!=8]
    for z in range(64):assert (-sum((v&z).bit_count()%2 for v in gs)-((8&z).bit_count()%2))%8==0
    return gs


def synth(seed,w=8,beam=500,depth=90,coefficients=None):
    rng=random.Random(seed);gs=goals(w) if coefficients is None else sorted(coefficients);gi={v:1<<i for i,v in enumerate(gs)}
    full=(1<<len(gs))-1
    cov=lambda rs:sum(set(gi[v] for v in rs if v in gi))
    front=[(INIT,cov(INIT),[],0)];seen={(INIT,cov(INIT)):0}
    for d in range(1,depth+1):
        nxt=[]
        for rs,m,path,exposure in front:
            for a,b in EDGES:
                nv=rs[a]^rs[b]
                if not rs[a] or nv==8 or rs[a]==8 or rs[b]==8:continue
                rr=list(rs);rr[b]=nv;rr=tuple(rr);nm=m|cov(rr)
                key=(rr,nm)
                if seen.get(key,999)<=d:continue
                seen[key]=d;nz=sum(v!=0 for v in rr);bad=sum(1<=v<=7 for v in rr)
                ep=exposure+bad;pp=path+[(a,b)]
                if nm==full and nz==6 and bad==0:
                    return dict(seed=seed,functional=w,rows=list(rr),path=pp,goals=gs,coefficients=coefficients,depth=d,exposure=ep)
                missing=len(gs)-nm.bit_count()
                near=sum(1 for v in {rr[a]^rr[b] for a,b in EDGES} if v in gi and not nm&gi[v])
                score=missing*4+(nz-6)*(.8 if missing else 3)+bad*.5+ep*.015-near*.12+rng.random()*1.6
                nxt.append((score,rr,nm,pp,ep))
        if not nxt:return None
        front=[(r,m,p,e) for _,r,m,p,e in heapq.nsmallest(beam,nxt,key=lambda a:a[0])]
        if d%5==0:print('beam',seed,w,d,len(gs)-front[0][1].bit_count(),len(seen),flush=True)
        if len(seen)>600000:seen={(r,m):d for r,m,p,e in front}
    return None


def build(rec,name,mode='first',phase_seed=0):
    rows=list(INIT);states=[list(rows)]
    for a,b in rec['path']:rows[b]^=rows[a];states.append(list(rows))
    rng=random.Random(phase_seed);chosen={}
    for g in rec['goals']:
        options=[(k,i) for k,rr in enumerate(states) for i,v in enumerate(rr) if v==g]
        chosen[g]=options[0] if mode=='first' else options[-1] if mode=='last' else rng.choice(options)
    back=[]
    for k in range(len(states)):
        for g,(kk,i) in chosen.items():
            if kk==k:
                cs=rec.get('coefficients')
                c=-1 if cs is None else cs.get(g,cs.get(str(g)))
                assert c in (-1,1)
                back.append(('T' if c==1 else 'TDG',(CELLS[i],)))
        if k<len(rec['path']):
            a,b=rec['path'][k];back.append(('CX',(CELLS[a],CELLS[b])))
    units=[];last={q:-1 for q in range(36)}
    def add(k,qs,b=None):
        t=max(last[q] for q in qs)+1;units.append(dict(k=k,q=qs,t=t,b=b))
        for q in qs:last[q]=t
    for q,v in zip(CELLS,rows):add('RX' if v else 'R',(q,))
    for k,qs in reversed(back):add(k,qs)
    for u in units[:len(CELLS)]:
        use=[v['t'] for v in units[len(CELLS):] if u['q'][0] in v['q']]
        if use:u['t']=min(use)-1
    t=max(last.values())+1
    for q,bit in [(3,500),(7,501)]:units.append(dict(k='MX',q=(q,),t=t,b=bit))
    for q in D:units.append(dict(k='R',q=(q,),t=t+1,b=None))
    for a,d in zip(A,D):
        units.append(dict(k='CX',q=(a,d),t=t+2,b=None))
        units.append(dict(k='CX',q=(d,a),t=t+3,b=None))
    original,suffix,dets,pre=old.split_suffix()
    busy={q:min(u['t'] for u in suffix if q in u['q']) for q in {q for u in suffix for q in u['q']}}
    shift=max([t+4-busy[q] for q in set(CELLS)|set(D) if q in busy]+[-min(u['t'] for u in suffix)])
    for u in suffix:u['t']+=shift
    for j,a in enumerate(A):
        if t+4<busy.get(a,999)+shift:
            units.append(dict(k='M',q=(a,),t=t+4,b=502+j));dets.append([502+j])
    units+=suffix;dets+=[[500],[501]]
    t0=min(u['t'] for u in units)
    for u in units:u['t']-=t0
    (HERE/'cand').mkdir(exist_ok=True)
    return save(HERE/'cand'/name,units,dets,D,dict(synthesis=rec,phase_locations=chosen,phase_mode=mode,phase_seed=phase_seed))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seed',type=int,default=0);p.add_argument('--functional',type=int,default=8);p.add_argument('--beam',type=int,default=500);p.add_argument('--price',action='store_true');p.add_argument('--t23-mask',type=int,default=0)
    args=p.parse_args();cs=None
    if args.t23_mask:
        s1={v for v in range(64) if v&8 and not v&16}
        s2={v for v in range(64) if v&32 and not (v&args.t23_mask).bit_count()%2}
        cs={v:int(v==8)-int(v in s1)+int(v in s2) for v in range(1,64)}
        cs={v:c for v,c in cs.items() if c}
        assert len(cs)==23 and all(c in (-1,1) for c in cs.values())
        for z in range(64):assert (sum(c*((v&z).bit_count()%2) for v,c in cs.items())-((8&z).bit_count()%2))%8==0
    rec=synth(args.seed,args.functional,args.beam,coefficients=cs)
    if rec is None:print('no witness',flush=True);sys.exit(0)
    name=f'r6_w{args.functional}_s{args.seed}' if cs is None else f'r6_t23_m{args.t23_mask}_s{args.seed}'
    (HERE/(name+'.network.json')).write_text(json.dumps(rec,indent=2)+'\n')
    stem=build(rec,name)
    print('candidate',stem,flush=True)
    if args.price:
        import analytic_price
        out=analytic_price.price(stem,verbose=True)
        Path(str(stem)+'.price.json').write_text(json.dumps(out,indent=2)+'\n')
        print(json.dumps(out,indent=2),flush=True)
