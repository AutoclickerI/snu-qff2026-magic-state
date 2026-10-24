from reschedule import *
import co_design
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('solver');p.add_argument('--out',required=True);p.add_argument('--workers',type=int,default=2);p.add_argument('--expand',action='store_true');a=p.parse_args();x=json.loads(Path(a.solver).read_text());out=HERE/a.out;raw=HERE/(a.out+'_raw')
 if a.expand:
  # Repair the old pipeline model's skipped-move deadline relaxation using
  # explicit physical dependencies. Expand ticks to preserve every occupancy
  # order, then let the full native scheduler determine the real durations.
  F=4;x['R']*=F;x['RA']=x.get('RA',x['R']//F)*F;x['prefix_times']=[t*F for t in x['prefix_times']];x['jobs']=[(u,v,t*F) for u,v,t in x['jobs']]
  for key,v in x['tokens'].items():
   v['init']*=F;v['ts']=[t*F for t in v['ts']];v['ends']=[t*F for t in v['ends']]
   ready=max([t+2 for t,mv in zip(v['ts'],v['moves']) if mv]+[0])
   field='RA' if key[0] in 'da' else 'R';x[field]=max(x[field],ready)
  for u,v,t in x['jobs']:
   field='RA' if u[0]=='a' else 'R';x[field]=max(x[field],t+1)
  x['R']=max(x['R'],x['RA'])
 co_design.build(x,raw)
 meta=json.loads(raw.with_suffix('.json').read_text());ops=json.loads(raw.with_suffix('.units.json').read_text());ops.sort(key=lambda o:o['t']);head,rr,dets=S.qasm_ops(raw.with_suffix('.qasm').read_text())
 schedule_build(ops,dets,meta['data_qubits'],out,a.workers,dict(data_hops=meta['data_hops'],block_moves=meta['block_moves'],source_solver=str(Path(a.solver).resolve())))
