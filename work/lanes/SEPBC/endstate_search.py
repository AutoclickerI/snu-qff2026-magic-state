"""Search native-time geometry before emitting a small full-score portfolio."""
from endstate_emit import *
import concurrent.futures
def main():
 p=argparse.ArgumentParser();p.add_argument('endstate');p.add_argument('--prefix',default='v23');p.add_argument('--tag',default='es');p.add_argument('--per-geometry',type=int,default=2);p.add_argument('--route-seeds',type=int,default=2);p.add_argument('--processes',type=int,default=3);p.add_argument('--seconds',type=float,default=3);p.add_argument('--emit',type=int,default=4);p.add_argument('--alap',action='store_true');a=p.parse_args();d=json.loads(Path(a.endstate).read_text());d['source_file']=str(Path(a.endstate).resolve());chs=choices(d,a.prefix);counts=collections.Counter();selected=[]
 for ch in chs:
  key=(ch['prefix_row'],ch['prefix_col'],ch['sym'],ch.get('end_row',0),ch.get('end_col',0))
  if counts[key]>=a.per_geometry:continue
  counts[key]+=1
  for seed in range(a.route_seeds):selected.append((ch,seed))
 def run(job):
  ch,seed=job
  try:
   c,r=build(d,ch,'unused',a.prefix,seed,a.seconds,1,emit=False);return c,r
  except Exception as e:return None,dict(error=repr(e),choice=ch,route_seed=seed)
 rows=[];witnesses=[]
 with concurrent.futures.ThreadPoolExecutor(a.processes)as pool:
  for c,r in pool.map(run,selected):
   rows.append(r)
   if c:witnesses.append((c,r))
 # R is a scheduling search objective, not a fidelity ranking. Full candidates
 # span geometry choices; their eventual ordering uses the full circuit loss.
 witnesses.sort(key=lambda z:(z[1]['R'],z[1]['cx']));keep=[];seen=set()
 for c,r in witnesses:
  key=(r['choice']['sym'],r['choice']['prefix_row'],r['choice']['prefix_col'],r['choice'].get('end_row',0),r['choice'].get('end_col',0))
  if key in seen:continue
  seen.add(key);keep.append((c,r))
  if len(keep)>=a.emit:break
 for j,(c,r)in enumerate(keep):
  name=f'{a.tag}_{a.prefix}_{j}'
  if a.alap:
   adjusted,ret=schedule(c,mode='alap',fixed_round=True,seconds=10)
   assert adjusted is not None,ret
   c=adjusted;r['alap_schedule']=ret
  stem=save(c,name)
  try:r['screen']=score(stem)
  except Exception as e:r['score_error']=repr(e)
  r['stem']=str(stem);stem.with_suffix('.build.json').write_text(json.dumps(r,indent=2));append_result(name,r,'ENDSTATE geometry/lifetime witness; R selected for construction, full loss is the ranking metric.');print(json.dumps(r),flush=True)
 (H/(a.tag+'_'+a.prefix+'.search.json')).write_text(json.dumps(dict(args=vars(a),trials=rows,built=[r for c,r in keep]),indent=2));print('complete',len(rows),'scheduled',len(witnesses),'built',len(keep),flush=True)
if __name__=='__main__':main()
