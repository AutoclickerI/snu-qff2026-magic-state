import sys,itertools,json
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'work/lanes/CAT3_20261027'))
import smallcat as s
H=R/'work/lanes/SOTA_DETECT_20261028';ops,_=s.f.parse_current((H/'deep_extra_best/flag_9_0_5.qasm').read_text());K=list(range(28,35));ls={q:max(o.time for o in ops if q in o.qs and o.time<18)+1 for q in K}
ENC=[[(0,2),(1,5),(3,6)],[(0,4),(1,6),(3,5)],[(0,6),(1,2),(3,4)]]
for mode in ['B','A']:
 ans=[]
 for k in itertools.permutations(K):
  ready={i:ls[k[i]]+1 for i in range(7)}
  for layer in ENC:
   for a,b in layer:
    a,b=(b,a) if mode=='B'else(a,b);ready[a]=ready[b]=max(ready[a],ready[b])+1
  ans.append((max(ready.values()),k))
 print(mode,sorted(ans)[:5])
