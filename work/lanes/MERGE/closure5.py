"""Close residual parity directions on the final selected circuit after convergence."""
from wide5 import *
def run(workers):
 hist=json.loads((R/'wide_history.json').read_text());assert hist[-1]['stop'];cur=hist[-1]['price'];st=Path(cur['stem'])
 from specialize5 import specialize
 specialize(st,cur);c=M.read(st);ds,gap=H5.detector_menu(c,st.with_suffix('.qasm').read_text());es=dict(ds);basis=list(ds)
 for mask in range(1,1<<len(gap['extra'])):
  bits=set()
  for k,d in enumerate(gap['extra']):
   if mask>>k&1:bits.symmetric_difference_update(d)
  bits=sorted(bits);i='xor:'+','.join(map(str,bits));es[i]=dict(id=i,fam='detparity',bits=bits)
 # Fresh buyer measurements, including removal of the last round's own edits.
 for e in M.removals(c)+M.trades(c):es[e['id']]=e
 from measured_init import convert_init
 for k,o in enumerate(c['ops']):
  u=M.unit(o)
  if u.name in ('RESET','RX')and convert_init(c,k)is not None:
   e=M.mk(fam='mi',q=u.qs[0],t=o['t'],name=u.name);es[e['id']]=e
 es.update(hist[-1]['atoms']);p=R/'closure_menu.json';dump(p,es);dump(R/'closure_gap.json',gap)
 tasks={(i,)for i in es}
 for n in range(2,len(basis)+1):tasks.update(itertools.combinations(basis,n))
 rows=batch(st,p,tasks,'closure',workers,cur['loss']);singles=[r for r in rows if len(r['edits'])==1]
 rows+=fund(st,p,rows,singles,cur,'closure',workers)
 best=choose(rows,cur);out=dict(base=cur,numerical=best,gain=cur['loss']-best['loss'],gap=gap,pareto=frontier(rows+[cur]),rows=len(rows),needs_new_round=cur['loss']-best['loss']>=1e-9)
 dump(R/'closure_outcome.json',out);print(json.dumps(dict(event='closure_complete',gain=out['gain'],loss=best['loss'],A=best['acceptance'],needs_new_round=out['needs_new_round'])),flush=True)
 return out
if __name__=='__main__':run(int(sys.argv[1]))
