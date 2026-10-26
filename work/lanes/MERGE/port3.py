from pass3 import *
from campaign import delta,apply_delta
def remove(c,t,qs,name='CX'):
 o=M.find(c,t,qs,name);c['ops'].remove(o)
def add(c,t,lines):c['ops'].append(dict(t=t,lines=lines))
def check(c):
 seen={}
 for o in c['ops']:
  for q in M.unit(o).qs:
   key=q,o['t']
   if key in seen:raise ValueError(('collision',key,seen[key],o))
   seen[key]=o
 return c
def right(base):
 c=copy.deepcopy(base);nb=M.bit(c)
 remove(c,30,17,'MX');add(c,30,['reset q[17];'])
 remove(c,30,28,'RESET');add(c,30,['h q[28];',f'measure q[28] -> c[{nb}];','h q[28];'])
 for t,a,b in [(31,17,23),(33,17,23),(31,29,28),(32,23,29)]:
  remove(c,t,[a,b]);add(c,t,[f'cx q[{b}],q[{a}];'])
 old=['// DETECTOR c[330] c[332] c[334] c[336] c[352] c[353] c[354]',
      '// DETECTOR c[331] c[332] c[335] c[336] c[353]',
      '// DETECTOR c[333] c[334] c[335] c[336] c[354]']
 new=[f'// DETECTOR c[330] c[332] c[334] c[336] c[352] c[{nb}]',
      f'// DETECTOR c[331] c[332] c[335] c[336] c[{nb}] c[353]',
      '// DETECTOR c[333] c[334] c[335] c[336] c[353]']
 for a,b in zip(old,new):c['tail'][c['tail'].index(a)]=b
 assert not any('c[354]'in l for l in c['tail'])
 return check(c)
def left(base,drop_guard=True):
 c=copy.deepcopy(base)
 for q,t in [(18,33),(24,32)]:
  o=M.find(c,t,q,'RESET');o['t']=31
 add(c,32,['cx q[24],q[18];'])
 if drop_guard:remove(c,33,[12,13])
 add(c,33,['cx q[12],q[18];'])
 for t in [42,43]:
  remove(c,t,[18,24]);add(c,t,['cx q[24],q[18];'])
 return check(c)
def lower(base):
 c=copy.deepcopy(base)
 # Preserve v37d's reused source: its checked/omitted c319 semantics are already accounted for.
 remove(c,39,[3,4])
 for t,a,b in [(40,4,3),(41,4,5),(42,5,11)]:
  remove(c,t,[a,b]);add(c,t-1,[f'cx q[{a}],q[{b}];'])
 return check(c)
def build():
 base=M.read(C/'base');variants={};audit=[]
 for mask in range(1,8):
  c=copy.deepcopy(base);names=[]
  try:
   for i,(name,fn)in enumerate([('R',right),('L',left),('Q3',lower)]):
    if mask>>i&1:c=fn(c);names.append(name)
   st=save(c,'bc3_'+str(mask),dict(kind='BC3 R45 footprint transport',modules=names,base='v37d'))
   variants[str(mask)]=str(st);d=delta(base,M.read(st));dump(R/f'port_diff_{mask}.json',d)
   price(st,dict(kind='BC3 modules',modules=names))
  except Exception as ex:audit.append(dict(mask=mask,error=repr(ex)))
 dump(R/'ports.json',dict(variants=variants,errors=audit))
if __name__=='__main__':build()
