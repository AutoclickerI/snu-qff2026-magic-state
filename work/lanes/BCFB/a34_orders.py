from a34_prep import *
from a34_dedup import physical_key

def orders(e):
 ops=e['ops'];n=len(ops);pred=[]
 for i,(a,b) in enumerate(ops):pred.append(sum(1<<j for j,(c,d) in enumerate(ops[:i]) if a==d or b==c or (a,b)==(c,d)))
 def rec(mask,seq):
  if len(seq)==n:yield dict(e,name=e['name']+'_commute',ops=[ops[i] for i in seq]);return
  for i in range(n):
   if mask>>i&1 or pred[i]&~mask:continue
   if seq and i<seq[-1] and len(set(ops[i]+ops[seq[-1]]))==4:continue
   yield from rec(mask|1<<i,seq+[i])
 yield from rec(0,[])
seen=set()
for name in ('encoders','checks','joint'):
 for s in json.loads((D/f'{name}.json').read_text())['stems']:seen.add(physical_key(H/s))
stems=[];counts=collections.Counter()
for base in ('encoders_00000','encoders_00013'):
 o=json.loads((D/'candidates'/base).with_suffix('.json').read_text())['options'];e=o['enc']
 for enc in orders(e):
  for checks in ([1,2,9],[],[1,14,8,9,15]):
   counts['attempted']+=1
   try:text,md=prep(enc,checks,o['reuse'])
   except (ValueError,AssertionError) as ex:counts[str(ex)]+=1;continue
   stem=D/'candidates'/f'orders_{len(stems):05}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md,indent=2));key=physical_key(stem)
   if key in seen:stem.with_suffix('.qasm').unlink();stem.with_suffix('.json').unlink();continue
   seen.add(key);stems.append(str(stem.relative_to(H)));counts['generated']+=1
(D/'orders.json').write_text(json.dumps(dict(counts=counts,stems=stems),indent=2));print('DONE',dict(counts),flush=True)
