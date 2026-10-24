"""Protection population with an exact all-orders acceptance prefilter."""
import sys,json,random,itertools
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import acceptance as a,protection_budget as pb

def external_guard():
 st=a.H.parents[2]/'work/lanes/SEPBC/v31/guard_joint_2';c=a.d.normalize(a.C.read(st));desc=dict(family='external_guard_seed',source=str(st),budget_screen=True)
 yield 'guard_base',c,desc
 # Single new windows and shared-helper checks retain the three verified guards.
 candidates=list(pb.all_free(c))+list(pb.all_free(c,reuse=True));seen=set()
 for x,r in candidates:
  fp=a.d.digest(x)
  if fp in seen:continue
  seen.add(fp);yield 'guard_'+fp,x,dict(r,parent='guard_base',budget_screen=True)
 # Existing ST2 windows that may straddle commuting guards are priced too.
 for e in a.ECHO:
  x,rec=pb.add_compatible(c,e)
  if x is not None:
   fp=a.d.digest(x)
   if fp not in seen:seen.add(fp);yield 'guard_cross_'+fp,x,dict(family='verified_echo_cross',echo=rec,budget_screen=True,parent='guard_base')

def prepared():
 jobs=json.loads((a.OUT/'prepared/queue.json').read_text())
 for st,r in jobs:
  p=Path(st)
  # Keep structural seeds and full/one-drop compositions; the newly verified
  # guard seed dominates spending most resources on obsolete two-drop sets.
  if r.get('family')=='protection_seed_cross'and len(r.get('drop',[]))>1:continue
  yield p.name,a.C.read(p),dict(r,budget_screen=True)

def beam(stems,generations,workers,label):
 rng=random.Random(32032);seeds=[]
 for i,st in enumerate(stems):seeds.append((f'seed{i}',a.C.read(st),dict(family='beam_seed',source=st,budget_screen=True)))
 rr=a.batch(seeds,label+'_seed',workers);seen=set();circs={};scores={}
 for r in rr:
  if r.get('loss') is not None:circs[r['stem']]=a.C.read(a.H/r['stem']);scores[r['stem']]=r;seen.add(a.d.digest(circs[r['stem']]))
 beam=list(circs)
 for gen in range(generations):
  jobs=[]
  for parent in beam:
   c=circs[parent]
   opts=list(pb.all_free(c))+list(pb.all_free(c,reuse=True))
   for x,desc in opts:
    fp=a.d.digest(x)
    if fp in seen:continue
    seen.add(fp);jobs.append((f'g{gen}_{fp}',x,dict(desc,parent=parent,budget_screen=True)))
  rnew=a.batch(jobs,label+f'_g{gen}',workers)
  for r in rnew:
   if r.get('loss')is not None and r.get('eligible'):circs[r['stem']]=a.C.read(a.H/r['stem']);scores[r['stem']]=r
  good=sorted(scores.values(),key=lambda r:r['loss']);best=good[:2]
  # Preserve one high-acceptance intermediate so it can buy a larger next check.
  rest=[r for r in good[2:] if r['acceptance']>best[0]['acceptance']+.001]
  if rest:best.append(min(rest,key=lambda r:r['loss']))
  beam=[r['stem']for r in best]
  (a.OUT/(label+f'_generation{gen}.json')).write_text(json.dumps(dict(best=good[:10],selected=beam,evaluations=len(rnew)),indent=2));print('BEST',gen,good[0]['stem'],good[0]['loss'],flush=True)
  if not jobs:break
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('mode');p.add_argument('--workers',type=int,default=14);p.add_argument('--generations',type=int,default=3);p.add_argument('--label',default='beam');p.add_argument('stems',nargs='*');args=p.parse_args()
 if args.mode=='guard':a.batch(external_guard(),'guard_cross',args.workers)
 elif args.mode=='prepared':a.batch(prepared(),'prepared_rank',args.workers)
 elif args.mode=='beam':beam(args.stems,args.generations,args.workers,args.label)
