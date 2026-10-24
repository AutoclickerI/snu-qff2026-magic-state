from assemble_layers import *
from mutations import with_round
rows=[]
for R in [43,42]:
 for mode in [0,1,2]:
  c=with_round(getbase(0),R)
  if mode in(0,1):
   o=next(o for o in c['ops']if o['t']==28 and o['lines']==['reset q[2];','h q[2];']);c['ops'].remove(o)
  if mode in(1,2):
   o=next(o for o in c['ops']if o.get('tag')=='encoder_a'and o['lines']==['reset q[2];','h q[2];']);c['ops'].remove(o)
  name=f'reuseblue_{mode}_R{R}';d,r=fit(c,10,cut=0,phases=True);row=dict(stem=name,schedule=r)
  if d:
   try:st,z=write(d,name,'Reuse measured X state on q2 before/after blue check, preserving every source and detector. Global exact CX/control-phase commuting reorder. Mandatory FAST gate because similar older recipes were slow.');row['screen']=z
   except Exception as e:row['error']=repr(e);print(name,repr(e),flush=True)
  else:print(name,r,flush=True)
  rows.append(row);(V/'reuseblue_builds.json').write_text(json.dumps(rows,indent=2))
