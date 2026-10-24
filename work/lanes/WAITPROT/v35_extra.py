"""Fold guard readout into existing instruments; shared and reused helpers."""
from v35_build import *

def fold(c,q,h,axis,first,last,readbit,readtime,mode):
 z=axis=='Z';m=find(c,bit=readbit);assert m['qs']==[h] and m['kind']==('MX'if z else'M')
 m['t']=readtime
 if mode=='reset':add(c,'RX'if z else'R',[h],first-1)
 elif mode=='mz_parity':
  assert not z;ini=nb(c);add(c,'M',[h],first-1,ini)
  c['dets']=[sorted(row+[ini])if row==[readbit]else row for row in c['dets']]
 elif mode!='first_use':raise ValueError(mode)
 edge=[h,q]if z else[q,h];add(c,'CX',edge,first);add(c,'CX',edge,last)
 if [readbit]not in c['dets'] and mode!='mz_parity':c['dets'].append([readbit])
 return c

def shared(c,axis,mode):
 h=21;z=axis=='Z'
 if mode=='separate':
  add(c,'RX'if z else'R',[h],18);bit=nb(c)
  add(c,'MX'if z else'M',[h],30,bit);c['dets'].append([bit])
  if z:add(c,'R',[h],31)
 elif mode=='fold':
  assert not z;add(c,'R',[h],18)
 elif mode=='first_use':assert not z
 else:raise ValueError(mode)
 for q,t in [(20,19),(15,20),(15,28),(20,29)]:add(c,'CX',[h,q]if z else[q,h],t)
 return c

def main():
 jobs=[]
 def put(name,c,**desc):jobs.append(emit(name,c,desc))
 for q,h,axis,first,last,bit,end in [(15,21,'X',20,29,45,32),(10,16,'X',20,22,43,24),(10,16,'X',20,27,43,29),(20,26,'Z',19,30,256,32)]:
  for mode in (['reset']if axis=='Z'else['reset','first_use','mz_parity']):
   c=fold(clone(),q,h,axis,first,last,bit,end,mode)
   put(f'fold_q{q}_h{h}_{first}_{last}_{mode}',c,family='fold_existing_detector',q=q,h=h,axis=axis,first=first,last=last,readbit=bit,readtime=end,mode=mode)
 for ax,mode in [('Z','separate'),('X','separate'),('X','fold'),('X','first_use')]:
  put(f'shared_20_15_h21_{ax}_{mode}',shared(clone(),ax,mode),family='shared_helper',data=[20,15],helper=21,axis=ax,mode=mode)
 # A second q7 window using h13 after its first guard and before the B encoder.
 for axis in ['Z','X']:
  for initmode in ['reset','reuse']:
   c=clone();find(c,t=25,qs=[13],kind='R')['t']=33
   g=dict(q=7,h=13,axis=axis,init=26,first=27,last=31,end=32,restore=None)
   if initmode=='reset':gadget(c,g)
   else:
    if axis=='Z':continue # preceding guard leaves Z, not X, eigenstate.
    bit=nb(c);add(c,'CX',[7,13],27);add(c,'CX',[7,13],31);add(c,'M',[13],32,bit)
    # Use the old guard's final record as the next guard's initial frame.
    c['dets'].append([275,bit])
   put(f'released_q7_h13_{axis}_{initmode}',c,family='released_helper',gadget=g,mode=initmode)
 # Change helper axis on each existing guard, restoring its original readout
 # basis before the next resource initialization when needed.
 for g in GUARDS:
  if g['axis']=='Z':continue
  c=clone();ini=find(c,t=g['init'],qs=[g['h']],kind='R');ini['kind']='RX';ini['t']=g['first']-1
  for t in [g['first'],g['last']]:find(c,t=t,qs=[g['q'],g['h']],kind='CX')['qs']=[g['h'],g['q']]
  find(c,t=g['end'],qs=[g['h']],kind='M')['kind']='MX'
  if g['h']in(11,5):add(c,'R',[g['h']],g['end']+1)
  put(f'guard{g["bit"]}_dualZ',c,family='guard_axis_dual',guard=g)
 (V/'extra_jobs.json').write_text(json.dumps(jobs,indent=2));print('EXTRA',len(jobs))
if __name__=='__main__':main()
