"""Enumerate compatible placements, select full-circuit moments minima per subset, verify references later."""
import os,sys,json,itertools,concurrent.futures,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import tick_build as tb
sys.path.insert(0,str(ROOT/'work/lanes/FRESH'))
import moments,xtim
xtim.cache_dir=str(H/'.xtim_cache')
rows=json.loads((H/'tick_singles.json').read_text());usable=[r for r in rows if r['correct'] and r['gadgets'][0]['logical'] is not None]

def evaluate(job):
 ids,gs=job;name='u_'+'_'.join(ids);p=tb.emit(name,gs)
 try:
  ev=tb.Eval(p.with_suffix('.qasm').read_text(),tb.DATA);out=moments.evaluate(ev)
  out.update(stem=name,ids=ids,subset=sorted(g['logical'] for g in gs),gadgets=gs,z_only=all(g['axis']=='Z' for g in gs),correct=True)
 except Exception as e:out=dict(stem=name,ids=ids,correct=False,error=repr(e))
 (H/(name+'.screen.json')).write_text(json.dumps(out));return out
if __name__=='__main__':
 jobs=[]
 for n in (2,3):
  for xs in itertools.combinations(usable,n):
   gs=[x['gadgets'][0] for x in xs];ls=[g['logical'] for g in gs]
   if len(set(ls))!=n:continue
   if n==3 and not any(set(ls)==set(line) for line in tb.FANO):continue
   if not tb.compatible(gs):continue
   jobs.append(([x['stem'].split('_')[0] for x in xs],gs))
 out=[]
 with concurrent.futures.ProcessPoolExecutor(max_workers=6) as ex:
  for r in ex.map(evaluate,jobs):out.append(r);print(json.dumps({k:r[k] for k in ('stem','correct','total','exp_minus_A1') if k in r}),flush=True)
 (H/'subset_screen.json').write_text(json.dumps(out,indent=2))
 winners={}
 for r in out:
  if not r['correct'] or r['exp_minus_A1']<.5002:continue
  k=','.join(map(str,r['subset']))
  for typ in ('mixed','Z'):
   if typ=='Z' and not r['z_only']:continue
   key=(k,typ)
   if key not in winners or r['total']<winners[key]['total']:winners[key]=r
 wr=[]
 for (k,typ),r in sorted(winners.items()):
  # validate original and inserted operation ticks before reference pricing.
  tb.check(H/r['stem']);wr.append(dict(stem=r['stem'],subset=r['subset'],family=typ,screen_total=r['total'],exp_minus_A1=r['exp_minus_A1'],gadgets=r['gadgets']))
 (H/'subset_winners.json').write_text(json.dumps(wr,indent=2))
 unique={r['stem']:r for r in wr};ranked=sorted(unique.values(),key=lambda x:x['screen_total'])
 (H/'subset_reference.json').write_text(json.dumps(ranked,indent=2))
 print('assignments',len(jobs),'winners',len(wr),'unique references',len(ranked),flush=True)
