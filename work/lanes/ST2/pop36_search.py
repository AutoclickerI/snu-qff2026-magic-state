"""Island population using exact all-orders fitness, never a truncated proxy."""
import os,sys,json,random,time,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import pop36_support as v,pop36_moves as moves
from concurrent.futures import ProcessPoolExecutor,as_completed

def gate_best(row):
 if row['loss']>=v.INCUMBENT-1e-12:return
 import pop36_finalize
 try:pop36_finalize.gate(v.H/row['stem'])
 except Exception as e:print('GATE_ERROR',row['stem'],repr(e),flush=True)

def run(label,workers,seed):
 out=v.OUT/label;out.mkdir(exist_ok=True);rng=random.Random(seed);cache={};circs={};seen=set();trace=[]
 for p in v.OUT.glob('*/*.score.json'):
  r=json.loads(p.read_text())
  if not r.get('eligible')or'loss'not in r:continue
  st=v.H/r['stem'];c=v.C.read(st);fp=v.d.digest(c)
  if fp in seen:continue
  seen.add(fp);cache[fp]=r;circs[fp]=c
 assert cache,'no eligible seed'
 def selection(keys):
  rr=sorted(keys,key=lambda x:(round(cache[x]['loss'],12),-cache[x]['acceptance']));chosen=rr[:3]
  # Choose acceptance alternatives at measured guard/gadget exchange rates,
  # rather than letting destructive high-acceptance circuits occupy the beam.
  for price in [1e-5,3e-5,1e-4]:
   ranked=sorted(keys,key=lambda x:cache[x]['loss']-price*cache[x]['acceptance'])
   for fp in ranked:
    if fp not in chosen:chosen.append(fp);break
  rest=[x for x in rr if x not in chosen];rng.shuffle(rest);return chosen+rest[:2]
 population=selection(list(cache));best=min(cache[x]['loss']for x in population);stagnant=0;gen=0
 gate_best(cache[min(population,key=lambda x:cache[x]['loss'])])
 while stagnant<2:
  pending=[];reject=[];attempts=collections.Counter();accepted=collections.Counter()
  # Every family gets attempts each generation; later parents include high
  # acceptance and worse loss alternatives for interacting trades.
  for fam in moves.FAMILIES:
   target=3 if fam in ('timing','commute','init','guard_window','guard_exchange','menu','seed_edit')else 2
   for trial in range(30):
    if accepted[fam]>=target:break
    attempts[fam]+=1;parent=rng.choice(population[:3]if rng.random()<.6 else population)
    try:
     c,desc=moves.mutate(circs[parent],rng,fam)
     if c is None:continue
     c=v.d.normalize(c)
     if rng.random()<.15:
      cc,dd=moves.mutate(c,rng,rng.choice(['init','guard_window','menu']))
      if cc is not None:c=v.d.normalize(cc);desc=dict(family='double',moves=[desc,dd])
     fp=v.d.digest(c)
     if fp in seen:continue
     seen.add(fp);st=out/f'g{gen:02}_{fp}';v.d.save(c,st);circs[fp]=c;pending.append((fp,str(st),dict(desc,parent=parent,generation=gen,budget_screen=True)));accepted[fam]+=1
    except Exception as e:reject.append(dict(family=fam,error=repr(e)))
  (out/f'jobs_{gen:02}.json').write_text(json.dumps([dict(stem=str(Path(st).relative_to(v.H)),description=desc)for fp,st,desc in pending],indent=2))
  print('GEN',gen,'children',len(pending),'best',best,'families',dict(accepted),flush=True)
  if not pending:break
  import datetime
  expanded=datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime(2026,10,24,17,20,tzinfo=datetime.timezone.utc)
  allowance=15 if expanded else workers
  active_workers=allowance if os.getloadavg()[0]+max(0,allowance-workers)<os.cpu_count()else workers
  print('WORKERS',active_workers,flush=True)
  with ProcessPoolExecutor(active_workers)as pool:
   fs={pool.submit(v.a.score,(st,desc)):fp for fp,st,desc in pending}
   for f in as_completed(fs):
    fp=fs[f];r=f.result();cache[fp]=r;trace.append(r)
    print('RESULT',r['stem'],r.get('loss'),r.get('acceptance'),r.get('error'),flush=True)
  eligible=[fp for fp,r in cache.items()if r.get('eligible')and'loss'in r];population=selection(eligible);newbest=min(cache[x]['loss']for x in population)
  improvement=best-newbest;stagnant=0 if improvement>1e-12 else stagnant+1;best=min(best,newbest)
  summary=dict(generation=gen,best=cache[min(eligible,key=lambda x:cache[x]['loss'])],improvement=improvement,stagnant=stagnant,ranked=sorted([cache[x]for x in eligible],key=lambda r:r['loss']),population=population,rejections=reject,attempts=dict(attempts),families=dict(accepted))
  (out/f'generation_{gen:02}.json').write_text(json.dumps(summary,indent=2));(out/'summary.json').write_text(json.dumps(summary,indent=2));print('BEST',gen,summary['best']['stem'],best,'improvement',improvement,'stagnant',stagnant,flush=True);gen+=1
  if improvement>1e-12:gate_best(summary['best'])
  # Persist measured improvements as crossover moves for both islands.
  import pop36_refresh
  pop36_refresh.refresh()
 print('DONE',label,'generations',gen,'best',best,flush=True)
if __name__=='__main__':run(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]))
