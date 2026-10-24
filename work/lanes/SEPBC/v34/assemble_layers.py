from release import *
def assemble(base,rec):
 c=copy.deepcopy(base);oldR=c['meta']['R'];R=rec['R'];kept=prefix(c);removed=[o for o in c['ops']if o.get('tag')=='encoder_a'and o not in kept];removed_bits={int(x)for o in removed for x in re.findall(r' -> c\[(\d+)\];',' '.join(o['lines']))}
 for b in removed_bits:
  refs=[l for l in c['tail']if re.search(rf'c\[{b}\]',l)];assert refs==[f'// DETECTOR c[{b}]'],(b,refs);c['tail'].remove(refs[0])
 tail=[o for o in c['ops']if o.get('tag')in('round','decoder')];b=bit(c);piv=set(rec['pivots']);rr=release(c);init=[]
 for q in A:
  if q not in piv and q not in((2,9)if c['meta'].get('route')=='via14'else(2,14)):continue
  reuse=rec['mode']%10>=3 and q in piv and q in((2,9)if c['meta'].get('route')=='via14'else(2,14))
  t=rr[q]['earliest']+1;lines=[f'reset q[{q}];']+([f'h q[{q}];']if q in piv else[])
  if not reuse:init.append(dict(lines=lines,t=t,tag='encoder_a'))
  else:t-=1
  if q in piv and(rec['mode']%10==0 or(rec['mode']%10 in(1,3)and q in(1,2,8))):
   init.append(dict(lines=[f'h q[{q}];',f'measure q[{q}] -> c[{b}];',f'h q[{q}];'],t=t+1,tag='encoder_a'));c['tail'].append(f'// DETECTOR c[{b}]');b+=1
 enc=[dict(lines=[f'cx q[{u}],q[{v}];'],t=t,tag='encoder_a')for t,u,v in sorted(rec['ops']+rec.get('bus',[]))]
 for o in tail:o['offset']=o['t']-oldR;o['t']=R+o['offset']
 c['ops']=kept+init+enc+tail;c['meta'].update(R=R,encoder_recipe=rec)
 for i,o in enumerate(c['ops']):o['id']=i
 c['h']=[re.sub(r'creg c\[\d+\]',f'creg c[{b}]',l)for l in c['h']]
 return c
def fit(c,seconds=8,cut=27,phases=False):
 c=copy.deepcopy(c);ops=c['ops'];us=[unit(o)for o in ops];R=c['meta']['R'];end=max([R+2]+[R+o['offset']for o in ops if'offset'in o]);m=cp_model.CpModel();ts=[m.NewIntVar(0,end,f't{i}')for i in range(len(ops))];by={};dev=[]
 for j,u in enumerate(us):
  o=ops[j]
  if 'offset'in o:m.Add(ts[j]==R+o['offset'])
  else:m.Add(ts[j]<R)
  for q in u.qs:by.setdefault(q,[]).append(j)
  for i in range(j):
   if not set(us[i].qs)&set(u.qs):continue
   commute=False
   if us[i].name==u.name=='CX'and ops[i]['t']>=cut and o['t']>=cut:
    a,b=map(int,S.QRE.findall(us[i].lines[0]));d,e=map(int,S.QRE.findall(u.lines[0]));commute=a!=e and d!=b
   if phases and ops[i]['t']>=cut and o['t']>=cut:
    for a,b in [(us[i],u),(u,us[i])]:
     if a.name=='CX'and b.name in('T','TDG','S','SDG','Z','X'):
      control,target=map(int,S.QRE.findall(a.lines[0]));commute|=b.qs[0]==(target if b.name=='X'else control)
   if not commute:m.Add(ts[j]>ts[i])
  target=o['t'];z=m.NewIntVar(0,60,f'd{j}');m.AddAbsEquality(z,ts[j]-target);dev.append(z*(3 if o.get('tag')in('prefix','data_hops','wait_guard')else 1));m.AddHint(ts[j],min(end,target))
 for seq in by.values():m.AddAllDifferent([ts[i]for i in seq])
 m.Minimize(sum(dev));s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=seconds;s.parameters.cp_model_presolve=False;st=s.Solve(m);r=dict(status=s.StatusName(st),R=R,seconds=s.WallTime(),objective=s.ObjectiveValue(),bound=s.BestObjectiveBound())
 if st not in(cp_model.OPTIMAL,cp_model.FEASIBLE):return None,r
 for i,o in enumerate(ops):o['t']=s.Value(ts[i])
 return fix(c),r
if __name__=='__main__':
 from mutations import route14
 recs=json.loads((V/'layer_recipes.json').read_text());rows=[]
 for i,rec in enumerate(recs):
  if rec['mode']%10>=3:continue
  base=route14(getbase(0))if rec['mode']>=10 else getbase(0)
  name=f'layer_{i}_R{rec["R"]}_m{rec["mode"]}';c=assemble(base,rec);d,r=fit(c);row=dict(stem=name,recipe=rec,schedule=r)
  if d:
   try:st,z=write(d,name,'Time-aware seven-cell A encoder. All original source-zero detectors retained; X-input verification follows the recorded mode. Decoder and its early D couplings are included in scheduling.');row['screen']=z
   except Exception as e:row['error']=repr(e);print(name,repr(e),flush=True)
  else:print(name,r,flush=True)
  rows.append(row);(V/'layer_builds.json').write_text(json.dumps(rows,indent=2))
