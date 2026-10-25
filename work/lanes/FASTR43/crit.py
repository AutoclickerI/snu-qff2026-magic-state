from fr import *
import sys
stem=sys.argv[1] if len(sys.argv)>1 else str(V36F)
ops,dets,md=load(stem)
ops=sorted(ops,key=lambda o:o.time)
prev={};E={}
for i,o in enumerate(ops):
    E[i]=max([E[prev[q]]+1 for q in o.qs if q in prev]+[0]); 
    for q in o.qs: prev[q]=i
end=max(o.time for o in ops)
nxt={};L={}
for i in range(len(ops)-1,-1,-1):
    o=ops[i]
    L[i]=min([L[nxt[q]]-1 for q in o.qs if q in nxt]+[end])
    for q in o.qs: nxt[q]=i
print('ASAP depth',max(E.values())+1)
lo,hi=int(sys.argv[2]) if len(sys.argv)>2 else 0,int(sys.argv[3]) if len(sys.argv)>3 else end
for t in range(lo,hi+1):
    row=[(o,E[i],L[i]) for i,o in enumerate(ops) if o.time==t]
    print(t,' '.join(f"{o.kind}{'/'.join(map(str,o.qs))}[{e}-{l}]" for o,e,l in row if l-e==0 ))
