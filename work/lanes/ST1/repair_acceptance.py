"""Price physical removal of each complete protection, including its readouts."""
from common import *
import argparse,concurrent.futures,gzip
p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--out',required=True);p.add_argument('--workers',type=int,default=6);p.add_argument('--floor',type=float,default=.5015);a=p.parse_args();base=json.loads(Path(a.stem).with_suffix('.plan.json').read_text());jobs=[]
def references(c,bit):return [l for l in c['tail']if bit in list(map(int,re.findall(r'c\[(\d+)\]',l)))]
for wi,w in enumerate(base['meta'].get('watches',[])):
 if w['family']!='measured_Z_init':continue
 bit=w['bit'];c=copy.deepcopy(base);hits=[o for o in c['ops']if any(f'-> c[{bit}];'in l for l in o['lines'])]
 if len(hits)!=1 or references(c,bit)!=[f'// DETECTOR c[{bit}]']:continue
 q=w['q'];hits[0]['lines']=[f'reset q[{q}];'];hits[0]['tag']='init_repair';c['tail'].remove(f'// DETECTOR c[{bit}]');c['meta']['watches'].pop(wi);jobs.append((a.out+f'_w{wi}',c,dict(family='revert_measured_init',bit=bit,q=q)))
for ei,e in enumerate(base['meta'].get('echoes',[])):
 c=copy.deepcopy(base);q,h,bit=e['q'],e['helper'],e['bit'];edge=(q,h)if e['axis']=='X'else(h,q);cx=[o for o in c['ops']if o.get('tag')=='echo'and unit(o).name=='CX'and S.name_qs(o['lines'][0])[1]==edge];reads=[o for o in c['ops']if any(f'-> c[{bit}];'in l for l in o['lines'])]
 if len(cx)!=2 or len(reads)!=1 or references(c,bit)!=[f'// DETECTOR c[{bit}]']:continue
 first=min(o['t']for o in cx);old=[o for o in c['ops']if h in unit(o).qs and o['t']<first];ini=max(old,key=lambda o:o['t']);initbits=list(map(int,re.findall(r'c\[(\d+)\]',' '.join(ini['lines']))))
 if ini.get('tag')not in('echo','measured_Z_init','init_repair'):continue
 if any(references(c,b)!=[f'// DETECTOR c[{b}]']for b in initbits):continue
 drop={id(o)for o in cx+reads+[ini]};c['ops']=[o for o in c['ops']if id(o)not in drop]
 for b in[bit]+initbits:c['tail'].remove(f'// DETECTOR c[{b}]')
 c['meta']['echoes'].pop(ei);c['meta']['watches']=[w for w in c['meta'].get('watches',[])if w['bit']not in initbits];jobs.append((a.out+f'_e{ei}',c,dict(family='remove_complete_echo',echo=e,removed_init_records=initbits)))
def price(job):
 name,c,desc=job
 try:stem=save(c,name);return dict(stem=str(stem),change=desc,**score(stem))
 except Exception as e:return dict(stem=str(H/name),change=desc,error=repr(e))
results=[]
with concurrent.futures.ProcessPoolExecutor(a.workers)as pool:
 for r in pool.map(price,jobs):results.append(r);append_result(Path(r['stem']).name,r,'Physical acceptance repair; all operations and references of the selected protection removed or restored, complete exact objective recomputed.');print(json.dumps(r),flush=True)
with gzip.open(H/(a.out+'.witnesses.jsonl.gz'),'wt')as z:
 for job,r in zip(jobs,results):z.write(json.dumps(dict(plan=job[1],result=r))+'\n')
good=[r for r in results if r.get('exp_minus_A1',0)>=a.floor and abs(r.get('c1',1))<1e-12 and 'total'in r];best=min(good,key=lambda r:r['total'])if good else None
if best:
 c=json.loads(Path(best['stem']).with_suffix('.plan.json').read_text());st=save(c,a.out+'_best');st.with_suffix('.screen.json').write_text(json.dumps(best,indent=2));print('BEST',json.dumps(best),flush=True)
(H/(a.out+'.receipt.json')).write_text(json.dumps(dict(floor=a.floor,best=best,results=results),indent=2))
