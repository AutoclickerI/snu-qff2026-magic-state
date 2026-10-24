"""Replace a connected-cell timing witness by exact physical encoders.

The abstract six-step encoder allowance is not a claimed physical duration.
Expand every model tick so each real encoder fits at its initialization tick,
emit and verify that circuit, then reschedule the complete native gate DAG ALAP.
"""
from reschedule import *
import co_design,exenc,copy

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('solver');p.add_argument('--out',required=True);p.add_argument('--workers',type=int,default=6);a=p.parse_args();x=json.loads(Path(a.solver).read_text());out=HERE/a.out;enc={};depth=0
 for k in 'abc':
  cells=[x['tokens'][f'{k}{i}']['pos'][0] for i in range(7)];ep=Path(str(out)+f'_prep_{k}.json')
  if not ep.exists():exenc.run(cells,'plus' if k=='a' else 'zero',[],1 if k=='a' else 0,ep,a.workers,False,k=='a',10000000)
  enc[k]=json.loads(ep.read_text());depth=max(depth,len(enc[k]['ops']))
 F=depth+2;y=copy.deepcopy(x);y['jobs']=[];y['prefix_times']=[t*F for t in x['prefix_times']];y['R']=x['R']*F;y['RA']=x.get('RA',x['R'])*F
 for key,v in y['tokens'].items():
  v['init']*=F;v['ts']=[t*F for t in v['ts']];v['ends']=[t*F for t in v['ends']]
 # The original abstract snapshot permits a skipped terminal move at R+1.
 # Explicitly place every real move before its coupling; no abstract duration
 # is trusted as native timing or silently counted as a completed circuit.
 for key,v in y['tokens'].items():
  ready=max([t+2 for t,mv in zip(v['ts'],v['moves']) if mv]+[0])
  if key[0] in 'da':y['RA']=max(y['RA'],ready)
  else:y['R']=max(y['R'],ready)
 y['R']=max(y['R'],y['RA'])
 for k in 'abc':
  cells=[y['tokens'][f'{k}{i}']['pos'][0] for i in range(7)];p=enc[k];y['encoders'][k]=dict(ops=[[(cells.index(u),cells.index(v)) for u,v in L] for L in p['ops']],pivots=[cells.index(q) for q in p['pivots']])
  start=y['tokens'][f'{k}0']['init']
  for layer,L in enumerate(p['ops']):
   for u,v in L:y['jobs'].append((f'{k}{cells.index(u)}',f'{k}{cells.index(v)}',start+layer+1))
 raw=HERE/(a.out+'_expanded');co_design.build(y,raw);ops=json.loads(raw.with_suffix('.units.json').read_text());ops.sort(key=lambda o:o['t']);meta=json.loads(raw.with_suffix('.json').read_text());head,rr,dets=S.qasm_ops(raw.with_suffix('.qasm').read_text())
 schedule_build(ops,dets,meta['data_qubits'],out,a.workers,dict(data_hops=meta['data_hops'],block_moves=meta['block_moves'],source_solver=str(Path(a.solver).resolve()),encoders=enc,expanded_scale=F))
