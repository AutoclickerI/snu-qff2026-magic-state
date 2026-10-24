from core import *
import argparse

def build(start=15):
 name=f'partial{start}';us=json.loads((HERE/'reuse10.units.json').read_text());dets=[s for s in (HERE/'reuse10.qasm').read_text().splitlines() if s.startswith('// DETECTOR')]
 bc=[];other=[]
 for u in us:
  if u['region']=='prep' and set(u['qs'])<=set(B+C):bc.append(u)
  else:other.append(u)
 # Occupied cells become available after their prefix / data transfer use.
 release={q:start for q in B+C}
 for u in other:
  if u['region'] not in ('pre','prep'):continue
  for q in u['qs']:
   if q in release:release[q]=max(release[q],u['t']+1)
 end=release.copy()
 for u in bc:
  u['t']=max(end[q] for q in u['qs'])
  for q in u['qs']:end[q]=u['t']+1
 assert max(end.values())<=49
 emit(other+bc,dets,D,HERE/name,dict(R=49,bc_start_bound=start))
 print(name,min(u['t'] for u in bc),max(u['t'] for u in bc),flush=True)
if __name__=='__main__':build(15);build(24)
