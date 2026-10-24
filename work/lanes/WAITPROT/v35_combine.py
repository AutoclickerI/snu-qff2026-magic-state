"""Reprice complete funding/protection bundles; never add marginal losses."""
from v35_build import *
from v35_extra import fold,shared
from v35_publish import circuit

def fund(c,parity=False):
 find(c,t=13,qs=[19],kind='R')['t']=17
 find(c,t=25,qs=[13],kind='R')['t']=33
 if parity:
  g=copy.deepcopy(GUARDS[1]);g['init']=17;replace_guard_init(c,g,'mz_parity')
  replace_guard_init(c,GUARDS[2],'mz_parity')
 return c
def release(c,axis):
 if axis=='Z':return gadget(c,dict(q=7,h=13,axis='Z',init=26,first=27,last=31,end=32,restore=None))
 bit=nb(c);add(c,'CX',[7,13],27);add(c,'CX',[7,13],31);add(c,'M',[13],32,bit);c['dets'].append([275,bit]);return c
def omit42(c):
 c['ops'].remove(find(c,bit=42));c['dets']=[r for r in c['dets']if r!=[42]]
 assert not any(42 in r for r in c['dets'])
 return c
def q15(c):return fold(c,15,21,'X',20,29,45,32,'first_use')

jobs=[]
def put(name,c,ingredients):
 r=emit('combo_'+name,c,dict(family='combination',ingredients=ingredients));r['procs']=4;jobs.append(r)
put('fund_fold15',q15(fund(clone())),['late_resets_joint','fold_q15_h21_20_29_first_use'])
put('fund_parity_fold15',q15(fund(clone(),True)),['late_resets_joint','guard274/275 measured parity','fold_q15_h21_20_29_first_use'])
for axis in ['Z','X']:
 put('fund_released7'+axis,release(fund(clone(),True),axis),['late_resets_joint','guard274/275 measured parity','released q7 '+axis])
 put('fund_fold15_released7'+axis,omit42(release(q15(fund(clone(),True)),axis)),['late_resets_joint','guard274/275 measured parity','fold q15','released q7 '+axis,'ST2 meas42 omit'])
for mode in ['fold','first_use']:
 c=shared(fund(clone(),True),'X',mode)
 put('fund_shared_'+mode,c,['late_resets_joint','guard274/275 measured parity','shared q20/q15 X '+mode])
 c=drop_guard(shared(fund(clone()),'X',mode),GUARDS[1])
 put('replace274_shared_'+mode,c,['late_resets_joint','remove guard274','shared q20/q15 X '+mode])
for label,src in [('st2','selected_initial/choice_000'),('st2best','tightened/restore_181_182_188_40')]:
 source=ROOT/'work/lanes/ST2/v35'/src
 for parity in [False,True]:
  c=fund(circuit(source),parity)
  put(label+'_fund'+('_parity'if parity else''),c,['ST2 '+src, 'late_resets_joint']+(['guard274/275 measured parity']if parity else[]))
  for axis in ['Z','X']:
   put(label+'_fund'+('_parity'if parity else'')+'_released7'+axis,release(clone(c),axis),['ST2 '+src,'late_resets_joint','guard measured parity'if parity else'reset guards','released q7 '+axis])
(V/'combo_jobs.json').write_text(json.dumps(jobs,indent=2));print('COMBINATIONS',len(jobs))
