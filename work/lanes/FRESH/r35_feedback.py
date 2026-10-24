"""All-orders coordinate feedback with exact time-dependence interpolation.

A native idle's survival is rho**n. Moving a k-wire operation changes two gaps
per wire, so each unnormalised moment is Laurent degree <=k in rho**time.
Use 2k+1 exact-contraction nodes, interpolate A and loss*A (not their ratio),
then directly contract any selected unsampled optimum. This covers EVERY integer
within the per-wire slack, while avoiding redundant contractions. Single-wire
unitaries commute with local depolarization, hence their shift is noise-identical.
"""
from round35 import *
import numpy as np

def run(procs=7):
 ops,dets,md=load(BASE);base=emit('feedback_base',ops,dets,md,dict(kind='control'));certify(base)
 r=price(base,procs);current=r;best=r['loss'];moves=[];count=0
 indices=sorted(range(len(ops)),key=lambda i:(-ops[i].time,-len(ops[i].qs),i))
 for ordinal,i in enumerate(indices):
  o=ops[i];qs=set(o.qs)
  lo=max([p.time for p in ops[:i] if qs&set(p.qs)],default=-1)+1
  hi=min([p.time for p in ops[i+1:] if qs&set(p.qs)],default=47)-1
  if hi==lo:continue
  old=o.time
  if o.kind in ('T','TDG','H','SX','SXDG','S','SDG','I'):
   with (D/'feedback_results.jsonl').open('a') as log:log.write(json.dumps(dict(index=i,kind=o.kind,qubits=o.qs,lo=lo,hi=hi,status='noise-identical: local depolarization covariance'))+'\n')
   continue
  k=len(qs);need=min(2*k+1,hi-lo+1);nodes={old,lo,hi}
  while len(nodes)<need:
   nodes.add(max(set(range(lo,hi+1))-nodes,key=lambda t:min(abs(t-v) for v in nodes)))
  rows={old:dict(current,stem=None)}
  def evaluate(at):
   nonlocal count
   oo=copy.deepcopy(ops);oo[i].time=at
   stem=emit(f'feedback_i{i:03}_t{at:02}',oo,copy.deepcopy(dets),md,dict(moves=moves+[dict(index=i,kind=o.kind,qubits=o.qs,old=old,new=at)]))
   certify(stem,singles=False);rr=price(stem,procs);rr.update(stem=str(stem),index=i,kind=o.kind,qubits=o.qs,old=old,new=at);rows[at]=rr;count+=1
   with (D/'feedback_results.jsonl').open('a') as log:log.write(json.dumps(rr)+'\n')
   print('PRICE',json.dumps(rr),flush=True)
   return rr
  for at in sorted(nodes-{old}):evaluate(at)
  if hi-lo+1>len(nodes):
   rho=1-4*.001/3
   x=np.array([rho**(t-old) for t in sorted(nodes)])
   aa=np.array([rows[t]['acceptance'] for t in sorted(nodes)])
   nn=np.array([rows[t]['acceptance']*rows[t]['loss'] for t in sorted(nodes)])
   pa=np.polynomial.Polynomial.fit(x,aa*x**k,2*k)
   pn=np.polynomial.Polynomial.fit(x,nn*x**k,2*k)
   predicted=[]
   for at in range(lo,hi+1):
    xx=rho**(at-old);A=float(pa(xx)/xx**k);N=float(pn(xx)/xx**k)
    if A>=.5005:predicted.append((N/A,at,A))
   if predicted:
    loss,at,acc=min(predicted)
    if at not in rows and loss<best-1e-12:
     rr=evaluate(at)
     assert abs(rr['loss']-loss)<3e-12 and abs(rr['acceptance']-acc)<3e-12,(i,at,rr,loss,acc)
   (D/f'feedback_i{i:03}_interpolation.json').write_text(json.dumps(dict(index=i,kind=o.kind,qubits=o.qs,lo=lo,hi=hi,nodes=sorted(nodes),covered_integer_times=hi-lo+1,degree=2*k,predicted=predicted),indent=2))
  feasible=[(rr['loss'],at,rr) for at,rr in rows.items() if rr['acceptance']>=.5005]
  if feasible:
   loss,at,rr=min(feasible,key=lambda z:z[0])
   if loss<best-1e-12:
    best=loss;current=rr;o.time=at;moves.append(dict(index=i,kind=o.kind,qubits=o.qs,old=old,new=at))
    target=emit('feedback_best',ops,dets,md,dict(moves=moves))
    Path(str(target)+'.allorders.json').write_text(Path(str(rr['stem'])+'.allorders.json').read_text())
    (D/'feedback_incumbent.json').write_text(json.dumps(dict(loss=best,acceptance=rr['acceptance'],moves=moves,source=rr['stem']),indent=2))
    print('IMPROVED',best,rr['acceptance'],moves[-1],flush=True)
  (D/'feedback_progress.json').write_text(json.dumps(dict(ordinal=ordinal,total_ops=len(ops),evaluations=count,loss=best,acceptance=current['acceptance'],moves=moves),indent=2))
 print('DONE',best,current['acceptance'],len(moves),count,flush=True)

if __name__=='__main__':run(int(sys.argv[1]) if len(sys.argv)>1 else 7)
