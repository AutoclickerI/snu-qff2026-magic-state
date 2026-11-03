"""Rank-six Clifford embedding of the existing rank-five 15-T polynomial.

The extra independent coordinate32 is never a T axis. It can flow through the
native parity network and ends on a second X-heralded qubit, detecting Clifford
faults without doubling the non-Clifford polynomial to31 rotations.
"""
import os,sys,json,random,heapq,math
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'PREFIX20261027'));sys.path.insert(0,str(H.parent/'T14'))
from search_phase import singles
import synth
from qcirc import save
from qtools import price
from qtools.validity import raw_check
A=synth.A;D=synth.D;CELLS=synth.CELLS;EDGES=synth.EDGES
INIT=tuple((9+A.index(q)) if q in A else 16 if q==3 else 32 for q in CELLS)
GOALS=synth.goals(24)

def addweights(w,adds):
    nw=list(w);value=0.
    for r,a in adds:
        if r and a:value+=a*nw[r^8];nw[r]+=a
    return tuple(nw),value

def search(seed=0,width=650,maxdepth=42,gamma=.15):
    rng=random.Random(seed);gi={v:i for i,v in enumerate(GOALS)};full=(1<<15)-1
    w=[0.]*64
    for r in GOALS:w[r]+=1/3
    for r in range(9,16):w[r]+=4
    front=[(INIT,synth.coverage(INIT,gi),[],tuple(w),0.,0)];seen={};found=[];first=None
    for depth in range(1,maxdepth+1):
        nxt=[]
        for rows,cov,path,w,cost,touch in front:
            for a,b in EDGES:
                if not rows[a] or rows[a]^rows[b]==8:continue
                nr=list(rows);nr[b]^=nr[a];nr=tuple(nr)
                nc=cov|synth.coverage(nr,gi);nt=touch+int(CELLS[a]==7 or CELLS[b]==7)
                adds=[(rows[i],1/3) for i in range(9) if i not in (a,b)]
                adds += [(rows[a],1/15),(rows[b],1/15),(nr[b],1/15)]
                ww,delta=addweights(w,adds);cc=cost+delta;key=(nr,nc,min(nt,2))
                if seen.get(key,math.inf)<=cc+1e-10:continue
                seen[key]=cc;pp=path+[(a,b)];missing=15-nc.bit_count();nz=sum(v!=0 for v in nr)
                safe=all(not v or (v&56).bit_count()%2 for v in nr)
                if not missing and nz==6 and safe and nt>=2:
                    _,last=addweights(ww,[(v,1.) for v in nr if v])
                    found.append(dict(rows=nr,path=pp,depth=depth,goals=GOALS,seed=seed,functional=24,
                                      extra_flag=32,z_pair_proxy=cc+last,gamma=gamma))
                    first=depth if first is None else first
                near=sum(v in {nr[c]^nr[t] for c,t in EDGES} for v in GOALS if not nc>>gi[v]&1)
                unsafe=sum(v!=0 and not (v&56).bit_count()%2 for v in nr)
                score=missing*5+(nz-6)*(.7 if missing else 3)+gamma*cc+.4*unsafe-.14*near+rng.random()*.5
                if nt<2:score+=.3
                nxt.append((score,nr,nc,pp,ww,cc,nt))
        front=[(r,c,p,w,z,t) for _,r,c,p,w,z,t in heapq.nsmallest(width,nxt,key=lambda z:z[0])]
        if depth%5==0:print('beam',seed,gamma,depth,len(front),len(found),flush=True)
        if not front or first is not None and depth>=first+3:break
        if len(seen)>900000:seen={(r,c,min(t,2)):z for r,c,p,w,z,t in front}
    unique={tuple(x['path']):x for x in found}
    return sorted(unique.values(),key=lambda r:(r['z_pair_proxy']+.1*r['depth'],r['depth']))[:6]

def build(rec,name):
    rows=list(INIT);states=[list(rows)];choices={v:[] for v in GOALS}
    for a,b in rec['path']:rows[b]^=rows[a];states.append(list(rows))
    for k,rr in enumerate(states):
        for i,v in enumerate(rr):
            if v in choices:choices[v].append((k,i))
    rng=random.Random(rec.get('phase_seed',0));mode=rec.get('phase_mode','first')
    chosen={v:(opts[0] if mode=='first' else opts[-1] if mode=='last' else rng.choice(opts)) for v,opts in choices.items()}
    back=[]
    checkpoints={int(k):int(q) for k,q in rec.get('checkpoints',[])}
    for k,rr in enumerate(states):
        for v,(kk,i) in chosen.items():
            if k==kk:back.append(('TDG',(CELLS[i],),None))
        if k in checkpoints:back.append(('MX',(CELLS[checkpoints[k]],),900+k))
        if k<len(rec['path']):
            a,b=rec['path'][k];back.append(('CX',(CELLS[a],CELLS[b]),None))
    assert sum(v!=0 for v in rows)==6 and len(chosen)==15
    units=[];last={q:-1 for q in range(36)}
    def add(k,qs,b=None):
        t=max(last[q] for q in qs)+1;units.append(dict(k=k,q=qs,t=t,b=b))
        for q in qs:last[q]=t
    for q,v in zip(CELLS,rows):add('RX' if v else 'R',(q,))
    for k,qs,b in reversed(back):add(k,qs,b)
    for u in units[:len(CELLS)]:
        touch=[v['t'] for v in units[len(CELLS):] if u['q'][0] in v['q']]
        if touch:u['t']=min(touch)-1
    flagt=max(last.values())+1
    for u in units[:len(CELLS)]:
        if not any(u['q'][0] in v['q'] for v in units[len(CELLS):]):u['t']=flagt-1
    units += [dict(k='MX',q=(q,),t=flagt,b=500+i) for i,q in enumerate([3,7])]
    extra_zeros=[q for q in CELLS if q not in A+[3,7]]
    units += [dict(k='M',q=(q,),t=flagt,b=600+i) for i,q in enumerate(extra_zeros)]
    h=flagt+1
    for d in D:units.append(dict(k='R',q=(d,),t=h,b=None))
    for a,d in zip(A,D):
        units.append(dict(k='CX',q=(a,d),t=h+1,b=None));units.append(dict(k='CX',q=(d,a),t=h+2,b=None))
    original,suf,dets,pre=synth.split_suffix();end=h+2
    busy={q:min(u['t'] for u in suf if q in u['q']) for q in {q for u in suf for q in u['q']}}
    shift=max([end+1-busy[q] for q in set(CELLS+D) if q in busy]+[-min(u['t'] for u in suf)])
    for u in suf:u['t']+=shift
    for j,a in enumerate(A):
        if end+1<busy.get(a,999)+shift:units.append(dict(k='M',q=(a,),t=end+1,b=502+j));dets.append([502+j])
    interim=sorted([u for u in units if u['b'] is not None and u['b']>=900],key=lambda u:u['t'])
    previous=None
    for u in interim:
        dets.append([u['b']] if previous is None else [previous,u['b']]);previous=u['b']
    units+=suf;dets += [[500],[501] if previous is None else [previous,501]]+[[600+i] for i in range(len(extra_zeros))]
    first=min(u['t'] for u in units)
    for u in units:u['t']-=first
    return save(H/'cand'/name,units,dets,D,dict(source='15T polynomial plus sixth Clifford flag',synthesis=rec,phase_locations=chosen))

def main():
    results=[];best=1;num=0
    for gamma in [0.,.15,.4]:
        for seed in range(3):
            networks=search(seed,gamma=gamma)
            (H/f'flag6_networks_g{gamma}_s{seed}.json').write_text(json.dumps(networks,indent=2)+'\n')
            for rec in networks[:3]:
                for mode,phseed in [('first',0),('last',0),('random',1),('random',2)]:
                    name=f'flag6_{num:03d}_{mode}{phseed}';r=dict(rec,phase_mode=mode,phase_seed=phseed)
                    try:
                        st=build(r,name);raw=raw_check(st.with_suffix('.qasm').read_text(),D)
                        row=dict(stem=str(st),source_cx=rec['depth'],z_pair_proxy=rec['z_pair_proxy'],raw=raw)
                        if raw['ok']:
                            c1,n=singles(st);row.update(c1=c1,harmful=n)
                            if c1<1e-5:
                                p=price(st,1);row.update(loss=p['loss'],acceptance=p['acceptance'])
                                if p['acceptance']>=.5002 and p['loss']<best:
                                    best=p['loss'];(H/'flag6_best.json').write_text(json.dumps(row,indent=2)+'\n')
                        print(json.dumps(row),flush=True);results.append(row)
                    except Exception as ex:
                        print('ERROR',name,repr(ex),flush=True);results.append(dict(name=name,error=repr(ex)))
                    (H/'flag6_results.json').write_text(json.dumps(results,indent=2)+'\n')
                num+=1

if __name__=='__main__':main()
