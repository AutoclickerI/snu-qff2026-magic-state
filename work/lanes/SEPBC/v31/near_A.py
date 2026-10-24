from earlier_A import *

def near(c,Rnew):
 c=copy.deepcopy(c);ops=c['ops'];us=[unit(o)for o in ops];R=c['meta']['R'];m=cp_model.CpModel();tv=[m.NewIntVar(0,R+2,f't{i}')for i in range(len(ops))];by={}
 for j,u in enumerate(us):
  if ops[j]['t']>=R:m.Add(tv[j]==Rnew+ops[j]['t']-R)
  else:m.Add(tv[j]<Rnew)
  for q in u.qs:by.setdefault(q,[]).append(j)
  for i in range(j):
   if not set(us[i].qs)&set(u.qs):continue
   commute=False
   if us[i].name==u.name=='CX'and 27<=ops[i]['t']<R and 27<=ops[j]['t']<R:
    a,b=map(int,S.QRE.findall(us[i].lines[0]));d,e=map(int,S.QRE.findall(u.lines[0]));commute=a!=e and d!=b
   if not commute:m.Add(tv[j]>tv[i])
 for seq in by.values():m.AddAllDifferent([tv[i]for i in seq])
 dev=[]
 for i,o in enumerate(ops):
  target=o['t']+(Rnew-R if o.get('tag')in('encoder_bc','encoder_a','round')else 0);d=m.NewIntVar(0,60,f'd{i}');m.AddAbsEquality(d,tv[i]-target);dev.append(d)
 m.Minimize(sum(dev));s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=15;st=s.Solve(m);rec=dict(status=s.StatusName(st),R=Rnew,objective=s.ObjectiveValue(),bound=s.BestObjectiveBound())
 if st not in(cp_model.OPTIMAL,cp_model.FEASIBLE):return None,rec
 for i,o in enumerate(ops):o['t']=s.Value(tv[i])
 c['meta']['R']=Rnew;return c,rec
if __name__=='__main__':
 for source,tag in [('full_port','port'),('full_timing_0','timing')]:
  base=json.loads((V/(source+'.plan.json')).read_text())
  for check8,check14 in [(False,False),(True,False),(True,True)]:
   name=f'A44_{tag}_{int(check8)}{int(check14)}'
   try:
    c=variant(base,check8,check14);out,r=near(c,44)
    if out:st=save(out,'v31/'+name);r['screen']=score(st)
    (V/(name+'.build.json')).write_text(json.dumps(r,indent=2));append_result(name,r,'R44 with reoriented A inputs; retain prior prefix timing and shift ancilla timing targets one step earlier.');print(name,json.dumps(r),flush=True)
   except Exception as e:print(name,repr(e),flush=True)
