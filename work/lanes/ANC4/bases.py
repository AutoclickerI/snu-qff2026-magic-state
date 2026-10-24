import sys,itertools,json,collections
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent
G=[85,102,120];S={0}
for g in G:S|={x^g for x in list(S)}
H=[x for x in range(1,128) if all((x&g).bit_count()%2==0 for g in G) and x.bit_count()<=4]
danger=[]
for x in range(128):
 sy=0
 for i in range(7):
  if x>>i&1:sy^=i+1
 if x^(1<<(sy-1) if sy else 0) not in S:danger.append(x)
def rank(xs):
 s={0}
 for x in xs:s|={z^x for z in list(s)}
 return len(s)==16
bases=[]
for h in itertools.combinations(H,4):
 if not rank(h):continue
 wt=min(sum((x&g).bit_count()%2 for g in h) for x in danger)
 deg=[sum(g>>i&1 for g in h) for i in range(7)]
 bases.append(dict(rows=[[i for i in range(7) if g>>i&1] for g in h],cx=sum(g.bit_count() for g in h),weight=wt,degree=deg))
summary=collections.Counter((v['cx'],v['weight'],tuple(sorted(v['degree']))) for v in bases)
(HERE/'parity_bases.json').write_text(json.dumps(bases,indent=2)+'\n')
print(len(bases),dict(summary))
