"""Alternative nearest-neighbor double-cat trees; all artifacts stay in L5."""
from search_v10 import *

DATA={0,7,8,20,3,15,4}
ANCS={10,9,2,1,14,6}
NODES=DATA|ANCS
EDGES=[(a,b) for a in sorted(NODES) for b in sorted(NODES) if a<b and abs(a//6-b//6)+abs(a%6-b%6)==1]
ORIG={(6,0),(9,3),(14,20),(2,8),(1,7),(10,4),(7,6),(8,14),(9,10),(8,7),(9,15),(8,9)}
ORIG={tuple(sorted(e)) for e in ORIG}

def spanning(rng):
    # Random Kruskal, also biased towards original edges in half the trials.
    groups={q:q for q in NODES};out=[]
    weights={e:rng.random()+(0 if e in ORIG else rng.choice([0,0,0,.3,.6])) for e in EDGES}
    for a,b in sorted(EDGES,key=lambda e:weights[e]):
        x,y=groups[a],groups[b]
        if x==y:continue
        out.append((a,b))
        for q in groups:
            if groups[q]==y:groups[q]=x
    assert len(out)==len(NODES)-1
    return out

def cat_ops(tree,root):
    adj={q:[] for q in NODES}
    for a,b in tree:adj[a].append(b);adj[b].append(a)
    parent={root:None};depth={root:0};queue=[root]
    for q in queue:
        for v in adj[q]:
            if v in parent:continue
            parent[v]=q;depth[v]=depth[q]+1;queue.append(v)
    flags={q for q in ANCS if q!=root and len(adj[q])==1}
    contraction=[]
    for q in sorted(flags):contraction.append(('cx',(q,parent[q]),None))
    for q in sorted(NODES-{root}-flags,key=lambda q:(-depth[q],q)):
        contraction.append(('cx',(parent[q],q),None))
    ops=[('RX',(q,),None) for q in sorted(ANCS)]
    ops += [('g:t',(q,),None) for q in sorted(DATA)]
    ops += contraction+[('MX',(root,),7),('RX',(root,),None)]+list(reversed(contraction))
    ops += [('g:tdg',(q,),None) for q in sorted(DATA)]
    ops += [('MX',(q,),b) for q,b in [(10,8),(9,9),(2,10),(1,11),(14,12),(6,13)]]
    return ops

def generate(count):
    raw,data,orig,ot,npre=base();rng=random.Random(59837)
    seen=set();items=[];attempts=0
    while len(items)<count and attempts<count*100:
        attempts+=1
        tree=sorted(ORIG) if attempts<15 else spanning(rng)
        root=sorted(NODES)[(attempts-1)%len(NODES)] if attempts<15 else rng.choice([8,8,8,9,7,14,3,15])
        key=(tuple(tree),root)
        if key in seen:continue
        seen.add(key)
        pre=orig[:85]+cat_ops(tree,root);ops=pre+orig[npre:];np=len(pre)
        pt=greedy(pre,4,True,True);ct=[t-min(ot[npre:])+max(pt)+1 for t in ot[npre:]]
        times=pt+ct
        label=f'cat_{len(items):03d}_r{root}'
        # First check exact eligibility with a small acceptance sample. Official scores follow.
        qasm=text_for(raw,ops,times)
        rep=tprep.check(qasm,data,shots=1000,seed=0)
        item={'label':label,'root':root,'tree':tree,'depth':max(times)+1,'passed_screen':rep.passed,'screen_report':str(rep)}
        print(json.dumps(item),flush=True)
        if not rep.passed:continue
        save(label,raw,data,ops,times,np,{'change':'alternate double-cat spanning tree','root':root,'tree':tree,'priority_seed':4})
        items.append(item)
    (HERE/'cat_screen.json').write_text(json.dumps(items,indent=2)+'\n')
    (HERE/'cat_manifest.json').write_text(json.dumps([x['label'] for x in sorted(items,key=lambda x:x['depth'])],indent=2)+'\n')
    print(json.dumps({'generated':len(items),'attempts':attempts,'edges':EDGES}),flush=True)

if __name__=='__main__':generate(int(sys.argv[1]) if len(sys.argv)>1 else 60)
