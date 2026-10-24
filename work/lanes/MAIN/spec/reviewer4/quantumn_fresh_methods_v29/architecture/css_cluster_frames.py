"""Exact CSS-state and symbolic-sign search on a 3x4 CNOT resource.

Initial black sites |+>, white sites |0>. One CX black->white per grid edge.
Five single-site X/Z measurements; keep seven. Track all symbolic outcomes
to test whether remaining Steane |0_L> has only Z byproducts, or additionally
a known logical X. Such byproducts are usable for a B ancilla without arbitrary
physical Pauli feed-forward. No noisy score or grid attachment is claimed.
"""
from itertools import combinations, product
from pathlib import Path
import json

def span(rows):
 out=[(0,0)]
 for v,s in rows:out+=[(w^v,t^s) for w,t in out]
 return out

def eliminate(rows,q):
 rows=list(rows);i=next((i for i,(v,s) in enumerate(rows) if v>>q&1),None)
 if i is None:return rows,None
 pivot=rows.pop(i);v,s=pivot
 return [(w^v,t^s) if w>>q&1 else (w,t) for w,t in rows],pivot

R,C=3,4;n=R*C
edges=[(r*C+c,(r+dr)*C+c+dc) for r in range(R) for c in range(C) for dr,dc in [(1,0),(0,1)] if r+dr<R and c+dc<C]
black=[q for q in range(n) if sum(divmod(q,C))%2==0]
white=[q for q in range(n) if q not in black]
neighbors={q:[v if u==q else u for u,v in edges if q in (u,v)] for q in range(n)}
initX=[(sum(1<<i for i in [q]+neighbors[q]),0) for q in black]
initZ=[(sum(1<<i for i in [q]+neighbors[q]),0) for q in white]
results=[];general=0;checked=0;general_rows=[]
for dead in combinations(range(n),5):
 for bases in product('XZ',repeat=5):
  xs,zs=initX,initZ
  for k,(q,P) in enumerate(zip(dead,bases)):
   if P=='X':
    zs,anti=eliminate(zs,q)
    if anti is not None:xs=xs+[(1<<q,1<<k)]
    xs,removed=eliminate(xs,q)
    assert removed is not None
   else:
    xs,anti=eliminate(xs,q)
    if anti is not None:zs=zs+[(1<<q,1<<k)]
    zs,removed=eliminate(zs,q)
    assert removed is not None
  checked+=1
  if len(xs)!=3 or len(zs)!=4:continue
  xx,zz=span(xs),span(zs)
  if any(v.bit_count()!=4 for v,s in xx if v):continue
  general+=1
  remaining=[q for q in range(n) if q not in dead]
  corrections=[];correction_ok=True
  for k,q in enumerate(dead):
   correction_checks=[(v,s) for v,s in zz if v.bit_count()==4]
   desired=[(s>>k)&1 for v,s in correction_checks]
   candidates=[]
   available=[r for r in neighbors[q] if r in remaining]
   for bits in range(1<<len(available)):
    xm=sum(1<<r for i,r in enumerate(available) if bits>>i&1)
    if [((v&xm).bit_count()%2) for v,s in correction_checks]==desired:candidates.append(xm)
   if not candidates:
    correction_ok=False;break
   best=min(candidates,key=int.bit_count)
   if best and bases[k]!='Z':raise AssertionError('Unexpected X-readout controls X correction')
   corrections +=[(q,r) for r in remaining if best>>r&1]
  general_rows.append(dict(measured=dead,bases=bases,remaining=remaining,x_generators=xs,z_generators=zs,
   direct_corrections_possible=correction_ok,direct_correction_CXs=corrections if correction_ok else None))
  if any(s for v,s in zz if v.bit_count()==4):continue
  kind='only_Z_byproducts' if all(s==0 for v,s in zz) else 'Z_and_known_logical_X'
  # Choose any logical Z representative to read the known logical-X branch.
  logical=next((v,s) for v,s in zz if v.bit_count()%2)
  results.append(dict(measured=dead,bases=bases,remaining=remaining,kind=kind,
                      x_generators=xs,z_generators=zs,logical_X_frame_expression=logical[1]))
out=dict(resource_CX=len(edges),resource_X_initializations=black,resource_Z_initializations=white,
 patterns_checked=checked,Steane_state_patterns=general,branch_safe_patterns=len(results),witnesses=results,
 coherent_correction_witnesses=[r for r in general_rows if r['direct_corrections_possible']])
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({**out,'witnesses':results[:3],'coherent_correction_witnesses':out['coherent_correction_witnesses'][:1],
 'coherent_correction_witness_count':len(out['coherent_correction_witnesses'])},indent=2))
