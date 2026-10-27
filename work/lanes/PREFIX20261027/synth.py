"""Native rank-five 15-T phase/encoder synthesis with free initial product basis.

The sum of all 15 non-logical forms in an affine hyperplane of F2^5
implements logical T on the Steane code, with a fifth X-measured flag.
Synthesis works backwards from code coordinates and stops at ANY product
state basis, avoiding a fixed encoder or restoration to the original wires.
All intermediate one-site and CX-supported Z faults are forbidden from
being the logical axis 8. This is a screening condition, not a full FT proof.
"""
import argparse,json,math,random,sys,time,heapq
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'work/lanes/T14'))
from qcirc import parse,emit,save,adjacent
HERE=Path(__file__).resolve().parent
A=[1,14,8,9,2,16,15]
D=[0,20,7,10,3,22,21]
B=[6,26,13,11,4,23,27]
CELLS=[1,2,3,7,8,9,14,15,16]
INIT=tuple((9+A.index(q)) if q in A else 16 if q==3 else 0 for q in CELLS)
EDGES=[(i,j) for i,a in enumerate(CELLS) for j,b in enumerate(CELLS) if adjacent(a,b)]
LOGICAL=8
FLAG=3;ZERO=7

def goals(functional):
    assert (functional&LOGICAL).bit_count()%2==1
    return [v for v in range(1,32) if (v&functional).bit_count()%2 and v!=LOGICAL]

def coverage(rows,goalidx):
    m=0
    for v in rows:
        if v in goalidx:m|=1<<goalidx[v]
    return m

def neighbors(rows):
    for a,b in EDGES:
        v=rows[b]^rows[a]
        if not rows[a] or v==LOGICAL or rows[a]==LOGICAL or rows[b]==LOGICAL:continue
        rr=list(rows);rr[b]=v
        yield (a,b),tuple(rr)

def synth(seed=0,functional=8,beam=800,depth=60,unsafe_weight=0.,safe_start=False):
    rng=random.Random(seed);target=goals(functional);gi={v:i for i,v in enumerate(target)}
    full=(1<<15)-1;cov=coverage(INIT,gi)
    # Importance of eliminating redundant rows rises after coverage.
    front=[(INIT,cov,[],0)];seen={(INIT,cov):0};best=None
    for d in range(1,depth+1):
        nxt=[]
        for rows,m,path,exposure in front:
            for edge,rr in neighbors(rows):
                nm=m|coverage(rr,gi);key=(rr,nm)
                if seen.get(key,999)<=d:continue
                seen[key]=d
                nz=sum(v!=0 for v in rr)
                pp=path+[edge]
                bad=sum(1<=v<=7 for v in rr)
                exp2=exposure+bad
                if nm==full and nz==5 and (not safe_start or bad==0):return dict(seed=seed,functional=functional,rows=list(rr),path=pp,depth=d,goals=target,unsafe_exposure=exp2,unsafe_weight=unsafe_weight)
                missing=15-nm.bit_count()
                # Local distance from missing axes to row XORs breaks plateaus.
                present=set(rr)
                xor2={rr[a]^rr[b] for a,b in EDGES}
                near=sum(v in xor2 for v in target if not (nm>>gi[v]&1))
                score=missing*4.0+(nz-5)*(.7 if missing else 3)+rng.random()*1.4-near*.18
                score += unsafe_weight*(bad+exp2*.08)
                nxt.append((score,rr,nm,pp,exp2))
        if not nxt:break
        front=[(r,m,p,e) for _,r,m,p,e in heapq.nsmallest(beam,nxt,key=lambda x:x[0])]
        if d%5==0:
            lead=front[0];print('beam',seed,functional,d,15-lead[1].bit_count(),sum(v!=0 for v in lead[0]),len(seen),flush=True)
        # Bound memory; beam already retains all useful paths.
        if len(seen)>800000:seen={(r,m):d for r,m,p,e in front}
    return None

def split_suffix():
    """Reuse the exact checked 98-CX suffix from the T14 experiment artifact.

    Do not apply a lifetime component splitter to v37j: its continuous guards
    deliberately join resource and data components before the terminal round.
    """
    p=ROOT/'work/lanes/T14'
    units,dets=parse((p/'t14a.qasm').read_text())
    stage=json.loads((p/'t14a.stage.json').read_text())
    prekeys={(u['t'],u['k'],tuple(u['q'])) for u in stage}
    pre={i for i,u in enumerate(units) if (u['t'],u['k'],u['q']) in prekeys}
    pb={units[i]['b'] for i in pre if units[i]['b'] is not None}
    suf=[dict(u) for i,u in enumerate(units) if i not in pre]
    ds=[d for d in dets if not(set(d)&pb)]
    assert sum(u['k']=='CX' for u in suf)==98
    return units,suf,ds,pre

def build(rec,name):
    # Record every available location for each phase axis, then jointly choose
    # locations. Moving a phase along an unchanged row preserves the unitary but
    # changes physical fault propagation through the remaining rotations.
    rr=list(INIT);gi=set(rec['goals']);states=[list(rr)];choices={v:[] for v in gi}
    for a,b in rec['path']:
        rr[b]^=rr[a];states.append(list(rr))
    for k,state in enumerate(states):
        for i,v in enumerate(state):
            if v in gi:choices[v].append((k,i))
    mode=rec.get('phase_mode','first');rng=random.Random(rec.get('phase_seed',0))
    chosen={}
    for v,opts in choices.items():
        assert opts
        pick=opts[0] if mode=='first' else opts[-1] if mode=='last' else rng.choice(opts)
        if 'phase_locations' in rec:pick=tuple(rec['phase_locations'][str(v)])
        chosen[v]=pick
    back=[]
    for k,state in enumerate(states):
        for v,(kk,i) in chosen.items():
            if kk==k:back.append(('TDG',(CELLS[i],)))
        if k<len(rec['path']):
            a,b=rec['path'][k];back.append(('CX',(CELLS[a],CELLS[b])))
    assert len(chosen)==15 and sum(v!=0 for v in rr)==5
    rec=dict(rec,phase_locations={str(v):list(p) for v,p in chosen.items()})
    # Parallelize a fixed order by per-wire dependencies. Only true dependencies
    # are retained; a full barrier is emitted for each resulting native layer.
    units=[];last={q:-1 for q in range(36)}
    def add(k,qs,b=None):
        t=max(last[q] for q in qs)+1
        units.append(dict(k=k,q=qs,t=t,b=b))
        for q in qs:last[q]=t
    for q,v in zip(CELLS,rr):add('RX' if v else 'R',(q,))
    for k,qs in reversed(back):add(k,qs)
    if rec.get('alap_init',False):
        for init in units[:len(CELLS)]:
            q=init['q'][0]
            touch=[u['t'] for u in units[len(CELLS):] if q in u['q']]
            if touch:init['t']=min(touch)-1
    # All phase axes are present and all final data rows have returned.
    flagt=max(last.values())+1
    units.append(dict(k='MX',q=(FLAG,),t=flagt,b=500))
    units.append(dict(k='M',q=(ZERO,),t=flagt,b=501))
    h=flagt+1
    # Optional native syndrome projectors: compute one code stabilizer onto a
    # physical wire, measure it, then invert the compute. No clean-resource oracle.
    for check in rec.get('postchecks',[]):
        mask=int(check['mask']);basis=check.get('basis','X')
        support=sum(1<<CELLS.index(A[j-1]) for j in range(1,8) if (j&mask).bit_count()%2)
        from collections import deque
        queue=deque([(support,[])])
        seen={support};found=None
        while queue:
            v,path=queue.popleft()
            if v and v&(v-1)==0:
                found=(v.bit_length()-1,path);break
            for a,b in EDGES:
                ca,ta=(a,b) if basis=='X' else (b,a)
                if not (v>>ca&1):continue
                nv=v^(1<<ta)
                if nv not in seen:seen.add(nv);queue.append((nv,path+[(a,b)]))
        assert found is not None
        q,path=found
        for a,b in path:units.append(dict(k='CX',q=(CELLS[a],CELLS[b]),t=h,b=None));h+=1
        bit=700+len([u for u in units if u['b'] is not None and u['b']>=700])
        units.append(dict(k='MX' if basis=='X' else 'M',q=(CELLS[q],),t=h,b=bit));h+=1
        for a,b in reversed(path):units.append(dict(k='CX',q=(CELLS[a],CELLS[b]),t=h,b=None));h+=1
    # Hops require freshly initialized target cells, including 19/20 freed above.
    for d in D:units.append(dict(k='R',q=(d,),t=h,b=None))
    for a,d in zip(A,D):
        assert adjacent(a,d)
        units.append(dict(k='CX',q=(a,d),t=h+1,b=None))
        units.append(dict(k='CX',q=(d,a),t=h+2,b=None))
    original,suf,dets,pre=split_suffix()
    end=h+2
    # Shift intact suffix enough to keep all source cells free during the new stage.
    busy={q:min(u['t'] for u in suf if q in u['q']) for q in {q for u in suf for q in u['q']}}
    floor=-min(u['t'] for u in suf) if rec.get('pull_suffix',False) else 0
    shift=max([end+1-busy[q] for q in set(CELLS)|set(D) if q in busy]+[floor])
    # Main output propagation remains complete; allow suffix to run in parallel on
    # unrelated cells. This is not a final optimal co-schedule.
    for u in suf:u['t']+=shift
    # Add heralds on the vacated source cells while available.
    for j,a in enumerate(A):
        if end+1<busy.get(a,999)+shift:
            units.append(dict(k='M',q=(a,),t=end+1,b=502+j));dets.append([502+j])
    units+=suf;dets += [[500],[501]] + [[u['b']] for u in units if u['b'] is not None and u['b']>=700]
    min_t=min(u['t'] for u in units)
    for u in units:u['t']-=min_t
    meta=dict(source='PREFIX20261027 rank5 joint phase encoder',synthesis=rec,suffix_shift=shift,prefix_removed_cx=sum(original[i]['k']=='CX' for i in pre))
    return save(HERE/'cand'/name,units,dets,D,meta)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--seed',type=int,default=0);ap.add_argument('--functional',type=int,default=8);ap.add_argument('--beam',type=int,default=500);ap.add_argument('--depth',type=int,default=60);a=ap.parse_args()
    (HERE/'cand').mkdir(exist_ok=True)
    r=synth(a.seed,a.functional,a.beam,a.depth)
    print('result',r,flush=True)
    if r:
        (HERE/f'network_{a.functional}_{a.seed}.json').write_text(json.dumps(r,indent=2))
        print('candidate',build(r,f'rank5_{a.functional}_{a.seed}'),flush=True)
