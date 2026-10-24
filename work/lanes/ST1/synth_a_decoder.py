"""Joint native A preparation/readout synthesis at a fixed complete round.

The A encoder is resynthesized so a two-CX destructive logical-X flag fits
without extending the data tail. Every emitted circuit is exact priced.
"""
from common import *
import argparse,gzip
p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--out',required=True);p.add_argument('--support',type=int,default=0);p.add_argument('--control',action='store_true');p.add_argument('--early-sources',action='store_true');p.add_argument('--retime-boundary',action='store_true');p.add_argument('--workers',type=int,default=4);p.add_argument('--seconds',type=float,default=30);p.add_argument('--attempts',type=int,default=30);p.add_argument('--cap',type=int,default=10);a=p.parse_args();base=json.loads(Path(a.stem).with_suffix('.plan.json').read_text());A=base['meta']['A'];D=base['meta']['data_qubits'];R=base['meta']['R'];gates=[]if a.control else[[(14,20),(13,14)],[(21,20),(27,21)]][a.support];index={q:i for i,q in enumerate(A)};reads={};contacts={};kept=[]
for o in base['ops']:
 u=unit(o);pair=S.name_qs(o['lines'][0])[1]
 if o.get('tag')=='A':continue
 if u.name=='CX'and pair in list(zip(D,A))and o['t']==R:contacts[pair[1]]=o;continue
 if u.name=='MEASURE'and u.qs[0]in A and o['t']>=R:reads[u.qs[0]]=o;continue
 kept.append(o)
assert len(reads)==len(contacts)==7
previous={q:max((o for o in kept if q in unit(o).qs and o['t']<R),key=lambda o:o['t'])for q in A};assert all(unit(o).name in('MEASURE','MX')for o in previous.values()),previous
if a.early_sources:
 for q,last in previous.items():
  before=[o['t']for o in kept if q in unit(o).qs and o['t']<last['t']];last['t']=max(before)+1
bits={q:int(re.search(r'c\[(\d+)\]',o['lines'][0])[1])for q,o in reads.items()};dets=[set(map(int,re.findall(r'c\[(\d+)\]',l)))for l in base['tail']if l.startswith('// DETECTOR')]
for u,v in gates:
 for row in dets:
  if bits[v]in row:row.symmetric_difference_update({bits[u]})
flags=[q for q in A if all(bits[q]not in r for r in dets)];assert len(flags)==int(not a.control)
m=cp_model.CpModel();piv=[m.NewBoolVar('plus'+str(q))for q in A];m.Add(sum(piv)==4);times=list(range(max(0,R-7),R));edges=[(i,j)for i,q in enumerate(A)for j,h in enumerate(A)if abs(q//6-h//6)+abs(q%6-h%6)==1];G={(t,i,j):m.NewBoolVar(f'g{t}_{i}_{j}')for t in times for i,j in edges};state=[[[m.NewBoolVar(f'x{t}_{i}_{j}')for j in range(7)]for i in range(7)]for t in range(len(times)+1)]
ki={id(o):i for i,o in enumerate(kept)};kt=[];movement=[];lastwire={}
for k,o in enumerate(kept):
 old=o['t'];delta=3 if a.retime_boundary and old<R else 0;t=m.NewIntVar(max(0,old-delta),min(R-1,old+delta)if delta else old,'kept'+str(k));kt.append(t);mv=m.NewIntVar(0,3,'shift'+str(k));m.AddAbsEquality(mv,t-old);movement.append(mv);m.AddHint(t,old)
 for q in unit(o).qs:
  if q in lastwire:m.Add(t>kt[lastwire[q]])
  lastwire[q]=k
for i in range(7):
 for j in range(7):m.Add(state[0][i][j]==(piv[i]if i==j else 0))
ct=[]
for i,q in enumerate(A):
 t=m.NewIntVar(R-4,R,'contact'+str(q));ct.append(t);touch=[R+j for j,e in enumerate(gates)if q in e];m.Add(t<min(touch))if touch else m.Add(t==R)
 prior=max((o for o in kept if D[i]in unit(o).qs and o['t']<R),key=lambda o:o['t']);m.Add(t>kt[ki[id(prior)]])
for ti,t in enumerate(times):
 for i,q in enumerate(A):
  incident=[g for(tt,u,v),g in G.items()if tt==t and i in(u,v)];m.Add(sum(incident)<=1);old=previous[q];basis=unit(old).name=='MX'
  for g in incident:
   m.Add(ct[i]>t).OnlyEnforceIf(g)
   m.Add(t>kt[ki[id(old)]]).OnlyEnforceIf(g);m.Add(t>=kt[ki[id(old)]]+2).OnlyEnforceIf([g,piv[i].Not()if basis else piv[i]])
  incoming=[G[t,u,v]for u,v in edges if v==i]
  for j in range(7):
   m.Add(state[ti+1][i][j]==state[ti][i][j]).OnlyEnforceIf([g.Not()for g in incoming])
   for u,v in edges:
    if v==i:m.AddAllowedAssignments([state[ti][i][j],state[ti][u][j],state[ti+1][i][j]],[(0,0,0),(0,1,1),(1,0,1),(1,1,0)]).OnlyEnforceIf(G[t,u,v])
for row in[[0,2,4,6],[1,2,5,6],[3,4,5,6]]:
 for j in range(7):m.AddBoolXOr([state[-1][i][j]for i in row]+[True])
m.Add(sum(G.values())<=a.cap);m.Minimize(10000*sum(G.values())+sum((R-t)*g for(t,i,j),g in G.items())+sum(R-t for t in ct)+sum(movement));assert not m.Validate(),m.Validate();decisions=piv+list(G.values());results=[];modelpath=H/(a.out+'.model.pbtxt');m.ExportToFile(str(modelpath))
with gzip.open(H/(a.out+'.model.pbtxt.gz'),'wb')as z:z.write(modelpath.read_bytes())
modelpath.unlink()
for attempt in range(a.attempts):
 s=cp_model.CpSolver();s.parameters.num_workers=a.workers;s.parameters.max_time_in_seconds=a.seconds;s.parameters.random_seed=attempt+1901;st=s.Solve(m)
 if st not in(cp_model.OPTIMAL,cp_model.FEASIBLE):print('STOP',s.StatusName(st),flush=True);break
 selected=[(t,A[i],A[j])for(t,i,j),g in G.items()if s.Value(g)];pv=[bool(s.Value(v))for v in piv];c=copy.deepcopy(base);c['ops']=copy.deepcopy(kept)
 for k,o in enumerate(c['ops']):o['t']=s.Value(kt[k])
 for i,q in enumerate(A):
  own=[t for t,u,v in selected if q in(u,v)];first=min(own);old=previous[q]
  if pv[i]!=(unit(old).name=='MX'):c['ops'].append(dict(t=first-1,lines=[f'reset q[{q}];']+([f'h q[{q}];']if pv[i]else[]),tag='A'))
  con=copy.deepcopy(contacts[q]);con['t']=s.Value(ct[i]);c['ops'].append(con);read=copy.deepcopy(reads[q]);tt=[R+j+1 for j,e in enumerate(gates)if q in e];read['t']=max(tt)if tt else R+1
  if q in flags:read['lines']=[f'h q[{q}];',f'measure q[{q}] -> c[{bits[q]}];',f'h q[{q}];']
  c['ops'].append(read)
 for t,u,v in selected:c['ops'].append(dict(t=t,lines=[f'cx q[{u}],q[{v}];'],tag='A'))
 for j,(u,v)in enumerate(gates):c['ops'].append(dict(t=R+j,lines=[f'cx q[{u}],q[{v}];'],tag='A_decoder'))
 c['tail']=[l for l in base['tail']if not l.startswith('// DETECTOR')]+['// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(row))for row in dets]+[f'// DETECTOR c[{bits[q]}]'for q in flags];c['meta']['A_resynthesis']=dict(encoder=selected,plus=[q for q,v in zip(A,pv)if v],decoder=gates,flag=flags);name=a.out+f'_{attempt}';r=dict(name=name,status=s.StatusName(st),encoder_cx=len(selected),encoder=selected,plus=c['meta']['A_resynthesis']['plus'])
 try:stem=save(c,name);r.update(score(stem))
 except Exception as e:r['error']=repr(e)
 results.append(r);append_result(name,r,'Joint A encoder and destructive logical-X readout synthesis on the complete R38 new geometry. Rank-four X generator space constrained to Steane |+L>; native cell/time constraints and full fault pricing determine validity. No extra final data step.');print(json.dumps(r),flush=True)
 with gzip.open(H/(a.out+'.witnesses.jsonl.gz'),'at')as z:z.write(json.dumps(dict(result=r,plan=c))+'\n')
 m.AddForbiddenAssignments(decisions,[[s.Value(v)for v in decisions]])
 if r.get('total',1)<4.8e-5 and r.get('exp_minus_A1',0)>=.5002:break
(H/(a.out+'.receipt.json')).write_text(json.dumps(dict(results=results,status=s.StatusName(st),stats=s.ResponseStats(),args=vars(a)),indent=2))
