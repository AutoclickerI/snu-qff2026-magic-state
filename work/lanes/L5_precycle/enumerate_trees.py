"""Enumerate all spanning trees on the original cat footprint, retaining shallow schedules."""
from cat_trees import *
import itertools
raw,data,orig,ot,npre=base();items=[];seen=set();connected=0
for edges in itertools.combinations(EDGES,len(NODES)-1):
    components={q:q for q in NODES}
    for a,b in edges:
        x,y=components[a],components[b]
        if x==y:break
        for q in components:
            if components[q]==y:components[q]=x
    else:
        connected+=1
        for root in (8,7,9,14):
            cat=cat_ops(edges,root)
            cts=greedy(cat,4,True,True)
            if max(cts)+1>12:continue
            pre=orig[:85]+cat;ops=pre+orig[npre:];np=len(pre)
            pt=greedy(pre,4,True,True);ct=[t-min(ot[npre:])+max(pt)+1 for t in ot[npre:]];times=pt+ct
            if max(times)+1>42:continue
            text=text_for(raw,ops,times);h=hashlib.sha256(text.encode()).hexdigest()
            if h in seen:continue
            seen.add(h)
            label=f'enumcat_{len(items):03d}_r{root}'
            save(label,raw,data,ops,times,np,{'change':'Exhaustive original-footprint double-cat spanning tree with depth <=42','root':root,'tree':edges,'priority_seed':4})
            items.append(label)
(HERE/'enumcat_manifest.json').write_text(json.dumps(items,indent=2)+'\n')
print(json.dumps({'connected_trees':connected,'shallow_candidates':len(items),'labels':items}),flush=True)
