import sys,os,json,re,copy
sys.dont_write_bytecode=True
from pathlib import Path
from build import build,Circuit,DATA,BASE
from tprep.exact import verify
from tprep.parse import declarations
from tprep.noise import schedule
from tprep.grid import SUPPORTS

def direct(parallel=False,barriers=False,frame='seven'):
 c=build(False,barriers)
 # Replace all-to-all flag ancillas with independent group ancillas when parallel.
 if parallel:
  group=None;new=[]
  maps={'logical_X_verifier':{16:30},'TA':{},'TB':{16:20,17:21,18:22,19:23},'PA':{16:24,17:25,19:26},'PB':{16:27,17:28,19:29}}
  for line in c.lines:
   if line.startswith('// STAGE '):group=line.split()[-1]
   mp=maps.get(group,{})
   line=re.sub(r'q\[(\d+)\]',lambda m:f'q[{mp.get(int(m[1])+1,int(m[1])+1)-1}]',line)
   new.append(line)
  c.lines=new
 start=c.lines.index('// STAGE software_gauge_frame')
 c.lines=c.lines[:start];c.nm=15;c.dets=c.dets[:-1];c.stage('coherent_gauge_frame')
 for a in range(1,8):c.gate('cx',a,a+7)
 c.stage('bulk_readout');rec={q:c.meas(q,'X') for q in range(8,16)}
 c.dets.append(list(rec.values()));c.frame=[rec[q] for q in range(8,15)]
 return c

ENC=[[(0,2),(1,5),(3,6)],[(0,4),(1,6),(3,5)],[(0,6),(1,2),(3,4)]]

def final_round(c,verifiedA=False,dummy=False):
 # Reuse source ancillas and bulk after measurement, all operations within 36 cells.
 # This serial version is then rescheduled ALAP for ancilla preparations.
 c.stage('final_steane_round')
 A=list(range(8,15));B=list(range(16,23));C=list(range(24,31));D=list(range(1,8))
 for block,dual in [(A,True),(B,False),(C,False)]:
  for i,q in enumerate(block):c.reset(q,'X' if (i not in [0,1,3])==dual else 'Z')
  for layer in ENC:
   for p,q in layer:c.gate('cx',*( (block[q],block[p]) if dual else (block[p],block[q]) ))
 # Force verification just before coupling, and both data couplings in successive steps.
 c.barrier([*A,*B,*C,*D])
 for b,cc in zip(B,C):c.gate('cx',b,cc)
 for d,a in zip([x+1 for x in DATA],A):c.gate('cx',d,a)
 ra=[c.meas(a) for a in A]
 rc=[c.meas(cc) for cc in C]
 for b,d in zip(B,[x+1 for x in DATA]):c.gate('cx',b,d)
 rb=[c.meas(b,'X') for b in B]
 for rec in [ra,rb,rc]:
  for g in SUPPORTS:c.dets.append([rec[i] for i in sorted(g)])
 c.dets.append(rc)
 return c

def finish(c,name):
 q,s,j=c.write(name,{'description':name,'status':'checking'})
 f,p=declarations(s);ex=verify(s,DATA,frame=f,postselect=p)
 _,steps,gaps=schedule(s)
 j.update(noiseless=ex,status='verified grid-free' if not ex['errors'] else 'INVALID',depth=max(t for row in steps for qs,t in row)+1,measure_reset=sum(x.startswith(('reset ','measure ')) for x in c.lines),statements=q.count(';'),bytes=len(q.encode()))
 (BASE/(name+'.json')).write_text(json.dumps(j,indent=2)+'\n');print(name,j['cx'],j['depth'],ex,flush=True)
 return c

if __name__=='__main__':
 for parallel in [False,True]:
  for barrier in ([False,True] if not parallel else [False]):
   stem=f'rm7_{"parallel" if parallel else "serial"}_{"barriers" if barrier else "asap"}'
   c=direct(parallel,barrier);finish(c,stem)
   if not barrier:finish(final_round(copy.deepcopy(c)),stem+'_steane')
