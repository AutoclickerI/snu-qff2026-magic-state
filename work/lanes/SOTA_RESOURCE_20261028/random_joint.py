exec(open('work/lanes/SOTA_RESOURCE_20261028/screen.py').read().split('rows=[]')[0])
import random
rows=json.loads((here/'screen.json').read_text());pool=[x['index'] for x in rows if x.get('raw',{}).get('ok')]
for seed in range(8):
 rng=random.Random(1999+seed);rem=[i for i in pool if rng.random() < [0.25,0.50,0.75,1][seed%4]]
 text=emit([o for i,o in enumerate(ops) if i not in set(rem)],dets);raw=raw_check(text,data)
 if not raw['ok']:continue
 p=here/f'random_{seed}';p.with_suffix('.qasm').write_text(text);p.with_suffix('.json').write_text(json.dumps(spec,indent=2)+'\n');p.with_suffix('.removed.json').write_text(json.dumps(rem))
 print(seed,len(rem),flush=True)
