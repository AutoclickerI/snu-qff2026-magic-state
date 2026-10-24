import sys,json,collections
from pathlib import Path
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parent));from native import read
out=[]
for f in sorted(H.glob('region*.plan.json')):
 if f.stem.endswith('_ordered.plan'):continue
 stem=Path(str(f)[:-10]);p=json.loads(f.read_text())
 if not stem.with_suffix('.qasm').exists():continue
 try:
  _,ops,_=read(stem);byline=collections.defaultdict(collections.deque);bad=[]
  for o in ops:byline[tuple(o['lines'])].append(o['t'])
  for o in sorted(p['ops'],key=lambda x:x['t']):
   queue=byline[tuple(o['lines'])];t=queue.popleft()if queue else None
   if t!=o['t']:bad.append(dict(expected=o,actual=t))
  roundtimes=[o['t']for o in ops if o['name']=='CX'and o['qs']==[p['meta']['data_qubits'][0],p['meta']['A'][0]]]
  out.append(dict(stem=stem.name,native_round=roundtimes[-1],metadata_R=p['meta']['R'],bad=bad,pass_R=roundtimes[-1]==p['meta']['R']))
 except Exception as e:out.append(dict(stem=stem.name,error=repr(e)))
(H/'native_audit.json').write_text(json.dumps(out,indent=1));print([(x['stem'],x.get('pass_R'),len(x.get('bad',[])),x.get('error'))for x in out])
