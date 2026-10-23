import sys,json,copy,re
sys.dont_write_bytecode=True
from build import Circuit,DATA,BASE
from variants import direct,final_round,finish
from tprep.qasm import convert
from tprep.parse import parse

def alap(c):
 q,s,j=c.write('_schedule_input',{})
 prog=parse(s);events=[];r=0;free=[0]*36
 recbits=[int(re.search(r"c\[(\d+)\]",line)[1]) for line in c.lines if line.startswith("measure ")]
 for ins in prog:
  if not ins.qubits:continue
  n=ins.name;qs=[x+1 for x in ins.qubits]
  assert len(qs)==(2 if n=='CX' else 1),(n,qs)
  t=max(free[q-1] for q in qs)
  for qu in qs:free[qu-1]=t+1
  events.append([t,n,qs,recbits[r] if n in ['M','MX'] else None])
  if n in ['M','MX']:r+=1
 end=max(free);latest=[end]*36
 for ev in reversed(events):
  ev[0]=min(latest[q-1] for q in ev[2])-1
  for q in ev[2]:latest[q-1]=ev[0]
 new=Circuit();new.nm=c.nm;new.dets=c.dets;new.frame=c.frame
 for t in sorted(set(ev[0] for ev in events)):
  new.barrier(range(1,37))
  for _,n,qs,rec in (ev for ev in events if ev[0]==t):
   if n in ['M','MX']:
    if n=='MX':new.gate('h',*qs)
    new.lines.append(f'measure q[{qs[0]-1}] -> c[{rec}];')
   elif n in ['R','RX']:new.reset(qs[0],'X' if n=='RX' else 'Z')
   else:new.gate({'CX':'cx','T':'t','T_DAG':'tdg','H':'h','S':'s','S_DAG':'sdg'}[n],*qs)
 return new

if __name__=='__main__':
 for par in [False,True]:
  name='rm7_'+('parallel' if par else 'serial')
  c=direct(par)
  finish(alap(c),name+'_alap')
  finish(alap(final_round(c)),name+'_steane_alap')
