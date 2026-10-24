from assemble_layers import *
from mutations import with_round
import itertools
base=with_round(getbase(0),43);inds=[i for i,o in enumerate(base['ops'])if o.get('tag')=='prefix'and o['t']>=28 and o['lines']in[[f'cx q[{a}],q[{b}];']for a,b in[(3,2),(8,2),(2,8),(2,3)]]];assert len(inds)==4
lines=[base['ops'][i]['lines']for i in inds];rows=[]
for j,perm in enumerate(itertools.permutations(range(4))):
 c=copy.deepcopy(base)
 for i,k in zip(inds,perm):c['ops'][i]['lines']=lines[k]
 name=f'blue_{j}_R43';d,r=fit(c,3);row=dict(stem=name,permutation=perm,schedule=r)
 if d:
  try:st,z=write(d,name,'Permuted the four data/blue-q2 gates as a new instrument; ideal correctness is tested, not assumed from commutation. All source-zero checks retained.');row['screen']=z
  except Exception as e:row['error']=repr(e);print(name,repr(e),flush=True)
 else:print(name,r,flush=True)
 rows.append(row);(V/'blue_permutations.json').write_text(json.dumps(rows,indent=2))
