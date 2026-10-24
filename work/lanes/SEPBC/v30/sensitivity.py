"""One full-cubic sensitivity step within the winning R45 precedence order."""
from retime import *
import moments_gradient as mg,zero_idle,numpy as np
c=json.loads((V/'commute_tail.plan.json').read_text());c,txt=normalized(c);ev=zero_idle.evaluate(txt,c['meta']['data_qubits']);base,grad=mg.evaluate(ev)
assert abs(base['total']-json.loads((V/'commute_tail.screen.json').read_text())['total'])<1e-13
per=collections.defaultdict(list)
for i,o in enumerate(c['ops']):
 for q in unit(o).qs:per[q].append(i)
old=[o['t']for o in c['ops']];R=c['meta']['R'];mx=max(old);m=cp_model.CpModel();ts=[m.NewIntVar(max(0,t-2),min(mx,t+2),f't{i}')for i,t in enumerate(old)]
for i,t in enumerate(old):
 if t>=R:m.Add(ts[i]==t)
ends={}
for q,seq in per.items():
 for i,j in zip(seq,seq[1:]):m.Add(ts[j]>ts[i]);ends[q,old[i]+1]=(i,j)
 ends[q,old[seq[-1]]+1]=(seq[-1],None)
loss=[];acc=[];by=np.bincount(ev.fch,weights=ev.fp*grad,minlength=len(ev.m.chans));byA=np.bincount(ev.fch,weights=ev.fp*(1-ev.a_single),minlength=len(ev.m.chans))
for ci,ch in enumerate(ev.m.chans):
 if ch['gap']is None:continue
 q,start,n=ch['gap'];i,j=ends[q,start];end=mx+1 if j is None else ts[j];delta=end-ts[i]-1-n
 assert(mx+1 if j is None else old[j])-old[i]-1==n
 dp=-.75*math.log1p(-4e-3/3)*(1-4e-3/3)**n;ix=np.flatnonzero(ev.fch==ci);gl=by[ci]/ch['prob']if ch['prob']else float(np.mean(grad[ix]));ga=byA[ci]/ch['prob']if ch['prob']else float(np.mean(1-ev.a_single[ix]));loss.append(round(gl*dp*1e13)*delta);acc.append(round(ga*dp*1e10)*delta)
m.Add(sum(acc)<=round((-math.log(.5002)+math.log(base['exp_minus_A1']))*1e10));m.Minimize(sum(loss));s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=15;s.parameters.cp_model_presolve=False;status=s.Solve(m);assert status in(cp_model.FEASIBLE,cp_model.OPTIMAL)
for i,o in enumerate(c['ops']):o['t']=s.Value(ts[i])
st=save(c,'v30/sensitivity_tail');r=score(st);rec=dict(status=s.StatusName(status),R=R,base=base,predicted=base['total']+s.ObjectiveValue()/1e13,screen=r);st.with_suffix('.build.json').write_text(json.dumps(rec,indent=2));append_result('sensitivity_tail',rec,'One exact-cubic derivative step uses +/-2 native-step slack; full score repriced, R45 and gate order fixed.');print(json.dumps(rec),flush=True)
