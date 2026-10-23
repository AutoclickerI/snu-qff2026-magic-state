import sys,os,json,itertools
sys.dont_write_bytecode=True
from pathlib import Path
import ft
here=Path(__file__).resolve().parent
orig={'b':[6,26,13,11,4,23,27],'c':[12,25,19,17,5,29,28]}
prep=json.loads((here.parent/'ST_BC/sat4_14_4.json').read_text())
autos=[]
for v0,v1,v2 in itertools.permutations(range(1,8),3):
 im=[(v0 if n&1 else 0)^(v1 if n&2 else 0)^(v2 if n&4 else 0) for n in range(1,8)]
 if len(set(im))==7 and 0 not in im:autos.append([n-1 for n in im])
for f in here.glob('*.json'):
 try:l=json.loads(f.read_text())
 except ValueError:continue
 if not isinstance(l,dict) or not all(k in l for k in ('a','b','c','d','M','moves')):continue
 ft.B=l['b'];ft.C=l['c']
 if 'template_perm' in l:
  pb=l['template_perm'];pc=l.get('template_permc',pb)
  mp={q:l[k][(pb if k=='b' else pc)[i]] for k in 'bc' for i,q in enumerate(orig[k])}
  ops=[[[mp[u],mp[v]] for u,v in layer] for layer in prep['ops']]
  assert all(abs(u//6-v//6)+abs(u%6-v%6)==1 for layer in ops for u,v in layer)
  d=dict(ops=ops,pivots=[mp[q] for q in prep['pivots']],cx=sum(map(len,ops)),depth=len(ops),cap=80,source='ST_BC/sat4_14_4.json',permB=pb,permC=pc,layout=f.name)
  assert not ft.faults(d)
  f.with_name(f.stem+'_BC_template.json').write_text(json.dumps(d,indent=2)+'\n');print('TEMPLATE',f.name,pb,pc,flush=True);continue
 for swap in (False,True):
  for perm in autos:
   mp={q:l[('c' if k=='b' else 'b') if swap else k][perm[i]] for k in 'bc' for i,q in enumerate(orig[k])}
   ops=[[[mp[u],mp[v]] for u,v in layer] for layer in prep['ops']]
   if not all(abs(u//6-v//6)+abs(u%6-v%6)==1 for layer in ops for u,v in layer):continue
   d=dict(ops=ops,pivots=[mp[q] for q in prep['pivots']],cx=sum(map(len,ops)),depth=len(ops),cap=80,source='ST_BC/sat4_14_4.json',perm=perm,swap=swap,layout=f.name)
   assert not ft.faults(d)
   f.with_name(f.stem+'_BC_template.json').write_text(json.dumps(d,indent=2)+'\n');print('TEMPLATE',f.name,perm,swap,flush=True);break
  else:continue
  break
