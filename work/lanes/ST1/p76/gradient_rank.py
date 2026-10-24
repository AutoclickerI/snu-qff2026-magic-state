"""Exact pair/triple timing feedback, accepted only by full all-orders rank."""
from context76 import *
import moments_gradient as mg,zero_idle,detector_order,numpy as np,argparse,gzip
p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--out',required=True);p.add_argument('--iterations',type=int,default=8);p.add_argument('--radius',type=int,default=2);p.add_argument('--workers',type=int,default=2);a=p.parse_args();stem=Path(a.stem);c=json.loads(stem.with_suffix('.plan.json').read_text());best=json.loads(stem.with_suffix('.allorders.json').read_text());results=[]
for it in range(a.iterations):
 c,txt=normalized(c);ev,proof=detector_order.evaluate(txt,c['meta']['data_qubits'],zero_idle.evaluate);diagnostic,grad=mg.evaluate(ev);ops=c['ops'];old=[o['t']for o in ops];R=c['meta']['R'];mx=max(old);per={q:[i for i,o in enumerate(ops)if q in unit(o).qs]for q in range(36)};m=cp_model.CpModel();ts=[m.NewIntVar(max(0,t-a.radius),min(mx,t+a.radius),'t'+str(i))for i,t in enumerate(old)];ends={}
 for i,t in enumerate(old):
  if t>=R:m.Add(ts[i]==t)
 for q,seq in per.items():
  if not seq:continue
  for i,j in zip(seq,seq[1:]):m.Add(ts[j]>ts[i]);ends[q,old[i]+1]=(i,j)
  ends[q,old[seq[-1]]+1]=(seq[-1],None)
 loss=[];acc=[];by=np.bincount(ev.fch,weights=ev.fp*grad,minlength=len(ev.m.chans));byA=np.bincount(ev.fch,weights=ev.fp*(1-ev.a_single),minlength=len(ev.m.chans))
 for ci,ch in enumerate(ev.m.chans):
  if ch['gap']is None:continue
  q,start,n=ch['gap'];i,j=ends[q,start];end=mx+1 if j is None else ts[j];delta=end-ts[i]-1-n;assert(mx+1 if j is None else old[j])-old[i]-1==n
  dp=-.75*math.log1p(-4e-3/3)*(1-4e-3/3)**n;ix=np.flatnonzero(ev.fch==ci);gl=by[ci]/ch['prob']if ch['prob']else float(np.mean(grad[ix]));ga=byA[ci]/ch['prob']if ch['prob']else float(np.mean(1-ev.a_single[ix]));loss.append(round(gl*dp*1e13)*delta);acc.append(round(ga*dp*1e10)*delta)
 m.Add(sum(acc)<=max(0,round((math.log(best['acceptance'])-math.log(.5002))*1e10)));m.Minimize(sum(loss));assert not m.Validate(),m.Validate();s=cp_model.CpSolver();s.parameters.num_workers=a.workers;s.parameters.max_time_in_seconds=10;st=s.Solve(m)
 if st not in(cp_model.FEASIBLE,cp_model.OPTIMAL)or s.ObjectiveValue()>=-1:break
 d=copy.deepcopy(c)
 for i,o in enumerate(d['ops']):o['t']=s.Value(ts[i])
 comp={t:i for i,t in enumerate(sorted({o['t']for o in d['ops']}))};d['meta']['R']=comp[R];name=a.out+f'_{it}';out=save(d,'p76/'+name);r=rank(out,a.workers);row=dict(name=name,result=r,predicted_loss=diagnostic['total']+s.ObjectiveValue()/1e13,cubic_base=diagnostic)
 results.append(row);append_result(name,row,'Exact pair/triple derivatives on all physical idle intervals, including newly opened waits; CP trust radius, full circuit all-orders rank. Same gate order and final B-verification timing.');print(json.dumps(row),flush=True)
 with gzip.open(OUT/(a.out+'.witnesses.jsonl.gz'),'at')as z:z.write(json.dumps(dict(row=row,plan=d))+'\n')
 if r['loss']>=best['loss']-1e-12 or r['acceptance']<.5002:break
 best=r;c=d;bstem=save(c,'p76/'+a.out+'_best');bstem.with_suffix('.allorders.json').write_text(out.with_suffix('.allorders.json').read_text())
(OUT/(a.out+'.receipt.json')).write_text(json.dumps(dict(best=best,results=results),indent=2));print('DONE',json.dumps(best),flush=True)
