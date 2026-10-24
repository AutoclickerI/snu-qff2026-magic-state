from common import *
from variants import retime
cs=json.loads((HERE/'encoder_candidates.json').read_text());found=[]
for ci,c in enumerate(cs):
 vec=[{p} for p in c['pivots']];gates=[e for L in c['ops'] for e in L];first=next(j for j,e in enumerate(gates) if 15 in e)
 for t in range(first+1):
  span={frozenset()}
  for v in vec:span|={frozenset(set(w)^v) for w in list(span)}
  if t and frozenset({14,9,16}) in span:found.append(dict(encoder=ci,boundary=t,first15=first,pivot15=15 in c['pivots']))
  if t<first:
   u,v=gates[t]
   for x in vec:
    if u in x:x.symmetric_difference_update({v})
(HERE/'internal_star.json').write_text(json.dumps(dict(tested=len(cs),support=[14,9,16],ancilla=15,admissible=found),indent=1))
print('internal star admissible prefixes',len(found),flush=True)
