from edits import *
def has_record(c,b):return any(f'-> c[{b}];'in' '.join(o['lines'])for o in c['ops'])
def fund(c,level='full'):
 c=copy.deepcopy(c)
 edits=[]
 for b in[42,43,46]+([45]if level=='full'else[]):
  if has_record(c,b):c=remove_check(c,b,'omit');edits.append(('omit',b))
 if level in('full','st2'):
  for b in[39,40,41]:
   if has_record(c,b):c=remove_check(c,b,'reset');edits.append(('reset',b))
 opts=prep_options(c);c=delay_preps(c,opts);c['meta']['funding']=dict(level=level,checks=edits,prep_delays=opts);return c
def add_st2(c,which):
 c=copy.deepcopy(c)
 if which in('15','both'):
  if has_record(c,45):c=remove_check(c,45,'omit')
  if not any(o['lines']==['reset q[21];']and o['t']==32 for o in c['ops']):c['ops'].append(dict(t=32,lines=['reset q[21];'],tag='data_hops',id=9999))
  c=echo(c,15,21,'X',19,20,29,30)
 if which in('20','both'):c=echo(c,20,26,'Z',19,20,30,31)
 return fix(c)
if __name__=='__main__':
 rows=[]
 for level in['omit','st2','full']:
  c=fund(base(),level);emit(c,'fund_'+level,dict(family='funding_joint',level=level),rows)
  for which in['15','20','both']:emit(fund(add_st2(base(),which),level),f'fund_{level}_echo{which}',dict(family='funding_echo_joint',level=level,echo=which),rows)
 (V/'fund_builds.json').write_text(json.dumps(rows,indent=2))
