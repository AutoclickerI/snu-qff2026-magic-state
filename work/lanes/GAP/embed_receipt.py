import json,re
from pathlib import Path

def odd_cycle(nodes,edges):
 g={q:[] for q in nodes}
 for a,b in edges:g[a].append(b);g[b].append(a)
 col={}
 for root in nodes:
  if root in col:continue
  col[root]=0; parent={root:None}; stack=[root]
  while stack:
   u=stack.pop()
   for v in g[u]:
    if v not in col: col[v]=col[u]^1;parent[v]=u;stack.append(v)
    elif col[v]==col[u]:
     pu=[]; x=u
     while x is not None: pu.append(x); x=parent[x]
     pv=[]; y=v
     while y is not None: pv.append(y); y=parent[y]
     su=set(pu); lca=next(z for z in pv if z in su)
     path=pu[:pu.index(lca)+1] + list(reversed(pv[:pv.index(lca)]))
     return path+[u]
 return None

rows=[]
for path in [Path('work/lanes/MAIN/gf/sep33.qasm'),Path('work/lanes/MAIN/gf/ver33g4.qasm'),Path('work/lanes/ARCH/hybridPZ4.qasm'),Path('work/lanes/ARCH/dummy_checked.qasm'),Path('work/lanes/GAP/merged3_r39.qasm')]:
 edges=set();nodes=set()
 for line in path.read_text().splitlines():
  m=re.match(r'cx q\[(\d+)\],q\[(\d+)\];',line.strip())
  if m:
   a,b=map(int,m.groups());nodes|={a,b};edges.add(tuple(sorted((a,b))))
 cyc=odd_cycle(sorted(nodes),sorted(edges))
 rows.append({'circuit':str(path),'logical_qubits':len(nodes),'cx_edges':len(edges),'grid_static_embedding':'infeasible' if cyc else 'not_proved','odd_cycle_example':cyc})
Path('work/lanes/GAP/embed_receipt.json').write_text(json.dumps(rows,indent=2)+'\n')
