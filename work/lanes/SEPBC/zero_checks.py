"""Measure transient known-zero BC wires in existing idle slots."""
from common import *
import argparse
def opportunities(c):
 ops=c['ops'];R=c['meta']['R'];qset=set(B+C)
 # Last preparation initialization before its first retained round use.
 init={q:max(i for i,o in enumerate(ops)if o['t']<R and unit(o).qs==(q,)and unit(o).name in('RX','RESET','MX','MEASURE'))for q in qset}
 vals={};started=set();index=0;out=[]
 for t in range(R+1):
  busy=set()
  for i,o in enumerate(ops):
   if o['t']!=t:continue
   u=unit(o);busy|=set(u.qs)
   for q in u.qs:
    if init.get(q)==i:
     vals[q]=1<<index if u.name in('RX','MX')else 0
     if vals[q]:index+=1
     started.add(q)
   if u.name=='CX'and set(u.qs)<=started:
    a,b=map(int,S.QRE.findall(u.lines[0]));vals[b]^=vals[a]
  for q in started-busy:
   if vals[q]==0 and t>ops[init[q]]['t']and any(o['t']>t and q in unit(o).qs for o in ops):out.append((q,t))
 return out
def add_check(c,q,t):
 c=copy.deepcopy(c);bit=max([int(b)for o in c['ops']for b in re.findall(r'c\[(\d+)\]',' '.join(o['lines']))]+[0])+1
 c['h']=[re.sub(r'creg c\[\d+\]',f'creg c[{bit+1}]',s)for s in c['h']]
 c['ops'].append(dict(lines=[f'measure q[{q}] -> c[{bit}];'],t=t,tag='bc_zero_check',id=9999))
 c['tail'].append(f'// DETECTOR c[{bit}]');c['meta']['zero_checks']=c['meta'].get('zero_checks',[])+[dict(q=q,t=t,bit=bit)]
 return c
def main():
 p=argparse.ArgumentParser();p.add_argument('base');p.add_argument('--tag',default='zero');a=p.parse_args();c=read(H/'inputs'/a.base);ops=opportunities(c);print('opportunities',ops,flush=True)
 for q,t in ops:
  name=f'{a.tag}_q{q}_t{t}'
  try:
   stem=save(add_check(c,q,t),name);r=score(stem);append_result(name,r,'Known-zero B/C intermediate wire measured during an idle slot, with its own detector; full physical noisy instrument.');print(json.dumps(dict(name=name,score=r)),flush=True)
  except Exception as e:append_result(name,dict(error=repr(e)),'Build failure is not a physical closure.');print(name,repr(e),flush=True)
if __name__=='__main__':main()
