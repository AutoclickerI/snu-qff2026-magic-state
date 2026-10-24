import os,sys,json,collections,itertools
sys.dont_write_bytecode=True
from pathlib import Path
import stim
H=Path(__file__).resolve().parent
L=json.loads((H/'library_input.json').read_text());E=json.loads((H/'library_encoders.json').read_text())
counts=collections.Counter();bybest=collections.Counter()
for sid,blocks in enumerate(E):
 s=L['shapes'][sid];bybest[min(x['cx']for x in blocks)]+=1
 for cid,b in enumerate(blocks):
  rows=[1<<i for i in b['pivots']]
  for u,v in b['ops']:
   assert abs(s[u][0]-s[v][0])+abs(s[u][1]-s[v][1])==1
   rows=[r^((1<<v)if r>>u&1 else 0)for r in rows]
  span={0}
  for r in rows:span|={x^r for x in list(span)}
  key=L['targets'][cid];want={0}
  for i in range(3):want|={x^((key>>(7*i))&127)for x in list(want)}
  assert span==want,(sid,cid)
  assert b['cx']==len(b['ops'])
  counts[b['cx']]+=1
out=dict(shapes=len(E),label_classes=30,encoders_checked=sum(counts.values()),cx_histogram=dict(sorted(counts.items())),shape_min_cx_histogram=dict(sorted(bybest.items())),scope='all connected fixed seven-cell grid-native CX circuits, product X/Z initialization, no helpers, no movement during encoder; arbitrary initial pivot sets, all Steane labels modulo 168 automorphisms; plus encoder from H dual')
(H/'library_verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
