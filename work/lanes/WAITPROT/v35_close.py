"""Closing comparisons: complete positive-window bundles and moving-cell helpers."""
from v35_build import *
from v35_publish import circuit
jobs=[]
def put(name,c,desc):
 r=emit(name,c,desc);r['procs']=4;jobs.append(r)
def pairs(c,q,h,ts):
 for t in ts:add(c,'CX',[q,h],t)
 return c
patterns={
 'A':(0,6,range(19,25)),
 'B':(20,14,[22,23]),
 'C':(7,1,[21,22]),
 'D':(15,9,[21,22]),
 'E':(15,16,[25,26,27,28]),
 'F':(10,9,[24,25,26,27])}
source=circuit(V/'final_own_mz19')
def build(keys='',read=30):
 c=clone(source);find(c,bit=45)['t']=read
 for key in keys:pairs(c,*patterns[key])
 return c
put('close_read30',build(),dict(family='combination',source='final_own_mz19',folded_readout=30))
for key in patterns:put('close_'+key,build(key),dict(family='combination',source='final_own_mz19',folded_readout=30,early_windows=key))
for keys in ['ABCD','ABCEF','ABCDF','ABCDE','ABCDEF']:
 put('close_'+keys,build(keys),dict(family='combination',source='final_own_mz19',folded_readout=30,early_windows=keys))
put('postT0_pair15_16',pairs(clone(),0,6,[15,16]),dict(family='post_T_identity',q=0,h=6,first=15,last=16,logical=0))
put('close_ABCDEF_postT0',pairs(build('ABCDEF'),0,6,[15,16]),dict(family='combination',source='close_ABCDEF',early_q0=[15,16]))

def late_guard(c,axis):
 # Replace new05's four operations, retaining its detector record identifier.
 m=find(c,t=36,qs=[21],kind='M');bit=m['bit']
 for o in [find(c,t=33,qs=[21],kind='R'),find(c,t=34,qs=[20,21],kind='CX'),find(c,t=35,qs=[20,21],kind='CX'),m]:c['ops'].remove(o)
 add(c,'RX'if axis=='Z'else'R',[21],32);edge=[21,20]if axis=='Z'else[20,21]
 add(c,'CX',edge,33);add(c,'CX',edge,34);add(c,'MX'if axis=='Z'else'M',[21],35,bit);add(c,'R',[21],36)
 return c
for axis in ['Z','X']:
 for keys in ['', 'ABCDEF']:
  put('close_'+(keys or'plain')+'_late'+axis,late_guard(build(keys),axis),dict(family='combination',source='final_own_mz19',early_windows=keys,late_guard_axis=axis,readout=35,restore=36))

# Output labels10 and21 are valid helpers before their data transfers.
for q,h,first,last,n in [(4,10,20,27,1),(4,10,20,27,4),(4,10,30,31,1),(20,21,33,35,1)]:
 c=clone();ts=range(first,first+2*n);pairs(c,q,h,ts)
 put(f'moving_helper_q{q}_h{h}_{first}_{last}_n{n}',c,dict(family='moving_cell_helper_identity',q=q,h=h,window=[first,last],pairs=n,helper_note='Not a data cell yet at these ticks.'))
for q,h,ts in [(4,10,[20,21,22,23,24,25,26,27]),(4,10,[30,31])]:
 keys='ABCDE'if ts[0]==20 else'ABCDEF'
 put(f'close_{keys}_moving{q}_{h}_{ts[0]}',pairs(build(keys),q,h,ts),dict(family='combination',source='close_'+keys,moving_helper=dict(q=q,h=h,ticks=ts)))
for keys in ['', 'ABCDEF']:
 c=build(keys);m=find(c,t=36,qs=[21],kind='M');bit=m['bit']
 for o in [find(c,t=33,qs=[21],kind='R'),find(c,t=34,qs=[20,21],kind='CX'),find(c,t=35,qs=[20,21],kind='CX'),m]:c['ops'].remove(o)
 c['dets']=[r for r in c['dets']if r!=[bit]];pairs(c,20,21,[33,34])
 put('close_'+(keys or'plain')+'_moving21',c,dict(family='combination',source='final_own_mz19',early_windows=keys,replace_new05_by_terminal_herald=True))

# Complementary Z protection nested inside q15's existing X guard.
c=clone();o=find(c,bit=43);o.update(kind='R',bit=None,t=30);c['dets']=[r for r in c['dets']if r!=[43]]
gadget(c,dict(q=15,h=16,axis='Z',init=20,first=21,last=28,end=29,restore=None))
put('nested15_Z_standalone',c,dict(family='fold_transfer_helper',q=15,h=16,axis='Z',first=21,last=28,readout=29,restoration=30))
for keys in ['', 'ABCF']:
 c=build(keys);o=find(c,bit=43);o.update(kind='R',bit=None,t=30);c['dets']=[r for r in c['dets']if r!=[43]]
 gadget(c,dict(q=15,h=16,axis='Z',init=20,first=21,last=28,end=29,restore=None))
 put('close_'+(keys or'plain')+'_nested15Z',c,dict(family='combination',source='final_own_mz19',early_windows=keys,nested_XZ_q15=True))
(V/'close_jobs.json').write_text(json.dumps(jobs,indent=2));print('CLOSING',len(jobs))
