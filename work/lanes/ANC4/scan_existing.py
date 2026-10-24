import json,itertools,sys
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent;LANES=HERE.parent
NB={q:{u for u in range(36) if abs(q//6-u//6)+abs(q%6-u%6)==1} for q in range(36)}
def connected(qs):
 qs=set(qs);s={min(qs)}
 while True:
  n=s|set().union(*(NB[q] for q in s))&qs
  if n==s:return s==qs
  s=n
out=[];seen=set()
for lane in ['LAYOUT2','LAYOUT3','R1','DR','ST_LAY']:
 for p in (LANES/lane).glob('*.json'):
  try:j=json.loads(p.read_text())
  except:continue
  if not isinstance(j,dict) or not all(k in j and isinstance(j[k],list) and len(j[k])==7 for k in ['a','b','d']):continue
  if not all(isinstance(v,int) for k in ['a','b','d'] for v in j[k]):continue
  key=tuple(j[k][i] for k in ['a','b','d'] for i in range(7))
  if key in seen:continue
  seen.add(key);free=set(range(36))-set(key)
  valid=[]
  for nf in range(5):
   for f in itertools.combinations(free,nf):
    if connected(j['b']+list(f)):valid.append(list(f))
   if valid:break
  if valid:out.append(dict(source=str(p),d=j['d'],a=j['a'],b=j['b'],f_options=valid,moves=j.get('moves'),connectedA=connected(j['a']),nf=nf))
(HERE/'existing_layouts.json').write_text(json.dumps(out,indent=2)+'\n')
print('scanned',len(seen),'feasible',len(out));print(json.dumps(out[:8]))
