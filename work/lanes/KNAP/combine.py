from search import *
import itertools

def apply_recipes(recipes,name):
 c=loadc(OUT/'base');remove=set();checks=[];bit=180
 for r in recipes:
  kind=r['kind'];i=r.get('unit');u=c['u'][i]if i is not None else None;q=u.qs[0]if u else None
  if kind=='drop_detector':c['tail']=[l for l in c['tail']if l!=r['line']]
  elif kind=='measure_init_no_detector':
   c['u'][i]=Unit([f'measure q[{q}] -> c[{bit}];']+([f'h q[{q}];']if u.name=='RX'else []));bit+=1
  elif kind=='measure_to_reset':
   c['u'][i]=Unit([f'reset q[{q}];']+([f'h q[{q}];']if u.name=='MX'and len(u.lines)==3 else []));dropbits(c,r['bits'])
  elif kind=='remove_measurement':remove.add(i);dropbits(c,r['bits'])
  elif kind=='check_rx':checks.append((i,q,bit));bit+=1
  elif kind=='time':c['t'][i]=r['time']
  elif kind=='bc_reset':
   c['u'][i]=Unit([f'reset q[{q}];',f'h q[{q}];'])
   b=r['bit'];tail=[]
   for l in c['tail']:
    if l.startswith('// DETECTOR'):
     bs=[x for x in detbits(l)if x!=b]
     if bs:tail.append('// DETECTOR '+' '.join(f'c[{x}]'for x in bs))
    else:tail.append(l)
   c['tail']=tail
  elif kind=='merge_detectors':
   dets=[l for l in c['tail']if l.startswith('// DETECTOR')];ls=[dets[d]for d in r['detectors']];bs=set()
   for l in ls:bs.symmetric_difference_update(detbits(l))
   c['tail']=[l for l in c['tail']if l not in ls]+['// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(bs))]
  else:raise ValueError(kind)
 for i,q,b in sorted(checks,reverse=True):
  c['u'].insert(i+1,Unit([f'h q[{q}];',f'measure q[{q}] -> c[{b}];',f'h q[{q}];']))
  c['t'].insert(i+1,c['t'][i]+1);c['tags'].insert(i+1,c['tags'][i]);c['tail'].append(f'// DETECTOR c[{b}]')
  remove={j+1 if j>i else j for j in remove}
 delete(c,remove)
 if checks:c.update(retime(c))
 return write(c,name,dict(kind='combination',items=recipes))

def select():
 rows=[json.loads(l)for l in(OUT/'items_results.jsonl').read_text().splitlines()];base=next(r for r in rows if r['stem']=='base');maxA=-math.log(FLOOR)
 # Bound enormous-loss items away only by dominance at the additive proposal stage.
 candidates=[r for r in rows if r['stem']!='base'and'total'in r and r['A0']>.999999 and r['total']-base['total']<2e-6 and (r['A1']<base['A1']-1e-6 or r['total']<base['total']-1e-10)]
 jobs=[];seen=set();proposals=[]
 def emit(chosen,label):
  key=tuple(sorted(r['stem']for r in chosen))
  if key in seen:return
  seen.add(key)
  try:jobs.append(apply_recipes([r['recipe']for r in chosen],label));proposals.append(dict(stem=label,items=key,predicted_loss=base['total']+sum(r['total']-base['total']for r in chosen),predicted_A1=base['A1']+sum(r['A1']-base['A1']for r in chosen)))
  except Exception as e:print(label,'build fail',repr(e),flush=True)
 for budget in [maxA,maxA-.001,maxA-.003,maxA-.006,maxA-.01]:
  for limit in [2,3,5,8,12,20,40]:
   m=cp_model.CpModel();vs=[m.new_bool_var(str(i))for i in range(len(candidates))]
   m.add(sum(vs)<=limit);m.add(sum(round((r['A1']-base['A1'])*1e9)*v for r,v in zip(candidates,vs))<=round((budget-base['A1'])*1e9))
   owned={}
   for k,r in enumerate(candidates):
    rec=r['recipe'];keys=[]
    if 'unit'in rec:keys.append(('unit',rec['unit']))
    if rec['kind']=='drop_detector':keys.extend(('bit',b)for b in detbits(rec['line']))
    if 'bits'in rec:keys.extend(('bit',b)for b in rec['bits'])
    for key in keys:owned.setdefault(key,[]).append(k)
   for ks in owned.values():m.add(sum(vs[k]for k in set(ks))<=1)
   m.minimize(sum(round((r['total']-base['total'])*1e14)*v for r,v in zip(candidates,vs)))
   s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=15;status=s.solve(m)
   if status in(cp_model.OPTIMAL,cp_model.FEASIBLE):emit([r for r,v in zip(candidates,vs)if s.value(v)],f'knap_{len(jobs):03}')
 # Every individual loss-reducing item with the cheap c3 budget and their compatible pairs.
 c3=next(r for r in rows if r['stem']=='drop_d03');gains=[r for r in candidates if r['total']<base['total']-1e-8]
 for r in gains:emit([c3,r],f'fund_{r["stem"]}')
 (OUT/'selection.json').write_text(json.dumps(dict(candidates=candidates,proposals=proposals),indent=2)+'\n')
 (OUT/'combo_manifest.json').write_text(json.dumps(jobs,indent=2)+'\n');print('combos',len(jobs),flush=True)

def merges():
 base=loadc(OUT/'base');dets=[l for l in base['tail']if l.startswith('// DETECTOR')];jobs=[]
 rows=[json.loads(l)for l in(OUT/'items_results.jsonl').read_text().splitlines()];control=rows[0]
 # Only directions having small marginal loss or substantial freed acceptance.
 ds=[r['recipe']['detector']for r in rows if r['recipe']['kind']=='drop_detector'and'total'in r and r['total']-control['total']<1e-6]
 for a,b in itertools.combinations(ds,2):
  jobs.append(apply_recipes([dict(kind='merge_detectors',detectors=[a,b])],f'merge_{a}_{b}'))
 (OUT/'merge_manifest.json').write_text(json.dumps(jobs,indent=2)+'\n');print('merge count',len(jobs))

if __name__=='__main__':globals()[sys.argv[1]]()
