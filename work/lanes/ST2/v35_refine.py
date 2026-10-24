"""Condition on a feasible full bundle before spending remaining acceptance."""
import sys,itertools
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import v35_campaign as v
base=v.C.read(v.V/'selected_initial/choice_000')
def omit(c,qs):
 x=v.C.clone(c)
 for q,t in [(16,24),(21,32),(22,28)]:
  if q not in qs:continue
  ix=[i for i,(u,tt)in enumerate(zip(x['u'],x['t']))if tt==t and u.qs==(q,)and u.name=='RESET'];assert len(ix)==1,(q,ix)
  v.a.remove_units(x,set(ix))
 return v.d.normalize(x)
def proposals():
 for n in (1,2,3):
  for qs in itertools.combinations([16,21,22],n):
   yield 'omit_'+'_'.join(map(str,qs)),omit(base,qs),dict(family='conditional_init_omit',parent='selected_initial/choice_000',qubits=qs,budget_screen=True)
 for qs in [(16,),(16,21,22)]:
  c=omit(base,qs)
  for q,h,ax,ini,first,last,end in [(10,16,'X',20,21,22,23),(10,16,'X',20,21,27,28)]:
   yield 'echo10_'+str(last)+'_omit_'+'_'.join(map(str,qs)),v.add_echo(c,q,h,ax,ini,first,last,end),dict(family='conditional_ported_echo',qubits=qs,last=last,budget_screen=True)
 # Use the same-basis guard outcome to prepare q13, paying only its extra readout.
 c=omit(base,[16,21,22]);i=next(i for i,(u,t)in enumerate(zip(c['u'],c['t']))if t==25 and u.qs==(13,)and u.name=='RESET');b=v.C.bit(c);c['u'][i]=v.C.Unit([f'measure q[13] -> c[{b}];']);c['tail'].append(f'// DETECTOR c[{b}]')
 yield 'omit_all_mz13',c,dict(family='conditional_mz13',budget_screen=True)
if __name__=='__main__':v.a.batch(proposals(),'refined',9)
