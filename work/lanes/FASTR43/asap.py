from fr import *
def asap(ops):
    ops=sorted(ops,key=lambda o:o.time);prev={};E={}
    for i,o in enumerate(ops):
        E[i]=max([E[prev[q]]+1 for q in o.qs if q in prev]+[0])
        for q in o.qs: prev[q]=i
    return ops,E
def depth(ops): return max(asap(ops)[1].values())+1
ops,dets,md=load(V36F)
P=pairs_of(ops);pid={id(x) for p in P for x in p}
sk=[o for o in ops if id(o) not in pid]
print('full',depth(ops),'no pairs',depth(sk),'pairs',len(P))
def drop(ops,items):
    o2=list(ops)
    for k,qs,t in items:
        o2=[o for o in o2 if not (o.kind==k and o.qs==tuple(qs) and o.time==t)]
    return o2
for name,items in [('M15',[('M',(15,),39)]),('M9',[('M',(9,),37)]),('M15+M9',[('M',(15,),39),('M',(9,),37)]),
                   ('M15+M9+M8+M16',[('M',(15,),39),('M',(9,),37),('M',(8,),35),('M',(16,),37)]),
                   ('RX8@22',[('RX',(8,),22)])]:
    print(name,depth(drop(sk,items)))
# critical chain in skeleton
o,E=asap(sk)

def chains(ops,limit=3):
    ops=sorted(ops,key=lambda o:o.time);prev={};E={};par={}
    for i,o in enumerate(ops):
        cands=[(E[prev[q]]+1,prev[q]) for q in o.qs if q in prev]
        E[i]=max([c[0] for c in cands]+[0]); par[i]=[c[1] for c in cands if c[0]==E[i]]
        for q in o.qs: prev[q]=i
    D=max(E.values())
    ends=[i for i in E if E[i]==D]
    # collect set of ops on any longest path
    crit=set();stack=list(ends)
    while stack:
        i=stack.pop()
        if i in crit: continue
        crit.add(i); stack.extend(par[i])
    return ops,E,crit
import sys
items=[('M',(15,),39),('M',(9,),37),('M',(8,),35),('M',(16,),37)]
o,E,crit=chains(drop(sk,items))
for t in range(0,47):
    row=[o[i] for i in crit if E[i]==t]
    print(t,' '.join(f"{x.kind}{'/'.join(map(str,x.qs))}@{x.time}" for x in row))
