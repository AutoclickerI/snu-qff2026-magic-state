"""Co-synthesize the native A encoder, pivots, logical-X flag and incoming timing.

Exact CX commutation, rather than a whole-A-before-data barrier, defines the
instrument. This first rung fixes the geometry, to audit the earlier closure.
"""
from context76 import *
import argparse,gzip
p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--out',required=True);p.add_argument('--round',type=int,default=38);p.add_argument('--support',type=int,default=0);p.add_argument('--workers',type=int,default=4);p.add_argument('--seconds',type=float,default=60);p.add_argument('--attempts',type=int,default=6);p.add_argument('--cap',type=int,default=14);p.add_argument('--commute-prefix',action='store_true');p.add_argument('--flag-objective',action='store_true');p.add_argument('--decoder');p.add_argument('--hint');a=p.parse_args();base=json.loads(Path(a.stem).with_suffix('.plan.json').read_text());A=base['meta']['A'];D=base['meta']['data_qubits'];oldR=base['meta']['R'];R=a.round;gates=[tuple(map(int,z.split(':')))for z in a.decoder.split(',')]if a.decoder else[[(14,20),(13,14)],[(21,20),(27,21)]][a.support];reads={};contacts={};kept=[]
for o in base['ops']:
 u=unit(o);pair=S.name_qs(o['lines'][0])[1]
 if o.get('tag')=='A':continue
 if u.name=='CX'and pair in list(zip(D,A))and o['t']==oldR:contacts[pair[1]]=o;continue
 if u.name=='MEASURE'and u.qs[0]in A and o['t']>=oldR:reads[u.qs[0]]=o;continue
 kept.append(o)
assert len(reads)==len(contacts)==7
previous={q:max((o for o in kept if q in unit(o).qs and o['t']<oldR),key=lambda o:o['t'])for q in A};assert all(unit(o).name in('MEASURE','MX')for o in previous.values())
bits={q:int(re.search(r'c\[(\d+)\]',o['lines'][0])[1])for q,o in reads.items()};dets=[set(map(int,re.findall(r'c\[(\d+)\]',l)))for l in base['tail']if l.startswith('// DETECTOR')]
for u,v in gates:
 for row in dets:
  if bits[v]in row:row.symmetric_difference_update({bits[u]})
flags=[q for q in A if all(bits[q]not in r for r in dets)];assert len(flags)==1;pull={flags[0]}
for u,v in reversed(gates):
 if u in pull:pull.symmetric_difference_update({v})
support=[A.index(q)for q in pull];assert len(support)==3 and ((support[0]+1)^(support[1]+1)^(support[2]+1))==0
m=cp_model.CpModel();piv=[m.NewBoolVar('plus'+str(q))for q in A];m.Add(sum(piv)==4);times=list(range(max(0,R-12),R));edges=[(i,j)for i,q in enumerate(A)for j,h in enumerate(A)if abs(q//6-h//6)+abs(q%6-h%6)==1];G={(t,i,j):m.NewBoolVar(f'g{t}_{i}_{j}')for t in times for i,j in edges};state=[[[m.NewBoolVar(f'x{t}_{i}_{j}')for j in range(7)]for i in range(7)]for t in range(len(times)+1)]
ki={id(o):i for i,o in enumerate(kept)};kt=[];movement=[];lastwire={}
for k,o in enumerate(kept):
 old=o['t'];t=m.NewIntVar(0,R if unit(o).name=='TDG'else R-1,'kept'+str(k))if old<oldR else m.NewIntVar(R+old-oldR,R+old-oldR,'kept'+str(k));kt.append(t);mv=m.NewIntVar(0,R+oldR,'shift'+str(k));m.AddAbsEquality(mv,t-old);movement.append(mv);m.AddHint(t,min(R-1,old)if old<oldR else R+old-oldR)
 for q in unit(o).qs:
  if q in lastwire and not a.commute_prefix:m.Add(t>kt[lastwire[q]])
  lastwire[q]=k
if a.commute_prefix:commuting_precedence(m,kept,kt)
dt=[m.NewIntVar(R-3,R+1,f'dec{j}')for j in range(len(gates))]
for i in range(1,len(dt)):m.Add(dt[i]>dt[i-1])
for i in range(7):
 for j in range(7):m.Add(state[0][i][j]==(piv[i]if i==j else 0))
ct=[];rt=[]
for i,q in enumerate(A):
 t=m.NewIntVar(R-1,R,'contact'+str(q));ct.append(t);read=m.NewIntVar(0,R+2,'read'+str(q));rt.append(read);m.Add(read>t);rel=kt[ki[id(previous[q])]];basis=unit(previous[q]).name=='MX';m.Add(t>rel);m.Add(t>=rel+2).OnlyEnforceIf(piv[i].Not()if basis else piv[i]);prior=max((o for o in kept if D[i]in unit(o).qs and o['t']<oldR and unit(o).name!='TDG'),key=lambda o:o['t']);m.Add(t>kt[ki[id(prior)]])
 for k,o in enumerate(kept):
  if D[i]in unit(o).qs and unit(o).name=='TDG':m.Add(t!=kt[k])
 for j,(u,v)in enumerate(gates):
  if q in(u,v):m.Add(t!=dt[j]);m.Add(read>dt[j])
  if q==u:m.Add(t<dt[j])
for ti,t in enumerate(times):
 for i,q in enumerate(A):
  incident=[g for(tt,u,v),g in G.items()if tt==t and i in(u,v)];m.Add(sum(incident)<=1);old=previous[q];basis=unit(old).name=='MX'
  for g in incident:m.Add(ct[i]!=t).OnlyEnforceIf(g);m.Add(rt[i]>t).OnlyEnforceIf(g);m.Add(t>kt[ki[id(old)]]).OnlyEnforceIf(g);m.Add(t>=kt[ki[id(old)]]+2).OnlyEnforceIf([g,piv[i].Not()if basis else piv[i]])
  incoming=[G[t,u,v]for u,v in edges if v==i]
  for j in range(7):
   m.Add(state[ti+1][i][j]==state[ti][i][j]).OnlyEnforceIf([g.Not()for g in incoming])
   for u,v in edges:
    if v==i:m.AddAllowedAssignments([state[ti][i][j],state[ti][u][j],state[ti+1][i][j]],[(0,0,0),(0,1,1),(1,0,1),(1,1,0)]).OnlyEnforceIf(G[t,u,v])
 for u,v in edges:
  g=G[t,u,v];m.Add(t<ct[u]).OnlyEnforceIf(g)
  for j,(c,d)in enumerate(gates):
   if A[u]in(c,d)or A[v]in(c,d):m.Add(t!=dt[j]).OnlyEnforceIf(g)
   if A[u]==d or A[v]==c:m.Add(t<dt[j]).OnlyEnforceIf(g)
for row in[[0,2,4,6],[1,2,5,6],[3,4,5,6]]:
 for j in range(7):m.AddBoolXOr([state[-1][i][j]for i in row]+[True])
phasecost=0
if a.flag_objective:
 from flag_objective import build
 phasecost=build(m,G,times,edges,A,piv,support)
if a.hint:
 hint=json.loads(Path(a.hint).read_text())['meta']['A_resynthesis'];sel={tuple(z)for z in hint['encoder']};pvset=set(hint['plus'])
 for i,q in enumerate(A):m.AddHint(piv[i],int(q in pvset))
 for(t,i,j),g in G.items():m.AddHint(g,int((t,A[i],A[j])in sel))
m.Add(sum(G.values())<=a.cap);decisions=piv+list(G.values());results=[];penalties={};s=cp_model.CpSolver();s.parameters.num_workers=a.workers;s.parameters.max_time_in_seconds=a.seconds;assert not m.Validate(),m.Validate();modelpath=OUT/(a.out+'.model.pbtxt');m.ExportToFile(str(modelpath))
with gzip.open(modelpath.with_suffix('.pbtxt.gz'),'wb')as z:z.write(modelpath.read_bytes())
modelpath.unlink()
for attempt in range(a.attempts):
 # Gate penalties are updated from flag-blind phase signatures; full all-orders
 # scores remain the rank. No scalar-danger or c1 pruning is performed.
 m.Minimize(10000*phasecost+sum((100+penalties.get((t,A[i],A[j]),0))*g for(t,i,j),g in G.items())+sum(movement)+1000*sum(R-t for t in ct)+sum(rt));s.parameters.random_seed=1901+attempt;st=s.Solve(m)
 if st not in(cp_model.OPTIMAL,cp_model.FEASIBLE):print('STOP',s.StatusName(st),flush=True);break
 selected=[(t,A[i],A[j])for(t,i,j),g in G.items()if s.Value(g)];pv=[bool(s.Value(v))for v in piv];c=copy.deepcopy(base);c['ops']=copy.deepcopy(kept)
 for k,o in enumerate(c['ops']):o['t']=s.Value(kt[k])
 for i,q in enumerate(A):
  own=[t for t,u,v in selected if q in(u,v)];first=min(own+[s.Value(ct[i])]);old=previous[q]
  if pv[i]!=(unit(old).name=='MX'):c['ops'].append(dict(t=first-1,lines=[f'reset q[{q}];']+([f'h q[{q}];']if pv[i]else[]),tag='A'))
  con=copy.deepcopy(contacts[q]);con['t']=s.Value(ct[i]);c['ops'].append(con);read=copy.deepcopy(reads[q]);read['t']=s.Value(rt[i])
  if q in flags:read['lines']=[f'h q[{q}];',f'measure q[{q}] -> c[{bits[q]}];',f'h q[{q}];']
  c['ops'].append(read)
 for t,u,v in selected:c['ops'].append(dict(t=t,lines=[f'cx q[{u}],q[{v}];'],tag='A'))
 for j,(u,v)in enumerate(gates):c['ops'].append(dict(t=s.Value(dt[j]),lines=[f'cx q[{u}],q[{v}];'],tag='A_decoder'))
 c['tail']=[l for l in base['tail']if not l.startswith('// DETECTOR')]+['// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(row))for row in dets]+[f'// DETECTOR c[{bits[q]}]'for q in flags];compact={t:i for i,t in enumerate(sorted({o['t']for o in c['ops']}))};c['meta']['R']=compact[R];profile,local=phase_profile(selected,[q for q,v in zip(A,pv)if v],A,support);c['meta']['A_resynthesis']=dict(encoder=selected,plus=[q for q,v in zip(A,pv)if v],decoder=[(u,v,s.Value(dt[j]))for j,(u,v)in enumerate(gates)],flag=flags,profile=profile);name=a.out+f'_{attempt}';r=dict(name=name,status=s.StatusName(st),encoder_cx=len(selected),profile=profile,cp_flag_units=s.Value(phasecost)if a.flag_objective else None)
 try:stem=save(c,'p76/'+name);r.update(rank(stem,a.workers))
 except Exception as e:r['error']=repr(e)
 results.append(r);append_result(name,r,'P76 commuting-precedence A/flag synthesis; full all-orders rank, fixed geometry first rung.');print(json.dumps(r),flush=True)
 with gzip.open(OUT/(a.out+'.witnesses.jsonl.gz'),'at')as z:z.write(json.dumps(dict(result=r,plan=c))+'\n')
 for key,value in local.items():penalties[key]=max(penalties.get(key,0),40*value)
 m.AddForbiddenAssignments(decisions,[[s.Value(v)for v in decisions]])
 if r.get('loss',1)<4.14605e-5 and r.get('acceptance',0)>=.5002:break
(OUT/(a.out+'.receipt.json')).write_text(json.dumps(dict(results=results,status=s.StatusName(st),stats=s.ResponseStats(),args=vars(a)),indent=2));print('COMPLETE',s.StatusName(st),len(results),flush=True)
