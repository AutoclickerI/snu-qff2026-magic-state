from common import *
from variants import retime
import itertools
cs=json.loads((HERE/'encoder_candidates.json').read_text());rows=json.loads((HERE/'internal_star.json').read_text())['admissible'];built=[]
for k,row in enumerate(rows):
 c=cs[row['encoder']];gates=[e for L in c['ops'] for e in L];h,us,tail,old,meta,init,ai=base()
 before=[i for i,t in enumerate(old) if t<45 and i not in ai];after=[i for i,t in enumerate(old) if t>=45];best=None
 for order in itertools.permutations([14,9,16]):
  au=[unit([f'reset q[{q}];']+([f'h q[{q}];'] if q in c['pivots'] or q==15 else [])) for q in A]
  for j,(u,v) in enumerate(gates):
   if j==row['boundary']:
    au += [unit([f'cx q[15],q[{q}];']) for q in order]
    au += [unit(['h q[15];','measure q[15] -> c[100];']+(['h q[15];'] if 15 in c['pivots'] else []))]
    if 15 not in c['pivots']:au += [unit(['reset q[15];'])]
   au.append(unit([f'cx q[{u}],q[{v}];']))
  uu=[us[i] for i in before]+au+[us[i] for i in after];tt=[old[i] for i in before]+[40]*len(au)+[old[i] for i in after]
  rr=set(range(len(before)+len(au),len(uu)));ts,R=retime(uu,tt,rr)
  key=(R,-sum(ts))
  if best is None or key<best[0]:best=(key,uu,ts,order)
 key,uu,ts,order=best
 name=f'internal_{k:03}';emit(name,uu,ts,tail+['// DETECTOR c[100]'],dict(R=key[0],method='internal A15 logical-X parity check before joining encoder',internal=row,check_order=order))
 built.append(dict(name=name,R=key[0],encoder=row['encoder'],boundary=row['boundary'],order=order))
(HERE/'internal_manifest.json').write_text(json.dumps(built,indent=1));print('built',len(built),'R range',min(x['R'] for x in built),max(x['R'] for x in built),flush=True)
