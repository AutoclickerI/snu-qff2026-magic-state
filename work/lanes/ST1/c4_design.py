"""Complete cultivation + A/B encoders + four parity-ancilla verification.
Each B wire couples to data at the very next native step after its last verifier CX.
"""
from common import *
import redesign as rd,argparse,collections,gzip
CHECKS=[[0,1,2],[0,3,4],[0,5,6],[1,3,5]];ROWS=rd.ROWS;ED=rd.ED

def create(a):
 pre,tail=rd.prefix(a.prefix_variant);cells=sorted({q for u in pre for q in u.qs});embs=rd.mappings(cells);m=cp_model.CpModel();H=a.max_round
 V=lambda lo,hi,n:m.NewIntVar(lo,hi,n)
 R=V(28,H,'R');xs=[];ys=[]
 def occ(p,start,end,name):
  s=V(0,H+3,name+'s');e=V(0,H+3,name+'e');d=V(0,H+3,name+'len');m.Add(s==start);m.Add(e==end);m.Add(d==e-s);xs.append(m.NewFixedSizeIntervalVar(p,1,name+'cell'));ys.append(m.NewIntervalVar(s,d,e,name+'life'))
 em=V(0,len(embs)-1,'embedding');mp={q:V(0,35,'prefix_cell'+str(q))for q in cells}
 if a.free_prefix:m.Add(em==0)
 else:
  m.AddAllowedAssignments([em]+list(mp.values()),[[i]+e['cells']for i,e in enumerate(embs)])
  if not a.b_catalog and not a.world_fixed:m.AddAllowedAssignments([em],[(i,)for i,e in enumerate(embs)if e['sym']==0])
 pt=[V(0,H-1,'pt'+str(i))for i in range(len(pre))];per=collections.defaultdict(list);pl=[];segments=[];cur={}
 for i,u in enumerate(pre):
  loc=[];m.Add(pt[i]<R)
  for q in u.qs:
   per[q].append(i)
   if u.name in('RESET','RX'):
    cur[q]=dict(pos=V(0,35,'segment'+str(len(segments)))if a.free_prefix else mp[q],units=[]);segments.append(cur[q])
   cur[q]['units'].append(i);loc.append(cur[q]['pos'])
  pl.append(loc)
  if a.free_prefix and u.name=='CX':m.AddAllowedAssignments(loc,ED)
 if a.fixed_prefix:
  pred,_=S.build_dag(pre);fixed=[]
  for ps in pred:fixed.append(max([fixed[j]+1 for j in ps]+[0]))
  for q,seq in per.items():
   for i,j in zip(seq,seq[1:]):
    if pre[i].name in('RESET','RX'):fixed[i]=fixed[j]-1
  for v,t in zip(pt,fixed):m.Add(v==t)
 for q,seq in per.items():
  for i,j in zip(seq,seq[1:]):m.Add(pt[j]>pt[i])
  if a.free_prefix:m.Add(mp[q]==cur[q]['pos'])
 for i,seg in enumerate(segments):occ(seg['pos'],pt[seg['units'][0]],pt[seg['units'][-1]]+1,'prefix'+str(i))
 if a.free_prefix and not a.b_catalog and not a.world_fixed:m.AddAllowedAssignments([segments[0]['pos']],[(q,)for q in[0,1,2,7,8,14]])
 release={k:[V(0,H+3,k+'release'+str(i))for i in range(len(CHECKS)if k=='c'else 7)]for k in'abc'};dp=[V(0,6,'data_perm'+str(i))for i in range(7)];m.AddAllowedAssignments(dp,rd.AUT if a.data_auto else [list(range(7))]);pe=[V(0,H,'prefix_end'+str(i))for i in range(7)]
 for i,q in enumerate(rd.PD):m.Add(pe[i]==pt[per[q][-1]]+1)
 T={};enc={k:rd.encoder(a.encoder,k)for k in'ab'};jobs=[];last={}
 for k,n in [('d',7),('a',7),('b',7),('c',len(CHECKS))]:
  for i in range(n):
   key=k+str(i);K=a.data_moves if k=='d'else a.check_moves if k=='c'else a.b_moves if k=='b'and a.b_moves is not None else a.moves;ps=[V(0,35,key+'p'+str(j))for j in range(K+1)];init=V(0,H-1,key+'init');ts=[];zs=[]
   if k=='d':m.AddElement(dp[i],[mp[q]for q in rd.PD],ps[0]);m.AddElement(dp[i],pe,init)
   for j in range(K):
    z=m.NewBoolVar(key+'m'+str(j));t=V(1,H-1,key+'t'+str(j));m.AddAllowedAssignments([ps[j],ps[j+1],z],[(u,v,1)for u,v in ED]+[(q,q,0)for q in range(36)]);m.Add(t>=init+(k!='d'))
    if j:m.Add(z<=zs[-1]);m.Add(t>=ts[-1]+(2 if k=='d'else 1)*zs[-1])
    ts.append(t);zs.append(z)
   m.Add(ts[-1]+(2 if k=='d'else 1)*zs[-1]<=R)
   for j in range(K+1):occ(ps[j],init if j==0 else ts[j-1]-zs[j-1],(release[k][i]if a.recycle_readouts and k!='d'else R+3)if j==K else ts[j]+(3 if k=='d'else 2)*zs[j],key+'_'+str(j))
   T[key]=dict(pos=ps,init=init,ts=ts,moves=zs);last[key]=init
 for k,flag in [('a',a.stationary_a),('b',a.stationary_b)]:
  if flag:
   for i in range(7):
    for z in T[k+str(i)]['moves']:m.Add(z==0)
 bcat=json.loads(Path(a.b_catalog).read_text())if a.b_catalog else None
 if bcat:
  for i,q in enumerate(bcat['native_b']):
   if a.b_endpoints:m.Add(T['b'+str(i)]['pos'][-1]==q)
   else:
    for v in T['b'+str(i)]['pos']:m.Add(v==q)
    for z in T['b'+str(i)]['moves']:m.Add(z==0)
  for j,detail in enumerate(bcat['check_routes']):
   path=detail[3];tok=T['c'+str(j)]
   for k,v in enumerate(tok['pos']):m.AddHint(v,path[min(k,len(path)-1)])
   for k,z in enumerate(tok['moves']):m.AddHint(z,int(k+1<len(path)))
 if a.external_b:
  for i in range(7):
   for seg in segments:m.Add(T['b'+str(i)]['pos'][0]!=seg['pos'])
 def at(tok,t,name):
  K=len(tok['moves']);s=V(0,K,name+'stage');p=V(0,35,name+'loc');m.AddElement(s,tok['pos'],p)
  for j in range(K+1):
   z=m.NewBoolVar(name+'eq'+str(j));m.Add(s==j).OnlyEnforceIf(z);m.Add(s!=j).OnlyEnforceIf(z.Not())
   if j:m.Add(tok['moves'][j-1]==1).OnlyEnforceIf(z);m.Add(t>=tok['ts'][j-1]+(2 if name[0]=='d'else 1)).OnlyEnforceIf(z)
   if j<K:m.Add(t<tok['ts'][j]).OnlyEnforceIf([z,tok['moves'][j]])
  return p,s
 for k in'dab':
  for gi,inds in enumerate([(i,)for i in range(7)]if k=='d'else enc[k][0]):
   t=V(0,H-1,k+'g'+str(gi));m.Add(t<R);loc=[];st=[]
   for i in inds:
    key=k+str(i);m.Add(t>=last[key]+(k!='d'));last[key]=t;p,s=at(T[key],t,key+'g'+str(gi));loc.append(p);st.append(s)
    if a.stationary_prep and k!='d':m.Add(s==0)
   if k!='d':m.AddAllowedAssignments(loc,ED)
   jobs.append(dict(k=k,indices=list(inds),t=t,loc=loc,stage=st))
 if a.stationary_prep:
  from graph_embeddings import embeddings
  for k in'ab':m.AddAllowedAssignments([T[k+str(i)]['pos'][0]for i in range(7)],embeddings(tuple(tuple(e)for e in enc[k][0])))
 P={k:[V(0,6,k+'perm'+str(i))for i in range(7)]for k in'ab'};E={'d':[T['d'+str(i)]['pos'][-1]for i in range(7)]}
 for k in'ab':
  m.AddAllowedAssignments(P[k],rd.AUT)
  if k=='b'and bcat:
   for i,v in enumerate(P[k]):m.Add(v==bcat['permutation'][i])
  E[k]=[V(0,35,k+'end'+str(i))for i in range(7)]
  for i in range(7):m.AddElement(P[k][i],[T[k+str(j)]['pos'][-1]for j in range(7)],E[k][i])
 for i in range(7):
  for k in'ab':m.AddAllowedAssignments([E['d'][i],E[k][i]],ED)
 E['c']=[T['c'+str(i)]['pos'][-1]for i in range(len(CHECKS))];m.AddAllDifferent(E['d']if a.recycle_readouts else sum(E.values(),[]))
 checks=[];byb=collections.defaultdict(list);byc=collections.defaultdict(list)
 for j,row in enumerate(CHECKS):
  for i in row:
   t=V(0,H,'check'+str(j)+'_'+str(i));tok=T['c'+str(j)];m.Add(t>tok['init']);p,stage=at(tok,t,'c'+str(j)+'g'+str(i));m.AddAllowedAssignments([E['b'][i],p],ED);byb[i].append(t);byc[j].append(t);checks.append(dict(j=j,i=i,t=t,loc=p,stage=stage))
   for k in range(7):
    z=m.NewBoolVar(f'b{i}native{k}check{j}');m.Add(P['b'][i]==k).OnlyEnforceIf(z);m.Add(P['b'][i]!=k).OnlyEnforceIf(z.Not());m.Add(t>last['b'+str(k)]).OnlyEnforceIf(z);tk=T['b'+str(k)];m.Add(t>=tk['ts'][-1]+tk['moves'][-1]).OnlyEnforceIf(z)
 m.AddMaxEquality(R,[c['t']for c in checks]);endb=[];endc=[];enda=[]
 for i in range(7):
  t=V(0,H,'lastcheck'+str(i));m.AddMaxEquality(t,byb[i])if byb[i]else m.Add(t==R);t=R if a.sync_round else t;endb.append(t);at=V(0,H,'Acontact'+str(i));enda.append(at)
  if a.final_window>=0:m.Add(t>=R-a.final_window);m.Add(at>=R-a.final_window)
  m.Add(at<=t)if a.early_a else m.Add(at==t);tok=T['d'+str(i)];m.Add(at>last['d'+str(i)]);m.Add(at>=tok['ts'][-1]+2*tok['moves'][-1])
  for j in range(7):
   z=m.NewBoolVar(f'a{i}native{j}');m.Add(P['a'][i]==j).OnlyEnforceIf(z);m.Add(P['a'][i]!=j).OnlyEnforceIf(z.Not());m.Add(at>last['a'+str(j)]).OnlyEnforceIf(z);m.Add(release['a'][j]==at+2).OnlyEnforceIf(z);tk=T['a'+str(j)];m.Add(at>=tk['ts'][-1]+tk['moves'][-1]).OnlyEnforceIf(z)
  for j in range(7):
   z=m.NewBoolVar(f'brelease{i}_{j}');m.Add(P['b'][i]==j).OnlyEnforceIf(z);m.Add(P['b'][i]!=j).OnlyEnforceIf(z.Not());m.Add(release['b'][j]==t+3).OnlyEnforceIf(z)
 for j in range(len(CHECKS)):
  t=V(0,H,'lastC'+str(j));m.AddMaxEquality(t,byc[j]);m.Add(release['c'][j]==t+2);endc.append(t);tok=T['c'+str(j)];m.Add(tok['ts'][-1]+tok['moves'][-1]<=t)
 # Per-CX conflicts are needed even while both token lifetimes remain reserved.
 for seq in list(byb.values())+list(byc.values()):m.AddAllDifferent(seq)
 m.AddNoOverlap2D(xs,ys);move=sum((2 if k[0]=='d'else 1)*sum(v['moves'])for k,v in T.items());m.Add(move<=a.move_budget)
 if a.tail_objective:m.Minimize(1000*sum(R-t for t in enda)+4000*sum(R-t for t in endb)+4000*R+20*sum(R-v['init']for v in T.values())+50*move)
 else:m.Minimize(1000000*R+sum(R-v['init']for v in T.values())+sum(R-t for t in pt)+4*move)
 return m,dict(R=R,em=em,mp=mp,pt=pt,pl=pl,T=T,jobs=jobs,P=P,E=E,dp=dp,checks=checks,endb=endb,endc=endc,enda=enda),enc

def extract(cb,a,v,enc):
 val=lambda x:cb.Value(x)
 return dict(args=vars(a),checker_rows=CHECKS,R=val(v['R']),data_permutation=list(map(val,v['dp'])),embedding=val(v['em']),mapping={q:val(z)for q,z in v['mp'].items()},prefix_t=list(map(val,v['pt'])),prefix_locs=[list(map(val,vs))for vs in v['pl']],tokens={k:{n:list(map(val,z))if isinstance(z,list)else val(z)for n,z in tok.items()}for k,tok in v['T'].items()},jobs=[{n:list(map(val,z))if n in('loc','stage')else val(z)if n=='t'else z for n,z in j.items()}for j in v['jobs']],permutations={k:list(map(val,vs))for k,vs in v['P'].items()},endpoints={k:list(map(val,vs))for k,vs in v['E'].items()},checks=[{k:val(z)if k in('t','loc','stage')else z for k,z in c.items()}for c in v['checks']],enda=list(map(val,v['enda'])),endb=list(map(val,v['endb'])),endc=list(map(val,v['endc'])),encoders=enc)

def build(x,name):
 pre,tail=rd.prefix(x['args']['prefix_variant']);ops=[];bit=100
 def add(t,lines,tag,**kw):ops.append(dict(t=t,lines=lines,tag=tag,**kw))
 for i,(u,t)in enumerate(zip(pre,x['prefix_t'])):add(t,rename(u.lines,dict(zip(u.qs,x['prefix_locs'][i]))),'prefix')
 for key,tok in x['tokens'].items():
  k=key[0];i=int(key[1:]);q=tok['pos'][0]
  if k!='d':add(tok['init'],[f'reset q[{q}];']+([f'h q[{q}];']if k in'ab'and i in x['encoders'][k][1]else[]),'prep_init')
  for j,z in enumerate(tok['moves']):
   if not z:continue
   u,v=tok['pos'][j:j+2];t=tok['ts'][j];add(t-1,[f'reset q[{v}];']+([f'h q[{v}];']if k=='a'else[]),'move_init');aa,bb=(v,u)if k=='a'else(u,v);add(t,[f'cx q[{aa}],q[{bb}];'],'move_cx')
   if k=='d':add(t+1,[f'cx q[{v}],q[{u}];'],'data_cx');add(t+2,[f'measure q[{u}] -> c[{bit}];'],'data_watch');tail.append(f'// DETECTOR c[{bit}]');bit+=1
   else:add(t+1,([f'h q[{u}];']if k!='a'else[])+[f'measure q[{u}] -> c[{bit}];']+([f'h q[{u}];']if k!='a'else[]),'tele_m',destination=v,axis=0 if k=='a'else 1,bit=bit);bit+=1
 for j in x['jobs']:
  if j['k']=='d':add(j['t'],[f"tdg q[{j['loc'][0]}];"],'data_tdg')
  else:u,v=j['loc'];add(j['t'],[f'cx q[{u}],q[{v}];'],'encoder_'+j['k'])
 for c in x['checks']:add(c['t'],[f"cx q[{x['endpoints']['b'][c['i']]}],q[{c['loc']}];"],'verify')
 read={}
 for i,t in enumerate(x['endb']):
  d,a,b=(x['endpoints'][k][i]for k in'dab');ta=x['enda'][i];add(ta,[f'cx q[{d}],q[{a}];'],'round');add(t+1,[f'cx q[{b}],q[{d}];'],'round')
  for k,q,tt in [('a',a,ta+1),('b',b,t+2)]:add(tt,([f'h q[{q}];']if k=='b'else[])+[f'measure q[{q}] -> c[{bit}];'],'read',bit=bit);read[k,i]=bit;bit+=1
 for i,t in enumerate(x['endc']):q=x['endpoints']['c'][i];add(t+1,[f'measure q[{q}] -> c[{bit}];'],'read',bit=bit);read['c',i]=bit;bit+=1
 ops.sort(key=lambda o:(o['t'],o['tag']!='tele_m'));frames={q:[set(),set()]for q in range(36)};corr={}
 for o in ops:
  u=unit(o);qs=list(map(int,S.QRE.findall(o['lines'][0])))
  if u.name in('RESET','RX'):frames[qs[0]]=[set(),set()]
  elif u.name=='CX':a,b=qs;frames[b][0]^=frames[a][0];frames[a][1]^=frames[b][1]
  elif o['tag']=='tele_m':q=qs[0];axis=o['axis'];frames[o['destination']][axis]^=frames[q][axis]^{o['bit']};frames[q]=[set(),set()]
  elif o['tag']=='read':corr[o['bit']]=frames[qs[0]][1 if u.name=='MX'else 0].copy()
  elif u.name=='H':frames[qs[0]].reverse()
  elif u.name in('T','TDG'):assert not any(frames[qs[0]])
 assert all(not any(frames[q])for q in x['endpoints']['d'])
 for k,groups in [('a',ROWS),('b',ROWS),('c',[[i]for i in range(len(x['checker_rows']))])]:
  for g in groups:
   bs={read[k,i]for i in g}
   for i in g:bs^=corr[read[k,i]]
   tail.append('// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(bs)))
 for i,o in enumerate(ops):o['id']=i
 compact={t:i for i,t in enumerate(sorted({o['t']for o in ops}))};start=min(x['enda']);c=dict(h=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{bit}];'],ops=ops,tail=tail,meta=dict(data_qubits=x['endpoints']['d'],R=compact[start],R_last=compact[x['R']],source=f"new C{len(x['checker_rows'])} parity verification",checker_rows=x['checker_rows'],sync_round=x['args']['sync_round'],recycle_readouts=x['args']['recycle_readouts'],block_teleports=sum(sum(v['moves'])for k,v in x['tokens'].items()if k[0]!='d'),data_hops=sum(sum(v['moves'])for k,v in x['tokens'].items()if k[0]=='d')))
 return save(c,name)

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--prefix-variant',default='cats13');p.add_argument('--free-prefix',action='store_true');p.add_argument('--encoder',default='s34c15,s13c8');p.add_argument('--stationary-prep',action='store_true');p.add_argument('--stationary-a',action='store_true');p.add_argument('--stationary-b',action='store_true');p.add_argument('--recycle-readouts',action='store_true');p.add_argument('--data-auto',action='store_true');p.add_argument('--b-catalog');p.add_argument('--world-fixed',action='store_true');p.add_argument('--sync-round',action='store_true');p.add_argument('--b-endpoints',action='store_true');p.add_argument('--b-moves',type=int);p.add_argument('--external-b',action='store_true');p.add_argument('--early-a',action='store_true');p.add_argument('--final-window',type=int,default=-1);p.add_argument('--tail-objective',action='store_true');p.add_argument('--fixed-prefix',action='store_true');p.add_argument('--presolve',action='store_true');p.add_argument('--moves',type=int,default=2);p.add_argument('--data-moves',type=int,default=4);p.add_argument('--check-moves',type=int,default=3);p.add_argument('--move-budget',type=int,default=60);p.add_argument('--max-round',type=int,default=50);p.add_argument('--workers',type=int,default=8);p.add_argument('--seconds',type=float,default=600);p.add_argument('--seed',type=int,default=0);a=p.parse_args();m,v,enc=create(a);modelpath=H/(a.out+'.model.pbtxt');m.ExportToFile(str(modelpath))
 with gzip.open(H/(a.out+'.model.pbtxt.gz'),'wb')as z:z.write(modelpath.read_bytes())
 modelpath.unlink();s=cp_model.CpSolver();s.parameters.num_workers=a.workers;s.parameters.max_time_in_seconds=a.seconds;s.parameters.cp_model_presolve=a.presolve;s.parameters.random_seed=a.seed;count=0
 class CB(cp_model.CpSolverSolutionCallback):
  def on_solution_callback(self):
   nonlocal count
   x=extract(self,a,v,enc);name=a.out+f'_w{count}';count+=1;(H/(name+'.solver.json')).write_text(json.dumps(x,indent=1));row=dict(name=name,R=x['R'],objective=self.ObjectiveValue())
   try:stem=build(x,name);row.update(score(stem))
   except Exception as e:row['error']=repr(e)
   with gzip.open(H/(a.out+'.witnesses.jsonl.gz'),'at')as z:z.write(json.dumps(dict(result=row,plan=x))+'\n')
   append_result(name,row,'Complete C4 instrument with independent A/B preparation and moving cultivation boundary; exact score only after full native emitter/format and noiseless frontend.');print(json.dumps(row),flush=True)
 st=s.Solve(m,CB());r=dict(status=s.StatusName(st),stats=s.ResponseStats(),witnesses=count,args=vars(a));(H/(a.out+'.receipt.json')).write_text(json.dumps(r,indent=2));append_result(a.out,r,'C4 spacetime search; UNKNOWN is not an infeasibility certificate.');print(json.dumps(r),flush=True)
if __name__=='__main__':main()
