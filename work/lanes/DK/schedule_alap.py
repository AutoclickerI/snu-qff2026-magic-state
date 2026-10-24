import json,re
from build import BASE,DATA,Circuit,build
from build_round import append_round
from tprep.qasm import convert
from tprep.parse import parse,declarations
from tprep.exact import verify

def alap(c):
 q,s,_=c.write('_tmp_sched',{})
 prog=parse(s);events=[];free=[0]*36;recbits=[int(re.search(r'c\[(\d+)\]',line)[1]) for line in c.lines if line.startswith('measure ')]
 r=0
 for ins in prog:
  if not ins.qubits: continue
  n=ins.name; qs=[x+1 for x in ins.qubits]; t=max(free[q-1] for q in qs)
  for q in qs: free[q-1]=t+1
  events.append([t,n,qs,recbits[r] if n in ['M','MX'] else None]); r += n in ['M','MX']
 end=max(free);latest=[end]*36
 for ev in reversed(events):
  ev[0]=min(latest[q-1] for q in ev[2])-1
  for q in ev[2]: latest[q-1]=ev[0]
 new=Circuit(); new.nm=c.nm;new.dets=c.dets;new.frame_z=c.frame_z
 for t in sorted(set(ev[0] for ev in events)):
  new.barrier(range(1,37))
  for _,n,qs,rec in [e for e in events if e[0]==t]:
   if n in ['M','MX']:
    if n=='MX':new.gate('h',*qs)
    new.lines.append(f'measure q[{qs[0]-1}] -> c[{rec}];')
   elif n in ['R','RX']:new.reset(qs[0],'X' if n=='RX' else 'Z')
   else:new.gate({'CX':'cx','T':'t','T_DAG':'tdg','H':'h','S':'s','S_DAG':'sdg'}[n],*qs)
 return new

if __name__ == '__main__':
 for stem,keep in [('dk_none_steane_alap',()),('dk_PB_steane_alap',('PB',)),('dk_PA_steane_alap',('PA',))]:
  c=build(barriers=True,keep=keep);append_round(c); c=alap(c)
  _,s,j=c.write(stem,dict(protocol='DK two-block plus verified round',variant=stem,kept_checks=list(keep),status='grid-free'))
  f,p=declarations(s);ex=verify(s,DATA,frame=f,postselect=p,n_qubits=36);j.update(noiseless=ex,status='verified grid-free' if not ex['errors'] else 'INVALID');(BASE/(stem+'.json')).write_text(json.dumps(j,indent=2)+'\n');print(stem,j['cx'],ex)
