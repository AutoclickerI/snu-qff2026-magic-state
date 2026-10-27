"""Two independently measured Clifford flags for parallel15T arithmetic.

The non-Clifford polynomial still has rank5. Coordinates32 and64 are extra plus
flags, each read whenever it becomes a single isolated physical factor. All
other non-target intermediate rows must carry at least one of those coordinates.
"""
import os,sys,json,random,heapq,math
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'PREFIX20261027'));sys.path.insert(0,str(H.parent/'T14'))
import synth
from search_phase import singles
from qcirc import save,adjacent
from qtools import price
from qtools.validity import raw_check
A=synth.A;D=synth.D;CELLS=[1,2,3,4,7,8,9,10,13,14,15,16]
FLAGS={32:7,64:13};RANK=7
INIT=tuple(9+A.index(q) if q in A else 16 if q==3 else 32 if q==7 else 64 if q==13 else 0 for q in CELLS)
EDGES=[(a,b) for a,q in enumerate(CELLS) for b,r in enumerate(CELLS) if adjacent(q,r)]
GOALS=synth.goals(24);GI={v:i for i,v in enumerate(GOALS)};TARGET=set(GOALS)

def allowed(r):return r==0 or r in TARGET or r&96 and r&31!=8

def isolated(rows,flag):
    ii=[i for i,r in enumerate(rows) if r&flag]
    return ii[0] if len(ii)==1 and rows[ii[0]]==flag else None

def metric(rows,cov):
    missing=15-cov.bit_count();nz=sum(r!=0 for r in rows)
    near=sum(v in {rows[a]^rows[b] for a,b in EDGES} for v in GOALS if not cov>>GI[v]&1)
    dirty=sum(max(0,sum(bool(r&f) for r in rows)-1) for f in FLAGS)
    return missing*5+(nz-RANK)*(.7 if missing else 3)+.18*dirty-.17*near

def search(seed=0,width=800,maxdepth=35):
    rng=random.Random(seed);cov=synth.coverage(INIT,GI)
    front=[(INIT,cov,[],[],[],(0,0))];seen={};sol=[];first=None
    for depth in range(1,maxdepth+1):
        keep={}
        for rows,cov,path,layers,checks,ages in front:
            old={f:isolated(rows,f) for f in FLAGS};base=metric(rows,cov);opts=[]
            for a,b in EDGES:
                if not rows[a] or not allowed(rows[a]^rows[b]):continue
                nr=list(rows);nr[b]^=nr[a];nc=cov|synth.coverage(nr,GI)
                opts.append((a,b,base-metric(nr,nc)))
            candidates=[[(a,b)] for a,b,g in opts]
            for trial in range(24):
                order=sorted(opts,key=lambda z:z[2]+(rng.random()*5 if trial else 0),reverse=True)
                used=set();layer=[]
                for a,b,g in order:
                    if a not in used and b not in used:layer.append((a,b));used.update([a,b])
                if layer:candidates.append(layer)
            for layer in candidates:
                nr=list(rows)
                for a,b in layer:nr[b]^=nr[a]
                nr=tuple(nr);nc=cov|synth.coverage(nr,GI);pp=path+layer;ll=layers+[layer];cp=list(checks);aa=[]
                for j,f in enumerate(FLAGS):
                    loc=isolated(nr,f);aa.append(0 if loc is not None else ages[j]+1)
                    if loc is not None and old[f] is None:cp.append((len(pp),loc,f))
                have=sum((1<<j) for j,f in enumerate(FLAGS) if any(c[2]==f for c in cp))
                nz=sum(r!=0 for r in nr)
                if nc==(1<<15)-1 and nz==RANK and have==3 and all(not r or (r&120).bit_count()%2 for r in nr):
                    sol.append(dict(rows=nr,path=pp,layers=ll,depth=len(pp),cx_layers=depth,cells=CELLS,flags=FLAGS,
                                    goals=GOALS,seed=seed,checkpoints=cp));first=depth if first is None else first;continue
                key=(nr,nc,have);cost=len(pp)+.1*sum(aa)
                if seen.get(key,math.inf)<=cost-1e-9:continue
                seen[key]=cost
                score=metric(nr,nc)+.07*len(pp)+.08*sum(aa)+.2*(2-have.bit_count())+rng.random()*.4
                if key not in keep or score<keep[key][0]:keep[key]=(score,nr,nc,pp,ll,cp,tuple(aa))
        front=[(r,c,p,l,k,a) for _,r,c,p,l,k,a in heapq.nsmallest(width,keep.values(),key=lambda z:z[0])]
        lead=front[0] if front else None
        print('twoflags',seed,depth,len(front),len(sol),(15-lead[1].bit_count(),sum(r!=0 for r in lead[0]),len(lead[2]),len(lead[4])) if lead else None,flush=True)
        if not front or first is not None and depth>=first+2:break
        if len(seen)>450000:seen={(r,c,sum((1<<j) for j,f in enumerate(FLAGS) if any(x[2]==f for x in k))):len(p)+.1*sum(a) for r,c,p,l,k,a in front}
    uniq={tuple(x['path']):x for x in sol}
    return sorted(uniq.values(),key=lambda r:(r['cx_layers'],r['depth']))[:4]

def build(rec,name):
    rows=list(INIT);states=[list(rows)];choices={v:[] for v in GOALS}
    for a,b in rec['path']:rows[b]^=rows[a];states.append(list(rows))
    for k,rr in enumerate(states):
        for i,v in enumerate(rr):
            if v in choices:choices[v].append((k,i))
    rng=random.Random(rec.get('phase_seed',0));mode=rec.get('phase_mode','first')
    chosen={v:opts[0] if mode=='first' else opts[-1] if mode=='last' else rng.choice(opts) for v,opts in choices.items()}
    checks={};bitaxis={}
    for j,(k,q,f) in enumerate(rec['checkpoints']):checks.setdefault(k,[]).append((q,900+j));bitaxis[900+j]=f
    back=[]
    for k,rr in enumerate(states):
        for v,(kk,q) in chosen.items():
            if k==kk:back.append(('TDG',(CELLS[q],),None))
        for q,b in checks.get(k,[]):back.append(('MX',(CELLS[q],),b))
        if k<len(rec['path']):a,b=rec['path'][k];back.append(('CX',(CELLS[a],CELLS[b]),None))
    assert sum(r!=0 for r in rows)==RANK
    units=[];last={q:-1 for q in range(36)}
    def add(k,qs,b=None):
        t=max(last[q] for q in qs)+1;units.append(dict(k=k,q=qs,t=t,b=b))
        for q in qs:last[q]=t
    for q,r in zip(CELLS,rows):add('RX' if r else 'R',(q,))
    for k,qs,b in reversed(back):add(k,qs,b)
    flagt=max(last.values())+1
    for u in units[:len(CELLS)]:
        touch=[v['t'] for v in units[len(CELLS):] if u['q'][0] in v['q']];u['t']=min(touch)-1 if touch else flagt-1
    units.append(dict(k='MX',q=(3,),t=flagt,b=500));dets=[[500]]
    finals={32:501,64:550}
    for f,q in FLAGS.items():units.append(dict(k='MX',q=(q,),t=flagt,b=finals[f]))
    zeros=[q for q in CELLS if q not in A+[3]+list(FLAGS.values())]
    for j,q in enumerate(zeros):units.append(dict(k='M',q=(q,),t=flagt,b=600+j));dets.append([600+j])
    previous={f:None for f in FLAGS}
    for u in sorted([u for u in units if u['b'] in bitaxis],key=lambda u:u['t']):
        f=bitaxis[u['b']];p=previous[f];dets.append([u['b']] if p is None else [p,u['b']]);previous[f]=u['b']
    for f,b in finals.items():dets.append([b] if previous[f] is None else [previous[f],b])
    h=flagt+1
    for d in D:units.append(dict(k='R',q=(d,),t=h,b=None))
    for a,d in zip(A,D):units.append(dict(k='CX',q=(a,d),t=h+1,b=None));units.append(dict(k='CX',q=(d,a),t=h+2,b=None))
    original,suf,sdets,pre=synth.split_suffix();dets+=sdets;end=h+2
    busy={q:min(u['t'] for u in suf if q in u['q']) for q in {q for u in suf for q in u['q']}}
    shift=max([end+1-busy[q] for q in set(CELLS+D) if q in busy]+[-min(u['t'] for u in suf)])
    for u in suf:u['t']+=shift
    for j,a in enumerate(A):
        if end+1<busy.get(a,999)+shift:units.append(dict(k='M',q=(a,),t=end+1,b=502+j));dets.append([502+j])
    units+=suf
    return save(H/'cand'/name,units,dets,D,dict(source='15T with two independent Clifford flags',synthesis=rec,phase_locations=chosen))

def main():
    out=[];best=1;number=0
    for seed in range(4):
        nets=search(seed)
        (H/f'twoflag_network_s{seed}.json').write_text(json.dumps(nets,indent=2)+'\n')
        for net in nets[:2]:
            for mode,ps in [('first',0),('last',0),('random',1),('random',2)]:
                rec=dict(net,phase_mode=mode,phase_seed=ps);name=f'twoflag_{number}_{mode}{ps}'
                try:
                    st=build(rec,name);raw=raw_check(st.with_suffix('.qasm').read_text(),D)
                    r=dict(stem=str(st),source_cx=net['depth'],cx_layers=net['cx_layers'],checks=len(net['checkpoints']),raw=raw)
                    if raw['ok']:
                        c1,n=singles(st);r.update(c1=c1,harmful=n)
                        if c1<1e-5:
                            p=price(st,1);r.update(loss=p['loss'],acceptance=p['acceptance'])
                            if p['acceptance']>=.5002 and p['loss']<best:
                                best=p['loss'];(H/'twoflag_best.json').write_text(json.dumps(r,indent=2)+'\n')
                    print(json.dumps(r),flush=True);out.append(r)
                except Exception as ex:
                    print('ERROR',name,repr(ex),flush=True);out.append(dict(name=name,error=repr(ex)))
                (H/'twoflag_results.json').write_text(json.dumps(out,indent=2)+'\n')
            number+=1

if __name__=='__main__':main()
