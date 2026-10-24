"""Earlier individual readout/check branches, with true D->A maximum reported."""
from assemble_layers import *
def stagger(base,keep_late):
 c=copy.deepcopy(base);old=44;R=43
 for o in c['ops']:
  if o.get('tag')in('round','decoder'):
   t=o['t']-1;u=unit(o)
   # Two A controls still carry encoder gates at43, so keep those D->A
   # couplings and the corresponding B->D/readout tails a tick later.
   if any(q in u.qs for q in keep_late):t=o['t']
   o['offset']=t-R;o['t']=t
 c['meta']['R']=R;c['meta']['stagger_late_cells']=sorted(keep_late)
 return c
if __name__=='__main__':
 rows=[]
 for n,late in [('stagger01',{0,1,6,12,7,8,13,19,9}),('stagger02',{0,1,6,12,7,8,13,19}),('stagger03',{0,1,7,8}),('stagger04',{0,1,6,7,8,13})]:
  c=stagger(getbase(0),late)
  # A encoder may finish during the first staggered check layer.
  for o in c['ops']:
   if o.get('tag')=='encoder_a'and o['t']==43:o['offset']=0
  d,r=fit(c,8);row=dict(stem=n,schedule=r)
  if d:
   try:
    st,z=write(d,n,'Staggered round branches; source checks and all encoder gates retained. This is a partial-round advance, not a claim that every D->A coupling is at43.');row['screen']=z
   except Exception as e:row['error']=repr(e);print(n,repr(e),flush=True)
  else:print(n,r,flush=True)
  rows.append(row)
 (V/'stagger_builds.json').write_text(json.dumps(rows,indent=2))
