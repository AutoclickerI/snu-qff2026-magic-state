"""Complete all-orders protection menu and conflict-constrained composition."""
from context76 import *
import argparse,gzip,concurrent.futures,multiprocessing
import echo_search,watch_search
p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--out',required=True);p.add_argument('--workers',type=int,default=4);a=p.parse_args();stem=Path(a.stem);base=json.loads(stem.with_suffix('.plan.json').read_text());baseline=json.loads(stem.with_suffix('.allorders.json').read_text());jobs=[];seen=set();basekeys={(o['t'],tuple(o['lines']))for o in base['ops']}
# watch_search rebinds echo_search.candidates; load the echo source independently.
sp=importlib.util.spec_from_file_location('p76_echo',H/'echo_search.py');ec=importlib.util.module_from_spec(sp);sp.loader.exec_module(ec)
for family,gen in [('echo',ec.candidates),('watch',watch_search.candidates)]:
 for c,desc in gen(base):
  c,txt=normalized(c);sha=hashlib.sha256(txt.encode()).hexdigest()
  if sha in seen:continue
  seen.add(sha);name=a.out+f'_m{len(jobs)}';jobs.append(dict(name=name,plan=c,change=desc,family=family))
def price(job):
 name=job['name'];done=OUT/(name+'.allorders.json')
 try:
  if done.exists():r=json.loads(done.read_text())
  else:r=rank(save(job['plan'],'p76/'+name),1)
  return dict(name=name,change=job['change'],family=job['family'],**{k:r[k]for k in('loss','acceptance','c1','seconds','sha256')})
 except Exception as e:return dict(name=name,error=repr(e),change=job['change'],family=job['family'])
results=[];print('MENU',len(jobs),flush=True)
with concurrent.futures.ProcessPoolExecutor(a.workers,mp_context=multiprocessing.get_context('fork'))as pool:
 for rec in pool.map(price,jobs):
  results.append(rec);append_result(rec['name'],rec,'Full all-orders price of physical idle-window echo or known-state readout. No c1 or low-order objective pruning.');print(json.dumps(rec),flush=True)
  with gzip.open(OUT/(a.out+'.menu.jsonl.gz'),'at')as f:f.write(json.dumps(rec)+'\n')
good=[i for i,r in enumerate(results)if r.get('loss',1)<baseline['loss']and r.get('acceptance',0)>=.5002];deltas={}
for i in good:
 job=jobs[i];c=job['plan'];keys={(o['t'],tuple(o['lines']))for o in c['ops']};added=[o for o in c['ops']if(o['t'],tuple(o['lines']))not in basekeys];removed=basekeys-keys;touch={(q,o['t'])for o in added for q in unit(o).qs};desc=job['change']
 if job['family']=='echo':touch|={(desc['helper'],t)for t in range(desc['window'][0],desc['window'][1]+1)}
 newrows=[l for l in c['tail']if l not in base['tail']];deltas[i]=dict(added=added,removed=removed,touch=touch,rows=newrows)
packages=[]
for floor in [.5002,.505,.515]:
 m=cp_model.CpModel();v={i:m.NewBoolVar('m'+str(i))for i in good}
 for j,i in enumerate(good):
  for k in good[j+1:]:
   if deltas[i]['touch']&deltas[k]['touch']or deltas[i]['removed']&deltas[k]['removed']:m.Add(v[i]+v[k]<=1)
 costs={i:round(math.log(baseline['acceptance']/results[i]['acceptance'])*1e9)for i in good};m.Add(sum(costs[i]*v[i]for i in good)<=int(math.log(baseline['acceptance']/floor)*1e9));m.Maximize(sum(round((baseline['loss']-results[i]['loss'])*1e13)*v[i]for i in good));s=cp_model.CpSolver();s.parameters.num_workers=a.workers;s.parameters.max_time_in_seconds=10;st=s.Solve(m)
 if st not in(cp_model.FEASIBLE,cp_model.OPTIMAL):continue
 selected=[i for i in good if s.Value(v[i])];c=copy.deepcopy(base);bit=1+max(int(b)for o in c['ops']for b in re.findall(r'c\[(\d+)\]',' '.join(o['lines'])));chosen=[]
 for i in selected:
  d=deltas[i];oldbit=jobs[i]['change']['bit'];replace=lambda line:re.sub(r'c\['+str(oldbit)+r'\]',f'c[{bit}]',line);c['ops']=[o for o in c['ops']if(o['t'],tuple(o['lines']))not in d['removed']]
  for o in d['added']:o=copy.deepcopy(o);o['lines']=[replace(l)for l in o['lines']];c['ops'].append(o)
  c['tail'] +=[replace(l)for l in d['rows']];desc=dict(jobs[i]['change'],bit=bit);c['meta'].setdefault('echoes'if jobs[i]['family']=='echo'else'watches',[]).append(desc);bit+=1;chosen.append(results[i]['name'])
 c['h']=[re.sub(r'creg c\[\d+\];',f'creg c[{bit}];',l)for l in c['h']];name=a.out+'_p'+str(len(packages));rec=dict(name=name,floor=floor,selected=chosen)
 try:r=rank(save(c,'p76/'+name),a.workers);rec.update(r)
 except Exception as e:rec['error']=repr(e)
 packages.append(rec);append_result(name,rec,'Compatibility-constrained package proposed by measured marginal all-orders gains and log acceptance; whole package repriced. Marginals are not treated as additive evidence.');print('PACKAGE',json.dumps(rec),flush=True)
with gzip.open(OUT/(a.out+'.plans.jsonl.gz'),'wt')as f:
 for job in jobs:f.write(json.dumps(job)+'\n')
(OUT/(a.out+'.receipt.json')).write_text(json.dumps(dict(base=baseline,results=results,packages=packages),indent=2));print('DONE',flush=True)
