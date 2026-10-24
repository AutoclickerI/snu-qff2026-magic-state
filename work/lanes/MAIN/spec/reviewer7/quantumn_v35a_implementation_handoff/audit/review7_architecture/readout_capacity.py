"""Bounded CSS readout capacity, not a no-go theorem for general instruments.

The three A Z-syndrome rows have all seven nonzero GF(2)^3 columns. An A
wire can be measured in X while retaining all three Z syndromes only when
its transformed column is zero. A CX(c,t) changes column c by XOR column t.
Enumerate arbitrary CNOT networks through three gates, even without grid
restrictions. Two zero columns require at least four gates. Separately,
if the first decoder layer has at most one gate and the second is a
matching, at most one column can vanish. This models the fixed current
A-preparation boundary, not alternatives that retime or resynthesize it.
"""
import itertools,json
from pathlib import Path
initial=tuple(range(1,8))
levels=[{initial}]
rows=[]
for depth in range(4):
 states=levels[depth]
 rows.append(dict(gates=depth,states=len(states),max_zero_columns=max(s.count(0)for s in states)))
 if depth<3:
  nxt=set()
  for state in states:
   for c,t in itertools.permutations(range(7),2):
    a=list(state);a[c]^=a[t];nxt.add(tuple(a))
  levels.append(nxt)
assert [r['max_zero_columns']for r in rows]==[0,0,1,1]

def matchings(vertices):
 if not vertices:
  yield []
  return
 a=vertices[0]
 for m in matchings(vertices[1:]):yield m
 for b in vertices[1:]:
  rest=[v for v in vertices if v not in[a,b]]
  for m in matchings(rest):
   yield [(a,b)]+m;yield [(b,a)]+m

maximum=0;checked=0
for first in [None]+list(itertools.permutations(range(7),2)):
 state=list(initial)
 if first:state[first[0]]^=state[first[1]]
 for matching in matchings(list(range(7))):
  final=state.copy()
  for c,t in matching:final[c]^=state[t]
  maximum=max(maximum,final.count(0));checked+=1
assert maximum==1
out=dict(scope=__doc__,arbitrary_cnot_networks=rows,
         one_CX_then_matching=dict(exhaustive_cases=checked,max_new_X_readouts=maximum),
         consequence='A second new independent X readout needs a changed preparation/extraction boundary, a different instrument, or extra latency; appending more disjoint last-layer A CNOTs cannot produce it.')
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
