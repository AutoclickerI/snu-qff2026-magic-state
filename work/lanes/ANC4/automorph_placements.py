import sys,json,itertools
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent;D0=[0,20,7,4,3,15,8]
autos=[]
for cols in itertools.permutations(range(1,8),3):
 vals=[0]
 for c in cols:vals += [v^c for v in vals[:]]
 if len(set(vals))==8:autos.append([vals[i]-1 for i in range(1,8)])
for fn in ['layout_enumeration','layout_tele_enumeration']:
 raw=json.loads((HERE/(fn+'.json')).read_text());out=[]
 for lay in raw['top']:
  for perm in autos:
   v=lay.copy()
   for key in ['B','d','a']:v[key]=[lay[key][i] for i in perm]
   v['code_permutation']=perm;v['distance']=sum(abs(x//6-y//6)+abs(x%6-y%6) for x,y in zip(D0,v['d']))
   out.append(v)
 out.sort(key=lambda v:v['distance']);(HERE/(fn+'_autos.json')).write_text(json.dumps(out[:20],indent=2)+'\n');print(fn,len(autos),out[:1])
