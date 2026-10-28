exec(open('work/lanes/SOTA_RESOURCE_20261028/screen.py').read().split('rows=[]')[0])
import random
rows=json.loads((here/'screen.json').read_text()); pool=[x['index'] for x in rows if x.get('raw',{}).get('ok')]
out=[]
for seed in range(12):
 rng=random.Random(seed);order=pool[:];rng.shuffle(order);removed=[]
 for i in order:
  trial=set(removed+[i]); text=emit([o for j,o in enumerate(ops) if j not in trial],dets)
  try: good=raw_check(text,data)['ok']
  except Exception:good=False
  if good:removed.append(i)
 text=emit([o for j,o in enumerate(ops) if j not in set(removed)],dets)
 p=here/f'joint_{seed}';p.with_suffix('.qasm').write_text(text);p.with_suffix('.json').write_text(json.dumps(spec,indent=2)+'\n')
 row={'seed':seed,'removed':removed,'n':len(removed),'stem':str(p)};out.append(row);print(json.dumps(row),flush=True)
(here/'joint.json').write_text(json.dumps(out,indent=2)+'\n')
