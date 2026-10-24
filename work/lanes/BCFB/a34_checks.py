from a34_prep import *
from a34_dedup import physical_key
encs=[];seen=set()
for s in json.loads((D/'encoders.json').read_text())['stems']:
 e=json.loads((H/s).with_suffix('.json').read_text())['options']['enc'];key=json.dumps([sorted(e['pivots']),e['ops']])
 if key not in seen:seen.add(key);encs.append(e)
print('encoders',len(encs),flush=True)
counts=collections.Counter();seen={physical_key(H/s) for s in json.loads((D/'encoders.json').read_text())['stems']};stems=[]
for e in encs:
 for reuse in ([],[14]):
  for m in range(128):
   checks=[q for i,q in enumerate(A) if m>>i&1];counts['attempted']+=1
   try:text,md=prep(e,checks,reuse)
   except (ValueError,AssertionError) as ex:counts[str(ex)]+=1;continue
   stem=D/'candidates'/f'checks_{len(stems):05}';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md,indent=2));key=physical_key(stem)
   if key in seen:stem.with_suffix('.qasm').unlink();stem.with_suffix('.json').unlink();continue
   seen.add(key);counts['generated']+=1;stems.append(str(stem.relative_to(H)))
(D/'checks.json').write_text(json.dumps(dict(counts=counts,stems=stems),indent=2));print('DONE',dict(counts),flush=True)
