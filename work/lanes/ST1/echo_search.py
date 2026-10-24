"""Exact-objective released-helper search on complete new circuits.

Each candidate adds a physical two-CX identity check inside an idle interval.
The full circuit is scored; compatible checks are composed by measured loss.
"""
from common import *
import argparse,gzip,concurrent.futures,multiprocessing

def candidates(c):
 ops=c['ops'];R=c['meta']['R'];per={q:[o for o in ops if q in unit(o).qs]for q in range(36)};newbit=1+max([int(b)for o in ops for b in re.findall(r'c\[(\d+)\]',' '.join(o['lines']))]+[-1])
 for q,seq in per.items():
  for aa,bb in zip(seq,seq[1:]):
   if unit(aa).name in('MEASURE','MX')or unit(bb).name in('RESET','RX'):continue
   lo=max(aa['t']+1,15);hi=min(bb['t']-1,R-1)
   if hi-lo<3:continue
   for h in range(36):
    if abs(q//6-h//6)+abs(q%6-h%6)!=1:continue
    hs=per[h];busy={o['t']for o in hs};runs=[];start=None
    for t in range(lo,hi+2):
     if t<=hi and t not in busy:
      if start is None:start=t
     elif start is not None:
      if t-start>=4:runs.append((start,t-1))
      start=None
    for left,right in runs:
     prev=[o for o in hs if o['t']<left];nxt=[o for o in hs if o['t']>right]
     if prev and unit(prev[-1]).name not in('MEASURE','MX'):continue
     if nxt and unit(nxt[0]).name not in('RESET','RX'):continue
     windows={(left,right)}
     if right-left>=7:windows|={(left,left+3),(right-3,right),(left,(left+right)//2),((left+right)//2,right)}
     for start,end in sorted(windows):
      for axis in'XZ':
       d=copy.deepcopy(c);edge=f'cx q[{q}],q[{h}];'if axis=='X'else f'cx q[{h}],q[{q}];';init=[f'reset q[{h}];']+([f'h q[{h}];']if axis=='Z'else[]);meas=([f'h q[{h}];']if axis=='Z'else[])+[f'measure q[{h}] -> c[{newbit}];']+([f'h q[{h}];']if axis=='Z'else[])
       for t,lines in[(start,init),(start+1,[edge]),(end-1,[edge]),(end,meas)]:d['ops'].append(dict(t=t,lines=lines,tag='echo'))
       d['h']=[re.sub(r'creg c\[\d+\];',f'creg c[{newbit+1}];',line)for line in d['h']];d['tail'].append(f'// DETECTOR c[{newbit}]');desc=dict(q=q,helper=h,axis=axis,window=[start,end],bit=newbit);d['meta']['echoes']=d['meta'].get('echoes',[])+[desc];yield d,desc

def price(job):
 name,c,desc=job
 try:
  stem=save(c,name);r=score(stem);return dict(stem=str(stem),change=desc,**r)
 except Exception as e:return dict(stem=str(H/name),change=desc,error=repr(e))

def main():
 p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--out',required=True);p.add_argument('--workers',type=int,default=6);p.add_argument('--rounds',type=int,default=8);p.add_argument('--floor',type=float,default=.5002);a=p.parse_args();c=json.loads(Path(a.stem).with_suffix('.plan.json').read_text());baseline=score(Path(a.stem));seen={baseline['sha256']};allrows=[];best=baseline|dict(stem=a.stem)
 for generation in range(a.rounds):
  jobs=[]
  for d,desc in candidates(c):
   d,txt=normalized(d);sha=hashlib.sha256(txt.encode()).hexdigest()
   if sha in seen:continue
   seen.add(sha);name=a.out+f'_g{generation}_{len(jobs)}';jobs.append((name,d,desc))
  print('GENERATION',generation,'CANDIDATES',len(jobs),flush=True);genrows=[]
  with concurrent.futures.ProcessPoolExecutor(a.workers,mp_context=multiprocessing.get_context('fork'))as pool:
   for r in pool.map(price,jobs):
    genrows.append(r);allrows.append(r);append_result(Path(r['stem']).name,r,'Complete native instrument edit in existing slots; full exact third-order score, ideal determinism, c1 and acceptance enforced before composition. Change field specifies the physical operation; no exposure proxy is used to rank.')
    with gzip.open(H/(a.out+'.witnesses.jsonl.gz'),'at')as z:z.write(json.dumps(r)+'\n')
    print(json.dumps(r),flush=True)
  good=[r for r in genrows if r.get('exp_minus_A1',0)>=a.floor and abs(r.get('c1',1))<1e-12 and r.get('total',1)<best['total']-1e-10]
  with gzip.open(H/(a.out+'.plans.jsonl.gz'),'at')as z:
   for name,d,desc in jobs:z.write(json.dumps(dict(name=name,plan=d,change=desc))+'\n')
  if not good:
   for name,d,desc in jobs:
    for ext in('.qasm','.json','.plan.json','.screen.json'):(H/(name+ext)).unlink(missing_ok=True)
   break
  best=min(good,key=lambda r:r['total']);c=json.loads(Path(best['stem']).with_suffix('.plan.json').read_text());out=save(c,a.out+'_best');out.with_suffix('.screen.json').write_text(json.dumps(best,indent=2));print('BEST',json.dumps(best),flush=True)
  (H/(a.out+'.receipt.json')).write_text(json.dumps(dict(best=best,generation=generation,evaluations=len(allrows)),indent=2))
  # Every nonfinal circuit remains reconstructible from the input and change list.
  for name,d,desc in jobs:
   if str(H/name)==best['stem']:continue
   for ext in('.qasm','.json','.plan.json','.screen.json'):(H/(name+ext)).unlink(missing_ok=True)
 print('DONE',json.dumps(best),flush=True);append_result(a.out+':completed',dict(best=best,evaluations=len(allrows)),'Measured greedy exact-loss composition over the enumerated released-helper windows; not a global optimum.')
if __name__=='__main__':main()
