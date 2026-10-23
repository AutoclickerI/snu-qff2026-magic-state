from cycles import *
r=json.loads((HERE/'cycle_0058.json').read_text());m=Cycle(r['layout'],r['leaves'],r['orient']);ref=m.reference_seed()
diff=[dict(node=i,tag=m.tags[i],operation=m.nodes[i],from_step=a,to_step=b) for i,(a,b) in enumerate(zip(ref,r['times'])) if a!=b]
(HERE/'winning_changes.json').write_text(json.dumps(diff,indent=2));print(diff)
