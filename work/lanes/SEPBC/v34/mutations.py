from design import *
def route14(c):
 c=copy.deepcopy(c)
 for o in c['ops']:
  if o.get('tag')=='data_hops'and 9 in unit(o).qs:o['lines']=rename(o['lines'],{9:14})
 # q14's old prefix release was placed late by loss optimization. Its
 # operations must precede reuse, even though their old timestamp is later
 # than q9's reset. Preserve the data20 guard before that release as well.
 moving=[o for o in c['ops']if o.get('tag')=='prefix'and o['t']>=27 and(o['lines']==['cx q[14],q[20];']or'measure q[14] -> c[12];'in o['lines'])]
 assert len(moving)==2
 for o in moving:c['ops'].remove(o)
 at=next(i for i,o in enumerate(c['ops'])if o.get('tag')=='data_hops'and o['lines']==['reset q[14];'])
 c['ops'][at:at]=moving
 c['meta']['route']='via14';return c
def with_round(c,R):
 c=copy.deepcopy(c);old=c['meta']['R']
 for o in c['ops']:
  if o.get('tag')in('round','decoder'):o['offset']=o['t']-old;o['t']=R+o['offset']
 c['meta']['R']=R;return c
