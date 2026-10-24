"""Full exact-loss priced CP-SAT macro scheduling with interaction cuts."""
from common import *
import argparse,gzip
p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--rounds',type=int,default=3);p.add_argument('--trials',type=int,default=20);a=p.parse_args()
c=read(a.stem);history=[];prefix=Path(a.stem).name+'_feedback';counter=0

def evalc(d):
 global counter
 counter+=1;d,txt=normalized(d);ev=exact2.Eval(txt,d['meta']['data_qubits']);r=mom.evaluate(ev)
 return d,r,txt

def proposal(c,index,delta):
 ops=c['ops'];us=[unit(o)for o in ops];ts0=[o['t']for o in ops];R=c['meta']['R'];m=cp_model.CpModel();ts=[m.NewIntVar(max(0,t-2),min(max(ts0),t+2),f't{i}')for i,t in enumerate(ts0)]
 pred,succ=S.build_dag(us)
 for i,ps in enumerate(pred):
  for j in ps:m.Add(ts[i]>ts[j])
 for i,t in enumerate(ts0):
  if t>=R:m.Add(ts[i]==t)
 m.Add(ts[index]==ts0[index]+delta);diff=[]
 for i,t in enumerate(ts):
  q=m.NewIntVar(0,2,f'd{i}');m.AddAbsEquality(q,t-ts0[i]);diff.append(q)
 m.Minimize(sum(diff));s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=1;s.parameters.cp_model_presolve=False
 st=s.Solve(m)
 if st not in(cp_model.FEASIBLE,cp_model.OPTIMAL):return None
 return tuple(s.Value(t)-t0 for t,t0 in zip(ts,ts0))

c,base,txt=evalc(c);best=base;seen=set()
for it in range(a.rounds):
 old=[o['t']for o in c['ops']];us=[unit(o)for o in c['ops']];macros=[];seenlocal=set()
 for i,o in enumerate(c['ops']):
  if o['t']>=c['meta']['R']:continue
  for delta in [-1,1]:
   dv=proposal(c,i,delta)
   if dv is None or dv in seenlocal:continue
   seenlocal.add(dv);d=copy.deepcopy(c)
   for j,x in enumerate(dv):d['ops'][j]['t']+=x
   d,r,txt=evalc(d);history.append(dict(iteration=it,kind='macro',index=i,delta=delta,changed=sum(x!=0 for x in dv),**r))
   if r['total']<best['total'] and r['exp_minus_A1']>=.5002:
    best=r;save(d,prefix+'_best');(H/(prefix+'_best.screen.json')).write_text(json.dumps(r,indent=2));append_result(prefix+'_best',r,'Exact-priced CP-SAT timing macro; judge and runtime pending.');print('best macro',counter,r,flush=True)
   # Include adverse moves: a combination may cancel shared harmful exposure.
   if r['exp_minus_A1']>.495 and r['total']-base['total']<2e-6:macros.append((dv,r))
 print('priced',it,len(macros),'of',len(seenlocal),flush=True)
 m=cp_model.CpModel();bs=[m.NewBoolVar(f'm{k}')for k in range(len(macros))];ts=[]
 for i,t in enumerate(old):
  v=m.NewIntVar(max(0,t-2),min(max(old),t+2),f't{i}');m.Add(v==t+sum(dv[i]*b for (dv,r),b in zip(macros,bs)if dv[i]));ts.append(v)
 pred,succ=S.build_dag(us)
 for i,ps in enumerate(pred):
  for j in ps:m.Add(ts[i]>ts[j])
 m.Add(sum(bs)>=1);m.Add(sum(bs)<=8)
 scale=10**12;loss=sum(round((r['total']-base['total'])*scale)*b for (dv,r),b in zip(macros,bs));penalties=[]
 # Exact A1 is nonlinear in finite-p gaps. Master approximation is screened again.
 m.Add(sum(round((-math.log(r['exp_minus_A1'])+math.log(base['exp_minus_A1']))*1e8)*b for(dv,r),b in zip(macros,bs))<=round((-math.log(.5002)+math.log(base['exp_minus_A1']))*1e8))
 for trial in range(a.trials):
  m.Minimize(loss+sum(penalties));s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=5;s.parameters.cp_model_presolve=False;st=s.Solve(m)
  if st not in(cp_model.FEASIBLE,cp_model.OPTIMAL):break
  selected=[i for i,b in enumerate(bs)if s.Value(b)];newtimes=[s.Value(t)for t in ts];d=copy.deepcopy(c)
  for o,t in zip(d['ops'],newtimes):o['t']=t
  d,r,txt=evalc(d);predicted=base['total']+sum(macros[i][1]['total']-base['total']for i in selected);residual=r['total']-predicted
  history.append(dict(iteration=it,kind='joint',selected=selected,predicted=predicted,residual=residual,**r));print('joint',it,trial,len(selected),r['total'],r['exp_minus_A1'],'residual',residual,flush=True)
  if r['total']<best['total'] and r['exp_minus_A1']>=.5002:
   best=r;save(d,prefix+'_best');(H/(prefix+'_best.screen.json')).write_text(json.dumps(r,indent=2));append_result(prefix+'_best',r,'Joint exact-loss CP-SAT incumbent; '+str(len(selected))+' macros. Judge and runtime pending.')
  # No-good excludes the evaluated decision. Residual conjunction reprices its supersets.
  m.AddBoolOr([bs[i].Not()if i in selected else bs[i]for i in range(len(bs))])
  if residual>0 and len(selected)>1:
   z=m.NewBoolVar(f'cut{trial}');m.AddBoolAnd([bs[i]for i in selected]).OnlyEnforceIf(z);m.AddBoolOr([bs[i].Not()for i in selected]).OnlyEnforceIf(z.Not());penalties.append(round(residual*scale)*z)
 with gzip.open(H/(prefix+'.witnesses.json.gz'),'wt')as f:json.dump(history,f)
 if best['total']>=base['total']-1e-12:break
 c=read(H/(prefix+'_best'));base=best
print('DONE',counter,best,flush=True)
