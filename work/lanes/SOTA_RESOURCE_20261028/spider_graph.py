import json,collections
from pathlib import Path
import rustworkx as rx,stim
R=Path.cwd();H=R/'work/lanes/SOTA_RESOURCE_20261028';c=stim.Circuit((R/'work/lanes/SOTA_DETECT_20261028/spider_bc.log').read_text());g=rx.PyGraph();g.add_nodes_from(list(range(20)));edges=collections.Counter()
for ins in c:
 if ins.name=='CX':
  qs=[x.value for x in ins.targets_copy()]
  for a,b in zip(qs[::2],qs[1::2]):edges[tuple(sorted((a,b)))]+=1
for a,b in edges:g.add_edge(a,b,None)
degree={i:g.degree(i) for i in range(20)};r={'nodes':20,'unique_edges':len(edges),'cx':sum(edges.values()),'degree':degree,'maxdegree':max(degree.values()),'bipartite':rx.is_bipartite(g),'planar':rx.is_planar(g),'edges':[dict(a=a,b=b,count=n) for (a,b),n in sorted(edges.items())],'components':[sorted(c) for c in rx.connected_components(g)]}
(H/'spider_graph.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
