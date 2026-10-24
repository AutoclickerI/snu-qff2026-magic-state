"""Commute native prefix/encoder/decoder operations and preserve late B check."""
from context76 import *
import argparse,gzip
p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--out',required=True);p.add_argument('--workers',type=int,default=2);p.add_argument('--round',type=int);p.add_argument('--commute',action='store_true');a=p.parse_args();c=json.loads(Path(a.stem).with_suffix('.plan.json').read_text());ops=c['ops'];oldR=c['meta']['R'];A=c['meta']['A'];B=c['meta']['B'];C=c['meta']['C'];D=c['meta']['data_qubits'];m=cp_model.CpModel();R=m.NewIntVar(28,oldR,'R');ts=[m.NewIntVar(0,oldR+2,'t'+str(i))for i in range(len(ops))]
if a.round is not None:m.Add(R==a.round)
if a.commute:commuting_precedence(m,ops,ts)
else:
 last={}
 for i,o in enumerate(ops):
  for q in unit(o).qs:
   if q in last:m.Add(ts[i]>ts[last[q]])
   last[q]=i
for pair,offset in [(z,0)for z in zip(B,C)]+[(z,1)for z in zip(B,D)]:
 i=max((i for i,o in enumerate(ops)if unit(o).name=='CX'and S.name_qs(o['lines'][0])[1]==pair),key=lambda i:ops[i]['t']);m.Add(ts[i]==R+offset)
for q in B+C:
 i=max((i for i,o in enumerate(ops)if q in unit(o).qs),key=lambda i:ops[i]['t']);assert unit(ops[i]).name in('MEASURE','MX');m.Add(ts[i]==R+ops[i]['t']-oldR)
for i,t in enumerate(ts):m.Add(t<=R+2);m.AddHint(t,min(oldR+2,ops[i]['t']))
s=cp_model.CpSolver();s.parameters.num_workers=a.workers;s.parameters.max_time_in_seconds=60;assert not m.Validate(),m.Validate();m.Minimize(R);st=s.Solve(m);receipt=dict(status=s.StatusName(st),minimum_round=s.Value(R)if st in(cp_model.OPTIMAL,cp_model.FEASIBLE)else None,stats=s.ResponseStats(),args=vars(a));print(json.dumps(receipt),flush=True)
if st in(cp_model.OPTIMAL,cp_model.FEASIBLE):
 rr=s.Value(R);m.Add(R==rr);moves=[]
 for i,o in enumerate(ops):v=m.NewIntVar(0,oldR+2,'move'+str(i));m.AddAbsEquality(v,ts[i]-o['t']);moves.append(v)
 m.Minimize(sum(moves));st=s.Solve(m)
 if st in(cp_model.OPTIMAL,cp_model.FEASIBLE):
  for i,o in enumerate(ops):o['t']=s.Value(ts[i])
  comp={t:i for i,t in enumerate(sorted({o['t']for o in ops}))};c['meta']['R']=comp[rr]
  try:stem=save(c,'p76/'+a.out);receipt.update(rank(stem,a.workers));receipt['R']=comp[rr]
  except Exception as e:receipt['error']=repr(e)
(OUT/(a.out+'.receipt.json')).write_text(json.dumps(receipt,indent=2));append_result(a.out,receipt,'Whole native instrument commutation retiming; all prefix checks, guards, encoder and decoder retained. C→B verification immediately precedes B→D; complete full-order expectation. No proxy score is used to rank.');print(json.dumps(receipt),flush=True)
