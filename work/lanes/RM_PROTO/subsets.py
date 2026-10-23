import sys,copy,json,itertools,re
sys.dont_write_bytecode=True
from variants import direct,final_round,finish
from alap import alap
from build import BASE

def subset(keep):
 c=direct(True);cur=None;new=[];removed=set()
 for line in c.lines:
  if line.startswith('// STAGE'):cur=line.split()[-1]
  if cur in ['TA','TB','PA','PB'] and cur not in keep:
   if line.startswith('measure '):removed.add(int(re.search(r'c\[(\d+)\]',line)[1]))
  else:new.append(line)
 c.lines=new;c.dets=[d for d in c.dets if not(set(d)&removed)]
 return c
if __name__=='__main__':
 for n in range(4):
  for keep in itertools.combinations(['TA','TB','PA','PB'],n):
   name='sub_'+('_'.join(keep) if keep else 'none')+'_steane'
   c=alap(final_round(subset(keep)));finish(c,name)
