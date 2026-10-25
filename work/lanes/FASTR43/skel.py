from fr import *
import sys
ops,dets,md=load(V36F)
P=pairs_of(ops); pid={id(x) for p in P for x in p}
print(len(P),'pairs')
lo,hi=int(sys.argv[1]),int(sys.argv[2]); qs=None if len(sys.argv)<4 else list(map(int,sys.argv[3].split(',')))
for t in range(lo,hi+1):
    row=[o for o in ops if o.time==t and id(o) not in pid and (qs is None or set(o.qs)&set(qs))]
    print(t,' '.join(f"{o.kind}{'/'.join(map(str,o.qs))}"+(f"@c{o.bit}" if o.bit is not None else '') for o in row))
