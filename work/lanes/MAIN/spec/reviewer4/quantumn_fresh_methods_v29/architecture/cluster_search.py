from graph_search import *
degree_patterns={tuple(sorted(x.bit_count() for x in a)) for a in seqs}
results=[]
for rows,cols,basis_set in [(2,4,'XYZ'),(2,5,'XYZ'),(3,4,'XZ')]:
 n=rows*cols
 grid=graph(n,[(r*cols+c,(r+dr)*cols+c+dc) for r in range(rows) for c in range(cols) for dr,dc in [(1,0),(0,1)] if r+dr<rows and c+dc<cols])
 witnesses=[];checked=0
 for dead in combinations(range(n),n-7):
  for bases in product(basis_set,repeat=n-7):
   a=grid;remain=list(range(n))
   for v,basis in zip(dead,bases):
    pos=remain.index(v);a=measure(a,pos,basis);remain.pop(pos)
   checked+=1
   if tuple(sorted(x.bit_count() for x in a)) not in degree_patterns:continue
   ca,order=canon(a)
   if ca in classes:
    rep,seq,torder=classes[ca]
    witnesses.append(dict(measured=dead,bases=bases,remaining=remain,derived_graph=edges(a),target_lc_sequence=seq,measured_order=order,target_order=torder))
 row=dict(shape=[rows,cols],bases=basis_set,patterns_checked=checked,witnesses=witnesses)
 results.append(row)
 print(json.dumps({**row,'witnesses':len(witnesses)}),flush=True)
Path(__file__).with_suffix('.json').write_text(json.dumps(results,indent=2)+'\n')
