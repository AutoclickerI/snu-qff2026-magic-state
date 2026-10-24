"""Late fresh-cell initialization and storage readout folded into a data transfer."""
from v35_build import *
jobs=[]
def put(name,c,description):
 r=emit(name,c,description);r['procs']=4;jobs.append(r)
for q,bit,last in [(16,43,30),(21,45,36),(22,46,34),(20,42,7)]:
 c=clone();o=find(c,bit=bit);old=o['t'];o['t']=last
 put(f'fresh_q{q}_t{last}',c,dict(family='fresh_init_timing',q=q,bit=bit,old=old,new=last))
for label,qs in [('three',[16,21,22]),('all',[16,21,22,20])]:
 c=clone()
 for q,bit,last in [(16,43,30),(21,45,36),(22,46,34),(20,42,7)]:
  if q in qs:find(c,bit=bit)['t']=last
 put('fresh_'+label,c,dict(family='fresh_init_joint',qubits=qs))
for first in [20,21]:
 for mode in ['reset','first_use']:
  c=clone();find(c,bit=43)['t']=30
  if mode=='reset':add(c,'R',[16],first-1)
  add(c,'CX',[15,16],first);add(c,'CX',[15,16],29)
  put(f'fold15_h16_X_{first}_29_{mode}',c,dict(family='fold_transfer_helper',q=15,h=16,axis='X',first=first,last=29,readout=30,mode=mode))
c=clone();o=find(c,bit=43);o.update(t=30,kind='R',bit=None);c['dets']=[r for r in c['dets']if r!=[43]]
gadget(c,dict(q=15,h=16,axis='Z',init=19,first=20,last=28,end=29,restore=None))
put('fold15_h16_Z_20_28_reset30',c,dict(family='fold_transfer_helper',q=15,h=16,axis='Z',first=20,last=28,readout=29,restoration=30))
(V/'fresh_jobs.json').write_text(json.dumps(jobs,indent=2))
# A small critical-path job can share an already allocated container quota.
(V/'fresh_priority.json').write_text(json.dumps([r for r in jobs if r['stem']=='fresh_three'],indent=2))
# Pending follow-on queue is read only after the current combination process exits.
follow=json.loads((V/'follow_jobs.json').read_text());follow=[r for r in follow if not(r['stem'].startswith('fresh_')or r['stem'].startswith('fold15_h16_'))]
(V/'follow_jobs.json').write_text(json.dumps(jobs+follow,indent=2));print('FRESH',len(jobs),'FOLLOW TOTAL',len(jobs+follow))
