import stim,itertools,json,sys
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'work/lanes/CAT3_20261027'))
import smallcat as s
ops,_=s.f.parse_current((H/'cand/spider_bc_source.qasm').read_text());resource=set(s.A+s.B+s.C);ops=[o for o in ops if not(o.time>9 and set(o.qs)&resource)]
c=stim.Circuit((H/'spider_bc.log').read_text());choices=[]
for perm in itertools.permutations([28,29,32,33,34,35]):
 mapping={i:(s.B+s.C+list(perm))[i] for i in range(20)}
 ready={i:max([10]+[o.time+1 for o in ops if mapping[i] in o.qs])for i in range(20)}
 for ins in c:
  typ=ins.name;ts=[t.value for t in ins.targets_copy()]
  if typ=='DETECTOR':continue
  if typ in ('R','RX','M','MX'):
   for i in ts:ready[i]+=1
  else:
   for a,b in zip(ts[::2],ts[1::2]):ready[a]=ready[b]=max(ready[a],ready[b])+1
 choices.append((max(ready.values()),perm))
print(sorted(choices)[:12])
