"""Drain the explicit finalist MC queue; resource allocation is read between cases."""
from v35_gate import *
manifest=sys.argv[1]if len(sys.argv)>1 else'mc_jobs.json'
allocation=sys.argv[2]if len(sys.argv)>2 else'mc_allocation.json'
while True:
 jobs=json.loads((V/manifest).read_text());pending=[]
 for name in jobs:
  p=V/name;sha=hashlib.sha256(p.with_suffix('.qasm').read_bytes()).hexdigest();receipt=p.with_suffix('.mc.json')
  if receipt.exists()and json.loads(receipt.read_text()).get('sha256')==sha:continue
  g=json.loads(p.with_suffix('.gates.json').read_text());r=json.loads(p.with_suffix('.score.json').read_text())
  assert g['passed']and g['speed']['classification']=='FAST'and r['acceptance']>=.5005
  assert sha==g['sha256']==r['sha256'];pending.append(name)
 if not pending:break
 name=pending[0];procs=json.loads((V/allocation).read_text())['procs']
 print('MC_BEGIN',name,procs,flush=True);mc(name,procs)
print('MC_QUEUE_COMPLETE',flush=True)
