"""Complete combinations of priced guards and compatible beneficial CX pairs."""
from v35_build import *
from v35_extra import fold
from v35_publish import circuit

def late(c):
 changes=[]
 for q in range(36):
  wire=sorted([o for o in c['ops']if q in o['qs']],key=lambda o:o['t'])
  for i,(a,b)in enumerate(zip(wire,wire[1:])):
   if a['kind']in('R','RX')and b['kind']in('R','RX'):
    c['ops'].remove(a);changes.append(dict(remove_redundant_reset=copy.deepcopy(a)));continue
   if a['kind']in('R','RX')or(i==0 and a['kind']in('M','MX')):
    if b['t']>a['t']+1:
     old=a['t'];a['t']=b['t']-1;changes.append(dict(q=q,kind=a['kind'],old=old,new=a['t']))
 return changes
def pair(c,q,h,first,last,axis='X'):
 edge=[q,h]if axis=='X'else[h,q];add(c,'CX',edge,first);add(c,'CX',edge,last);return c
def pack(c,which='all'):
 pair(c,10,16,37,38)
 if which in('all','10_3'):pair(c,3,2,33,34)
 if which=='all':pair(c,0,6,36,37)
 return c
def own(include20z=True,shared=True):
 c=clone();find(c,t=13,qs=[19],kind='R')['t']=17;find(c,t=25,qs=[13],kind='R')['t']=33
 gadget(c,dict(q=7,h=13,axis='Z',init=26,first=27,last=31,end=32,restore=None))
 fold(c,15,21,'X',20,29,45,32,'first_use')
 gadget(c,dict(q=20,h=21,axis='X',init=33,first=34,last=35,end=36,restore=None))
 if include20z:gadget(c,dict(q=20,h=26,axis='Z',init=19,first=20,last=30,end=31,restore=None))
 if shared:pair(c,20,21,21,28)
 late(c)
 return c
jobs=[]
def put(name,c,**desc):
 r=emit('final_'+name,c,dict(family='combination',**desc));r['procs']=4;jobs.append(r)
for label,name in [('st2share','follow_st2best_fund_new05_released7Z_share21_28'),('st2','follow_st2best_fund_new05_released7Z')]:
 source=circuit(V/name)
 for mode in ['10','10_3','all']:
  c=pack(clone(source),mode);put(label+'_pack'+mode,c,source=name,packing=mode)
 c=pack(clone(source));changes=late(c);put(label+'_packall_late',c,source=name,packing='all',late_initializations=changes)
for incz,share in [(True,True),(True,False),(False,True),(False,False)]:
 c=pack(own(incz,share));put(f'own_z{int(incz)}_share{int(share)}',c,source='v35a',late_initializations=True,packing='all',q20_Z=incz,shared20=share)
 if incz and share:
  d=clone(c);d['ops'].remove(find(d,bit=42));d['dets']=[r for r in d['dets']if r!=[42]]
  put('own_omit42',d,source='v35a',packing='all',q20_Z=True,shared20=True,omit_bit42=True)
  d=clone(c);old=find(d,t=33,qs=[19],kind='R');bit=nb(d);old.update(kind='M',bit=bit);d['dets'].append([bit])
  put('own_mz19',d,source='v35a',packing='all',q20_Z=True,shared20=True,measured_resource19=True)
  # Trade part of q7's Z window for a profitable consecutive pair.
  d=clone(c);find(d,t=31,kind='CX',qs=[13,7])['t']=29;find(d,t=32,kind='MX',qs=[13])['t']=30;pair(d,7,1,30,31)
  put('own_q7_short_pack',d,source='v35a',packing='all plus q7/h1',q7_Z_end=29)
c=clone();changes=late(c);put('late_preparations_control',c,source='v35a',late_initializations=changes)
# Restore the future data cell's Z basis after a Z guard by replacing its old
# initialization, rather than trying to fit a fifth operation into four slots.
c=clone();c['ops'].remove(find(c,bit=45));c['dets']=[r for r in c['dets']if r!=[45]]
gadget(c,dict(q=20,h=21,axis='Z',init=32,first=33,last=34,end=35,restore=36))
r=emit('repair_replace45_Zguard',c,dict(family='replace_init_Z_guard',q=20,h=21,first=33,last=34,restore=36));r['procs']=4;jobs.append(r)
(V/'final_jobs.json').write_text(json.dumps(jobs,indent=2));print('FINAL BEAM',len(jobs))
