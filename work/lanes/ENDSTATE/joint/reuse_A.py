"""Reuse already checked |0> / |+> sources for A, preserving detector checks."""
import os,sys,json,re,copy
from pathlib import Path
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
from retime import run

def reuse(stem,out,allowed=None,regions=('A',),same_only=False):
 stem=Path(stem);p=json.loads(stem.with_suffix('.plan.json').read_text());ops=sorted(p['ops'],key=lambda o:o['t']);checks=[set(map(int,re.findall(r'c\[(\d+)\]',l)))for l in p['tail']if l.startswith('// DETECTOR')];basis={}
 for row in checks:
  v=sum(1<<b for b in row)
  while v:
   k=v.bit_length()-1
   if k not in basis:basis[k]=v;break
   v^=basis[k]
 def known(bit):
  v=1<<bit
  while v:
   k=v.bit_length()-1
   if k not in basis:return False
   v^=basis[k]
  return True
 changed=[];new=[];previous={}
 for o in ops:
  if o['region']in regions and o['name']in('RESET','RX')and(allowed is None or o['qs'][0]in allowed):
   q=o['qs'][0];prev=previous.get(q)
   if prev and prev['name']in('MEASURE','MX'):
    bits=list(map(int,re.findall(r'c\[(\d+)\]',' '.join(prev['lines']))));assert len(bits)==1
    if known(bits[0])and(not same_only or(o['name']=='RX')==(prev['name']=='MX')):
     if prev['name']=='MX'and prev['lines'][-1]!=f'h q[{q}];':prev['lines'].append(f'h q[{q}];')
     same=(o['name']=='RX')==(prev['name']=='MX');changed.append(dict(cell=q,old=o['name'],previous_measure=prev['name'],bit=bits[0],replacement='none'if same else'H'))
     if same:continue
     o=copy.deepcopy(o);o.update(name='H',lines=[f'h q[{q}];'])
  new.append(o)
  for q in o['qs']:previous[q]=o
 p['ops']=new;p['meta']['A_reuse'if regions==('A',)else'destination_reuse']=changed
 temp=H/(out+'_ordered');temp.with_suffix('.plan.json').write_text(json.dumps(p,indent=1));run(temp,out);print(changed,flush=True)
if __name__=='__main__':reuse(*sys.argv[1:])
