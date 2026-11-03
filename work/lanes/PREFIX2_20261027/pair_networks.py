"""Joint native encoder/phase synthesis with a Z-fault pair objective.

Tracks parity-error weights, penalizing complementary histories r and r^logical.
Unlike the first experiment, every initial plus seed must be in the same affine
hyperplane as the fifteen rotations, and solutions are retained beyond the first
minimum-CX witness. The proxy is screened with full single-fault signatures and
ranked by the all-orders evaluator.
"""
import os,sys,json,random,heapq,time,math
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
sys.path.insert(0,str(H.parent/'PREFIX20261027'))
import synth
from search_phase import singles
from qtools import price
synth.HERE=H
(H/'cand').mkdir(exist_ok=True)

def addweights(w,adds):
 nw=list(w);value=0.
 # Normalized p=1 weights; logical complement 8.
 for r,a in adds:
  if r and a:
   value+=a*nw[r^8];nw[r]+=a
 return tuple(nw),value

def search(seed=0,beam=800,maxdepth=44,gamma=.15,extra=5):
 rng=random.Random(seed);goals=synth.goals(24);gi={v:i for i,v in enumerate(goals)};full=(1<<15)-1
 w=[0.]*32
 for r in goals:w[r]+=1/3
 for r in range(9,16):w[r]+=4.
 rows=synth.INIT;cov=synth.coverage(rows,gi)
 front=[(rows,cov,[],tuple(w),0.)];seen={(rows,cov):0.};found=[];first=None
 for depth in range(1,maxdepth+1):
  nxt=[]
  for rows,cov,path,w,cost in front:
   for (a,b),rr in synth.neighbors(rows):
    nc=cov|synth.coverage(rr,gi);key=(rr,nc)
    adds=[(rows[i],1/3) for i in range(len(rows)) if i not in (a,b)]
    adds += [(rows[a],1/15),(rows[b],1/15),(rr[b],1/15)]
    ww,delta=addweights(w,adds);cc=cost+delta
    # Keep a little state diversity: comparing only total cost can exclude a
    # higher current cost whose future complementary exposure is lower.
    old=seen.get(key,math.inf)
    if cc>=old-1e-9:continue
    seen[key]=cc
    pp=path+[(a,b)];missing=15-nc.bit_count();nz=sum(v!=0 for v in rr)
    if not missing and nz==5 and all(not v or v in gi for v in rr):
     wf,dc=addweights(ww,[(v,1.) for v in rr if v]);val=cc+dc
     rec=dict(seed=seed,functional=24,rows=list(rr),path=pp,depth=depth,goals=goals,z_pair_proxy=val,gamma=gamma)
     found.append(rec);first=depth if first is None else first
     # Can continue past the first solution; additional physical operations may
     # produce a less damaging product preparation.
    present=set(rr);xor2={rr[a]^rr[b] for a,b in synth.EDGES}
    near=sum(v in xor2 for v in goals if not(nc>>gi[v]&1))
    unsafe=sum(v!=0 and v not in gi for v in rr)
    score=missing*5.0+(nz-5)*(.7 if missing else 3.)+gamma*cc+unsafe*.15-near*.15+rng.random()*.2
    nxt.append((score,rr,nc,pp,ww,cc))
  front=[(r,m,p,w,c) for _,r,m,p,w,c in heapq.nsmallest(beam,nxt,key=lambda z:z[0])]
  if depth%5==0:
   x=front[0] if front else None
   print('beam',seed,gamma,depth,'front',len(front),'found',len(found),'lead',(15-x[1].bit_count(),sum(v!=0 for v in x[0]),x[4]) if x else None,flush=True)
  if not front or first is not None and depth>=first+extra:break
  if len(seen)>1000000:seen={(r,m):c for r,m,p,w,c in front}
 # Distinct circuit paths, ordered by pair cost with a weak length tie-break.
 found.sort(key=lambda r:(r['z_pair_proxy'],r['depth']))
 return found[:8]

def run():
 results=[];best=1.;idx=0
 for gamma in [.05,.12,.25,.5]:
  for seed in range(2):
   recs=search(seed,beam=550,gamma=gamma)
   (H/f'networks_g{gamma}_s{seed}.json').write_text(json.dumps(recs,indent=2))
   for r in recs[:5]:
    for mode in ['first','last']:
     rec=dict(r,phase_mode=mode,phase_seed=0,alap_init=True,pull_suffix=True)
     name=f'pairnet_{idx:03d}_{mode}';st=synth.build(rec,name)
     try:
      c1,n=singles(st);ans=dict(stem=str(st),c1=c1,harmful=n,z_pair_proxy=r['z_pair_proxy'],source_cx=r['depth'])
      if c1<1e-5:
       p=price(st,1);ans.update(loss=p['loss'],acceptance=p['acceptance'])
       if p['loss']<best:
        best=p['loss'];(H/'pairnet_best.json').write_text(json.dumps(ans,indent=2))
      print(json.dumps(ans),flush=True);results.append(ans);(H/'pairnet_results.json').write_text(json.dumps(results,indent=2))
     except Exception as ex:print('ERROR',name,repr(ex),flush=True)
    idx+=1
if __name__=='__main__':run()
