from build import *
import moments_gradient as mg,zero_idle,numpy as np,argparse
import wide_moments

def step(c,radius=2):
 c,txt=normalized(c);ev=wide_moments.prepare(zero_idle.evaluate(txt,c['meta']['data_qubits']));base,grad=mg.evaluate(ev);per={}
 for i,o in enumerate(c['ops']):
  for q in unit(o).qs:per.setdefault(q,[]).append(i)
 old=[o['t']for o in c['ops']];R=c['meta']['R'];mx=max(old);m=cp_model.CpModel();ts=[m.NewIntVar(max(0,t-radius),min(mx,t+radius),f't{i}')for i,t in enumerate(old)]
 for i,t in enumerate(old):
  if t>=R:m.Add(ts[i]==t)
 ends={}
 for q,seq in per.items():
  for i,j in zip(seq,seq[1:]):m.Add(ts[j]>ts[i]);ends[q,old[i]+1]=(i,j)
  ends[q,old[seq[-1]]+1]=(seq[-1],None)
 loss=[];acc=[];by=np.bincount(ev.fch,weights=ev.fp*grad,minlength=len(ev.m.chans));byA=np.bincount(ev.fch,weights=ev.fp*(1-ev.a_single),minlength=len(ev.m.chans))
 for ci,ch in enumerate(ev.m.chans):
  if ch['gap']is None:continue
  q,start,n=ch['gap'];i,j=ends[q,start];end=mx+1 if j is None else ts[j];delta=end-ts[i]-1-n;assert(mx+1 if j is None else old[j])-old[i]-1==n
  dp=-.75*math.log1p(-4e-3/3)*(1-4e-3/3)**n;ix=np.flatnonzero(ev.fch==ci);gl=by[ci]/ch['prob']if ch['prob']else float(np.mean(grad[ix]));ga=byA[ci]/ch['prob']if ch['prob']else float(np.mean(1-ev.a_single[ix]));loss.append(round(gl*dp*1e13)*delta);acc.append(round(ga*dp*1e10)*delta)
 m.Add(sum(acc)<=round((-math.log(.5005)+math.log(base['exp_minus_A1']))*1e10));m.Minimize(sum(loss));s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=5;s.parameters.cp_model_presolve=False;status=s.Solve(m)
 if status not in(cp_model.FEASIBLE,cp_model.OPTIMAL)or s.ObjectiveValue()>=-1:return None,dict(base=base,status=s.StatusName(status))
 for i,o in enumerate(c['ops']):o['t']=s.Value(ts[i])
 c,txt=normalized(c);r=wide_moments.evaluate(exact2.Eval(txt,c['meta']['data_qubits']));rec=dict(status=s.StatusName(status),R=R,base=base,predicted=base['total']+s.ObjectiveValue()/1e13,screen=r)
 if r['total']>=base['total']-1e-12 or r['exp_minus_A1']<.5002:return None,rec
 return c,rec
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--iterations',type=int,default=8);p.add_argument('--tag',default='feedback');a=p.parse_args();c=json.loads((V/(a.stem+'.plan.json')).read_text());history=[]
 for k in range(a.iterations):
  out,r=step(c);history.append(r)
  if out is None:print('stopped',k,r,flush=True);break
  c=out;name=f'{a.tag}_{k}';st=save(c,'v31/'+name);st.with_suffix('.screen.json').write_text(json.dumps(r['screen'],indent=2));st.with_suffix('.build.json').write_text(json.dumps(r,indent=2));append_result(name,r,'Exact cubic sensitivity retiming at fixed R, including zero-width waits and acceptance constraint; lane-local wide projector batching.');print(name,json.dumps(r['screen']),flush=True)
 (V/(a.tag+'.history.json')).write_text(json.dumps(history,indent=2))
