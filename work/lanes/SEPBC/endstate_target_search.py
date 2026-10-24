"""All code automorphisms on geometries with the strongest scheduling bounds."""
from endstate_emit import *
import concurrent.futures
p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('bounds');p.add_argument('--tag',required=True);p.add_argument('--prefix',default='v29');p.add_argument('--processes',type=int,default=4);p.add_argument('--emit',type=int,default=2);a=p.parse_args();d=json.loads(Path(a.source).read_text());d['source_file']=str(Path(a.source).resolve());bd=json.loads(Path(a.bounds).read_text());minimum=bd['minimum_R_lower_bound'];key=lambda c:(c['prefix_row'],c['prefix_col'],c['sym'],c.get('end_row',0),c.get('end_col',0));geoms={key(r['choice'])for r in bd['rows']if r['R_lower_bound']<=minimum};jobs=[(c,s)for c in choices(d,a.prefix)if key(c)in geoms for s in range(2)];print('jobs',len(jobs),'geometries',len(geoms),flush=True)
def run(job):
 ch,seed=job
 try:return build(d,ch,'unused',a.prefix,seed,1,1,emit=False)
 except Exception as e:return None,dict(error=repr(e),choice=ch,route_seed=seed)
rows=[];best=[]
with concurrent.futures.ThreadPoolExecutor(a.processes)as pool:
 for c,r in pool.map(run,jobs):
  rows.append(r)
  if c:best.append((c,r))
best.sort(key=lambda z:(z[1]['R'],z[1]['cx']));selected=[];seen=set()
for c,r in best:
 k=key(r['choice'])
 if k in seen:continue
 seen.add(k);selected.append((c,r))
 if len(selected)>=a.emit:break
for j,(c,r)in enumerate(selected):
 c,ret=schedule(c,mode='alap',fixed_round=True);assert c is not None,ret;name=a.tag+f'_{j}';stem=save(c,name);r['screen']=score(stem);r['alap_schedule']=ret;r['stem']=str(stem);stem.with_suffix('.build.json').write_text(json.dumps(r,indent=2));append_result(name,r,'All 168 automorphisms and two routes on minimum-bound geometries; full score ranks emitted circuits.');print(json.dumps(r),flush=True)
(H/(a.tag+'.search.json')).write_text(json.dumps(dict(args=vars(a),trials=rows,built=[r for c,r in selected]),indent=2));print('DONE',len(rows),flush=True)
