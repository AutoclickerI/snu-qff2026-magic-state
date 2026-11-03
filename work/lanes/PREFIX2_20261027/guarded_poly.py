"""Flagged native parity arithmetic with intermediate MX time-slice records.

Every non-target parity must carry the sixth coordinate32. When that coordinate
returns to one isolated physical |+> factor, it is measured and reused. Distinct
record parities prevent Z faults in different arithmetic intervals from hiding
by cancelling their final flag. No extra T gates are introduced.
"""
import os,sys,json,random,heapq,math
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import flag6 as f6
from qtools import price
from qtools.validity import raw_check
from search_phase import singles
H=Path(__file__).resolve().parent;GOALS=set(f6.GOALS)

def allowed(row):
    return row==0 or row in GOALS or row&32 and row!=40

def isolated(rows):
    carrying=[i for i,r in enumerate(rows) if r&32]
    return carrying[0] if len(carrying)==1 and rows[carrying[0]]==32 else None

def search(seed=0,beam=1200,maxdepth=75,gamma=.1):
    rng=random.Random(seed);gi={v:i for i,v in enumerate(f6.GOALS)}
    cov=f6.synth.coverage(f6.INIT,gi);full=(1<<15)-1
    # Initial future weights include the real T axes and a tail exposure prior.
    w=[0.]*64
    for r in GOALS:w[r]+=1/3
    for r in range(9,16):w[r]+=4
    front=[(f6.INIT,cov,[],[],tuple(w),0.,cov)];seen={};solutions=[];first=None
    for depth in range(1,maxdepth+1):
        nxt={}
        for rows,cov,path,checks,w,cost,last_clean_cov in front:
            clean=isolated(rows)
            for a,b in f6.EDGES:
                if not rows[a] or not allowed(rows[a]^rows[b]):continue
                nr=list(rows);nr[b]^=nr[a];nr=tuple(nr)
                nc=cov|f6.synth.coverage(nr,gi);pp=path+[(a,b)];cp=list(checks)
                adds=[(rows[q],1/3) for q in range(len(f6.CELLS)) if q not in (a,b)]
                adds += [(rows[a],1/15),(rows[b],1/15),(nr[b],1/15)]
                ww,delta=f6.addweights(w,adds);cc=cost+delta
                ni=isolated(nr);lc=last_clean_cov
                if ni is not None and clean is None:
                    cp.append((depth,ni));lc=nc
                    # Different readout-time syndromes cannot cancel each other.
                    ww=tuple(v if not i&32 else 0. for i,v in enumerate(ww))
                missing=15-nc.bit_count();nz=sum(v!=0 for v in nr)
                good=sum(bool(x[0]) for x in cp)
                safe=all(not r or (r&56).bit_count()%2 for r in nr)
                if not missing and nz==6 and safe and len(cp)>=2:
                    _,dc=f6.addweights(ww,[(r,1.) for r in nr if r])
                    solutions.append(dict(rows=nr,path=pp,depth=depth,goals=f6.GOALS,seed=seed,checkpoints=cp,
                                          z_pair_proxy=cc+dc,gamma=gamma,guarded_arithmetic=True))
                    first=depth if first is None else first
                key=(nr,nc,min(len(cp),2))
                if seen.get(key,math.inf)<=cc+1e-10:continue
                seen[key]=cc
                near=sum(v in {nr[c]^nr[d] for c,d in f6.EDGES} for v in GOALS if not nc>>gi[v]&1)
                dirty=sum(bool(r&32) for r in nr)-1
                score=missing*5+(nz-6)*(.6 if missing else 3)+gamma*cc+.22*dirty-.18*near+rng.random()*.5
                if len(cp)<2:score+=.15*(2-len(cp))
                if key not in nxt or score<nxt[key][0]:nxt[key]=(score,nr,nc,pp,cp,ww,cc,lc)
        front=[(r,c,p,k,w,z,lc) for _,r,c,p,k,w,z,lc in heapq.nsmallest(beam,nxt.values(),key=lambda z:z[0])]
        if depth%5==0:
            lead=front[0] if front else None
            print('guard',seed,gamma,depth,len(front),len(solutions),
                  (15-lead[1].bit_count(),sum(r!=0 for r in lead[0]),len(lead[3]),lead[5]) if lead else None,flush=True)
        if not front or first is not None and depth>=first+3:break
        if len(seen)>800000:seen={(r,c,min(len(k),2)):z for r,c,p,k,w,z,lc in front}
    uniq={tuple(r['path']):r for r in solutions}
    return sorted(uniq.values(),key=lambda r:(r['z_pair_proxy']+.05*r['depth'],r['depth']))[:6]

def main():
    results=[];best=1;num=0
    for gamma in [.05,.2]:
        for seed in range(3):
            networks=search(seed,gamma=gamma)
            (H/f'guarded_network_g{gamma}_s{seed}.json').write_text(json.dumps(networks,indent=2)+'\n')
            for net in networks[:3]:
                for mode,phseed in [('first',0),('last',0),('random',1),('random',2)]:
                    rec=dict(net,phase_mode=mode,phase_seed=phseed)
                    name=f'guarded_{num:03d}_{mode}{phseed}'
                    try:
                        st=f6.build(rec,name);raw=raw_check(st.with_suffix('.qasm').read_text(),f6.D)
                        row=dict(stem=str(st),source_cx=net['depth'],checks=len(net['checkpoints']),proxy=net['z_pair_proxy'],raw=raw)
                        if raw['ok']:
                            c1,n=singles(st);row.update(c1=c1,harmful=n)
                            if c1<1e-5:
                                p=price(st,1);row.update(loss=p['loss'],acceptance=p['acceptance'])
                                if p['acceptance']>=.5002 and p['loss']<best:
                                    best=p['loss'];(H/'guarded_best.json').write_text(json.dumps(row,indent=2)+'\n')
                        print(json.dumps(row),flush=True);results.append(row)
                    except Exception as ex:
                        print('ERROR',name,repr(ex),flush=True);results.append(dict(name=name,error=repr(ex)))
                    (H/'guarded_results.json').write_text(json.dumps(results,indent=2)+'\n')
                num+=1

if __name__=='__main__':main()
