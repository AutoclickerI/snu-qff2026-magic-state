"""New full circuits: free cultivation embedding/timing, data routing and ABC.

No incumbent suffix is imported. The cultivation logical construction/checks
are retained; all ancilla blocks and the final round are built here.
"""
from common import *
import argparse,collections,gzip
ROWS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
PD=[0,20,7,4,3,15,8]
ED=[(q,p)for q in range(36)for p in range(36)if abs(q//6-p//6)+abs(q%6-p%6)==1]
AUT=[[((a if i&1 else 0)^(b if i&2 else 0)^(c if i&4 else 0))-1 for i in range(1,8)]for a in range(1,8)for b in range(1,8)for c in range(1,8)if len({a,b,c,a^b,a^c,b^c,a^b^c})==7]

def prefix(variant="base",keep_tdg=False):
 global PD
 text=(H/'inputs/cultivation19.qasm').read_text();head,raw,tail=S.qasm_ops(text);units=S.fold_units(raw);times=native_times(text,units);pre=[copy.deepcopy(u)for u,t in zip(units,times)if t<=29]
 bits={int(b)for u in pre for l in u.lines for b in re.findall(r'c\[(\d+)\]',l)}
 det=[l for l in tail if l.startswith('// DETECTOR')and set(map(int,re.findall(r'c\[(\d+)\]',l)))<=bits];gone=set();out=[]
 for u in pre:
  if u.name=='MEASURE'and any(int(b)>=39 for l in u.lines for b in re.findall(r'c\[(\d+)\]',l)):
   gone|=set(map(int,re.findall(r'c\[(\d+)\]',' '.join(u.lines))));u=Unit([f'reset q[{u.qs[0]}];'])
  out.append(u)
 det=[l for l in det if not(set(map(int,re.findall(r'c\[(\d+)\]',l)))&gone)]
 from prefix_macros import transform
 out,det,PD=transform(out,det,variant)
 if not keep_tdg:out=[u for u in out if not(u.name=='TDG'and u.qs[0]in PD)]
 assert len(det)==14+variant.split('+').count('release20')+variant.split('+').count('release15')
 seen=set()
 for u in out:
  if u.name=='CX':assert tuple(u.qs)in ED,('prefix adjacency',variant,u.lines)
  for q in u.qs:
   if q not in seen:assert u.name in('RESET','RX'),(q,u.lines);seen.add(q)
 return out,det

def mappings(cells):
 rows=[]
 for sym in range(8):
  def tf(q):
   r,c=divmod(q,6);return [(r,c),(r,-c),(-r,c),(-r,-c),(c,r),(c,-r),(-c,r),(-c,-r)][sym]
  xy=[tf(q)for q in cells];mr=min(r for r,c in xy);mc=min(c for r,c in xy);hh=max(r for r,c in xy)-mr+1;ww=max(c for r,c in xy)-mc+1
  for dr in range(7-hh):
   for dc in range(7-ww):rows.append(dict(sym=sym,row=dr,col=dc,cells=[(r-mr+dr)*6+c-mc+dc for r,c in xy]))
 assert rows
 return rows

def encoder(name,k):
 if ','in name:name=name.split(',')['abc'.index(k)]
 if name.startswith('s')and name!='std9':
  t=json.loads((H/'inputs/endstate_templates.json').read_text())[name]['plus'if k=='a'else'zero'];return t['ops'],t['pivots']
 if name=='std9':
  ops=[(0,2),(1,6),(3,5),(0,4),(1,2),(3,6),(0,6),(1,5),(3,4)];piv=[0,1,3]
 else:
  p=json.loads((H/'inputs'/('prep_l3_10.json'if name=='l3_10'else'prepA_L5_s7307.json')).read_text());cells=p.get('cells',[1,14,8,9,2,16,15]);ops=[(cells.index(v),cells.index(u))for L in p['ops']for u,v in L];piv=[i for i in range(7)if cells[i]not in p['pivots']]
 if k=='a':ops=[(v,u)for u,v in ops];piv=[i for i in range(7)if i not in piv]
 return ops,piv

def create(a):
 pre,dets=prefix(a.prefix_variant);cells=sorted({q for u in pre for q in u.qs});embs=mappings(cells);horizon=a.max_round;m=cp_model.CpModel();R=m.NewIntVar(a.min_round,a.max_round,'R');xx=[];yy=[]
 def V(lo,hi,name):return m.NewIntVar(lo,hi,name)
 def occ(pos,start,end,name):
  s=V(0,horizon+3,name+'s');e=V(0,horizon+3,name+'e');z=V(0,horizon+3,name+'len');m.Add(s==start);m.Add(e==end);m.Add(z==e-s);xx.append(m.NewFixedSizeIntervalVar(pos,1,name+'cell'));yy.append(m.NewIntervalVar(s,z,e,name+'life'))
 embed=V(0,len(embs)-1,'embedding');mapping={q:V(0,35,f'prefix_cell{q}')for q in cells}
 if not a.free_prefix:
  m.AddAllowedAssignments([embed]+list(mapping.values()),[[i]+p['cells']for i,p in enumerate(embs)])
  if a.embedding>=0:m.Add(embed==a.embedding)
  elif not a.catalog:m.AddAllowedAssignments([embed],[(i,)for i,e in enumerate(embs)if e['sym']==0])
 else:m.Add(embed==0)
 pt=[V(0,horizon-1,f'prefix_t{i}')for i in range(len(pre))];per=collections.defaultdict(list);pl=[];segments=[];current={}
 for i,u in enumerate(pre):
  m.Add(pt[i]<R);loc=[]
  for q in u.qs:
   per[q].append(i)
   if u.name in('RESET','RX'):
    pos=V(0,35,f'prefix_segment{len(segments)}')if a.free_prefix else mapping[q]
    current[q]=dict(pos=pos,units=[],logical=q);segments.append(current[q])
   seg=current[q];seg['units'].append(i);loc.append(seg['pos'])
  pl.append(loc)
  if a.free_prefix and u.name=='CX':m.AddAllowedAssignments(loc,ED)
 for q,seq in per.items():
  for i,j in zip(seq,seq[1:]):m.Add(pt[j]>pt[i])
 for si,seg in enumerate(segments):
  seq=seg['units'];occ(seg['pos'],pt[seq[0]],pt[seq[-1]]+1,f'prefix_segment{si}')
 if a.free_prefix:
  for q in cells:m.Add(mapping[q]==current[q]['pos'])
  if not a.catalog:m.AddAllowedAssignments([segments[0]['pos']],[(q,)for q in [0,1,2,7,8,14]])
 T={};J=[];decisions=[];enc={k:encoder(a.encoder,k)for k in'abc'};cat=json.loads(Path(a.catalog).read_text())if a.catalog else None
 if cat and 'blocks'in cat:
  enc={k:([(cat['initial'][k].index(u),cat['initial'][k].index(v))for u,v in cat['blocks'][k]['ops']],[cat['initial'][k].index(q)for q in cat['blocks'][k]['pivots']])for k in'abc'}
 for k in'dabc':
  for i in range(7):
   key=f'{k}{i}';K=a.data_moves if k=='d'else a.moves;ps=[V(0,35,key+f'p{j}')for j in range(K+1)];init=V(0,horizon-1,key+'init');ts=[];moves=[]
   if k=='d':m.Add(ps[0]==mapping[PD[i]]);m.Add(init==pt[per[PD[i]][-1]]+1)
   for j in range(K):
    z=m.NewBoolVar(key+f'm{j}');t=V(1,horizon-1,key+f't{j}');m.AddAllowedAssignments([ps[j],ps[j+1],z],[(u,v,1)for u,v in ED]+[(q,q,0)for q in range(36)]);m.Add(t>=init+(k!='d'))
    if j:m.Add(z<=moves[-1]);m.Add(t>=ts[-1]+(2 if k=='d'else 1)*moves[-1])
    ts.append(t);moves.append(z)
   m.Add(ts[-1]+(2 if k=='d'else 1)*moves[-1]<=R)
   for j in range(K+1):occ(ps[j],init if j==0 else ts[j-1]-moves[j-1],R+(3 if k in'bd'else 2)if j==K else ts[j]+(3 if k=='d'else 2)*moves[j],key+f'_{j}')
   T[key]=dict(pos=ps,init=init,ts=ts,moves=moves);decisions+=ps+moves
 if a.prep_before_moves and not a.catalog:
  from graph_embeddings import embeddings
  for k in 'abc':m.AddAllowedAssignments([T[f'{k}{i}']['pos'][0]for i in range(7)],embeddings(tuple(tuple(e)for e in enc[k][0])))
 if a.compact9:
  assert a.encoder=='std9'and a.moves>=a.external_moves+2
  coords=[(0,1),(1,2),(0,2),(1,0),(0,0),(2,0),(1,1),(2,1),(2,2)];patterns=[]
  for sym in range(8):
   def tf(r,c):return [(r,c),(r,2-c),(2-r,c),(2-r,2-c),(c,r),(c,2-r),(2-c,r),(2-c,2-r)][sym]
   for dr in range(4):
    for dc in range(4):patterns.append([(rr+dr)*6+cc+dc for r,c in coords for rr,cc in[tf(r,c)]])
  for k in'abc':
   m.AddAllowedAssignments([T[f'{k}{i}']['pos'][0]for i in range(7)]+T[f'{k}5']['pos'][1:3],patterns)
   m.Add(T[f'{k}5']['moves'][0]==1);m.Add(T[f'{k}5']['moves'][1]==1)
   for i in range(7):
    cap=(2 if i==5 else 0)+a.external_moves
    if cap<a.moves:m.Add(T[f'{k}{i}']['moves'][cap]==0)
 for k in'dabc':
  jobs=[(i,)for i in range(7)]if k=='d'else enc[k][0];last={i:T[f'{k}{i}']['init']for i in range(7)}
  for gi,indices in enumerate(jobs):
   t=V(0,horizon-1,f'{k}g{gi}t');m.Add(t<R);loc=[];stages=[]
   for i in indices:
    tok=T[f'{k}{i}'];K=len(tok['moves']);stage=V(0,K,f'{k}g{gi}s{i}');p=V(0,35,f'{k}g{gi}p{i}');m.AddElement(stage,tok['pos'],p);m.Add(t>=last[i]+(k!='d'));last[i]=t;loc.append(p);stages.append(stage)
    if a.catalog or a.prep_before_moves:m.Add(stage==0)if k!='d'else None
    if a.compact9 and k!='d':m.Add(stage==(2 if i==5 and next(v for v in indices if v!=i)==1 else 0))
    for j in range(K+1):
     z=m.NewBoolVar(f'{k}g{gi}s{i}eq{j}');m.Add(stage==j).OnlyEnforceIf(z);m.Add(stage!=j).OnlyEnforceIf(z.Not())
     if j:m.Add(tok['moves'][j-1]==1).OnlyEnforceIf(z);m.Add(t>=tok['ts'][j-1]+(2 if k=='d'else 1)).OnlyEnforceIf(z)
     if j<K:m.Add(t<tok['ts'][j]).OnlyEnforceIf([z,tok['moves'][j]])
   if k!='d':m.AddAllowedAssignments(loc,ED)
   J.append(dict(k=k,indices=list(indices),t=t,loc=loc,stage=stages));decisions+=stages
 P={k:[V(0,6,f'{k}perm{i}')for i in range(7)]for k in'abc'};E={'d':[T[f'd{i}']['pos'][-1]for i in range(7)]}
 for k in'abc':
  m.AddAllowedAssignments(P[k],AUT);E[k]=[V(0,35,f'{k}end{i}')for i in range(7)]
  for i in range(7):m.AddElement(P[k][i],[T[f'{k}{j}']['pos'][-1]for j in range(7)],E[k][i])
 for i in range(7):
  for k,l in[('d','a'),('d','b'),('b','c')]:m.AddAllowedAssignments([E[k][i],E[l][i]],ED)
 m.AddAllDifferent(sum(E.values(),[]));m.AddNoOverlap2D(xx,yy)
 if a.catalog:
  assert 'blocks'in cat and all(len(cat['final'][k])==7 for k in'dabc'),'catalog needs explicit seven-wire encoders'
  for k in'abc':
   for i in range(7):
    m.Add(T[f'{k}{i}']['pos'][0]==cat['initial'][k][i]);m.Add(T[f'{k}{i}']['pos'][-1]==cat['final'][k][i]);m.Add(P[k][i]==P['a'][i])
  for i in range(7):m.AddElement(P['a'][i],cat['final']['d'],E['d'][i])
  # All 168 code automorphisms retain the catalog's physical encoded states.
  reachable=[]
  for ei,em in enumerate(embs):
   mp=dict(zip(cells,em['cells']))
   for pp in AUT:
    if all(abs(mp[PD[i]]//6-cat['final']['d'][pp[i]]//6)+abs(mp[PD[i]]%6-cat['final']['d'][pp[i]]%6)<=a.data_moves for i in range(7)):reachable.append([ei]+pp)
  if not a.free_prefix:m.AddAllowedAssignments([embed]+P['a'],reachable)
 move_cost=sum((2 if k[0]=='d'else 1)*sum(tok['moves'])for k,tok in T.items());m.Add(move_cost<=a.move_budget)
 if a.exposure_objective:
  idle=[]
  for seg in segments:
   seq=seg['units'];idle.append(2*(pt[seq[-1]]-pt[seq[0]]+1-len(seq)))
  for key,tok in T.items():
   k=key[0];i=int(key[1:]);gates=1 if k=='d'else 1+sum(i in pair for pair in enc[k][0]);count=R-tok['init']-gates-(2 if k=='d'else 1)*sum(tok['moves']);m.Add(count>=0);idle.append((4 if k=='d'else 1 if k=='a'else 2)*count)
  m.Minimize(100*(sum(idle)+4*move_cost)+R)
 # Search priority reflects the early-round target and measured exposure/move prices;
 # all resulting complete circuits are scored by full third order.
 cost=1000000*R+sum(R-v['init']for v in T.values())+sum(R-j['t']for j in J)+sum(R-t for t in pt)+4*sum(z for v in T.values()for z in v['moves'])
 if not a.exposure_objective:m.Minimize(cost)
 return m,dict(R=R,embedding=embed,mapping=mapping,prefix_t=pt,prefix_locs=pl,tokens=T,jobs=J,permutations=P,endpoints=E),pre,dets,embs,enc,decisions

def get(s,a,V,pre,dets,embs,enc):
 x=dict(args=vars(a),R=s.Value(V['R']),embedding=s.Value(V['embedding']),embedding_description=embs[s.Value(V['embedding'])],mapping={q:s.Value(v)for q,v in V['mapping'].items()},prefix_t=[s.Value(v)for v in V['prefix_t']],prefix_locs=[[s.Value(v)for v in vs]for vs in V['prefix_locs']],tokens={key:{k:[s.Value(v)for v in vs]if isinstance(vs,list)else s.Value(vs)for k,vs in tok.items()}for key,tok in V['tokens'].items()},jobs=[{k:[s.Value(v)for v in vs]if k in('loc','stage')else(s.Value(vs)if k=='t'else vs)for k,vs in j.items()}for j in V['jobs']],permutations={k:[s.Value(v)for v in vs]for k,vs in V['permutations'].items()},endpoints={k:[s.Value(v)for v in vs]for k,vs in V['endpoints'].items()},encoders=enc)
 return x

def build(x,name):
 pre,tail=prefix(x['args'].get('prefix_variant','base'));R=x['R'];mp={int(k):v for k,v in x['mapping'].items()};ops=[];bit=100
 def add(t,lines,tag,**kw):ops.append(dict(t=t,lines=lines,tag=tag,**kw))
 for i,(u,t)in enumerate(zip(pre,x['prefix_t'])):
  um=dict(zip(u.qs,x['prefix_locs'][i]))if 'prefix_locs'in x else mp
  add(t,rename(u.lines,um),'prefix',prefix_i=i)
 for key,tok in x['tokens'].items():
  k=key[0];i=int(key[1:]);q=tok['pos'][0]
  if k!='d':add(tok['init'],[f'reset q[{q}];']+([f'h q[{q}];']if i in x['encoders'][k][1]else[]),'prep_init')
  for j,z in enumerate(tok['moves']):
   if not z:continue
   u,v=tok['pos'][j:j+2];t=tok['ts'][j];add(t-1,[f'reset q[{v}];']+([f'h q[{v}];']if k=='a'else[]),'move_init')
   aa,bb=(v,u)if k=='a'else(u,v);add(t,[f'cx q[{aa}],q[{bb}];'],'move_cx')
   if k=='d':
    add(t+1,[f'cx q[{v}],q[{u}];'],'data_cx');add(t+2,[f'measure q[{u}] -> c[{bit}];'],'data_watch');tail.append(f'// DETECTOR c[{bit}]');bit+=1
   else:
    add(t+1,([f'h q[{u}];']if k!='a'else[])+[f'measure q[{u}] -> c[{bit}];']+([f'h q[{u}];']if k!='a'else[]),'tele_m',destination=v,axis=0 if k=='a'else 1,bit=bit);bit+=1
 for j in x['jobs']:
  if j['k']=='d':add(j['t'],[f"tdg q[{j['loc'][0]}];"],'data_tdg')
  else:u,v=j['loc'];add(j['t'],[f'cx q[{u}],q[{v}];'],'encoder_'+j['k'])
 read={}
 for i in range(7):
  d,a,b,c=(x['endpoints'][k][i]for k in'dabc');add(R,[f'cx q[{d}],q[{a}];'],'round');add(R,[f'cx q[{b}],q[{c}];'],'round');add(R+1,[f'cx q[{b}],q[{d}];'],'round')
  for k,q,t,basis in[('a',a,R+1,'Z'),('b',b,R+2,'X'),('c',c,R+1,'Z')]:
   add(t,([f'h q[{q}];']if basis=='X'else[])+[f'measure q[{q}] -> c[{bit}];'],'read',bit=bit);read[k,i]=bit;bit+=1
 ops.sort(key=lambda o:(o['t'],o['tag']!='tele_m'));frames={q:[set(),set()]for q in range(36)};corr={}
 for o in ops:
  u=unit(o);qs=list(map(int,S.QRE.findall(o['lines'][0])))
  if u.name in('RESET','RX'):frames[qs[0]]=[set(),set()]
  elif u.name=='CX':a,b=qs;frames[b][0]^=frames[a][0];frames[a][1]^=frames[b][1]
  elif o['tag']=='tele_m':
   q=qs[0];axis=o['axis'];frames[o['destination']][axis]^=frames[q][axis]^{o['bit']};frames[q]=[set(),set()]
  elif o['tag']=='read':corr[o['bit']]=frames[qs[0]][1 if u.name=='MX'else 0].copy()
  elif u.name=='H':frames[qs[0]].reverse()
  elif u.name in('T','TDG'):assert not any(frames[qs[0]]),('output frame on T',o,frames[qs[0]])
 assert all(not any(frames[q])for q in x['endpoints']['d'])
 for k in'abc':
  for g in ROWS+([list(range(7))]if k=='c'else[]):
   bs={read[k,i]for i in g}
   for i in g:bs^=corr[read[k,i]]
   tail.append('// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(bs)))
 for i,o in enumerate(ops):o['id']=i
 compact={t:i for i,t in enumerate(sorted({o['t']for o in ops}))}
 c=dict(h=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{bit}];'],ops=ops,tail=tail,meta=dict(data_qubits=x['endpoints']['d'],R=compact[R],R_model=R,source='complete prefix-round redesign',free_prefix=x['args'].get('free_prefix',False),embedding=x['embedding_description'],encoder=x['args']['encoder'],catalog=x['args']['catalog'],block_teleports=sum(sum(v['moves'])for k,v in x['tokens'].items()if k[0]!='d'),data_hops=sum(sum(v['moves'])for k,v in x['tokens'].items()if k[0]=='d')))
 return save(c,name)

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--free-prefix',action='store_true');p.add_argument('--hint');p.add_argument('--prep-before-moves',action='store_true');p.add_argument('--exposure-objective',action='store_true');p.add_argument('--move-budget',type=int,default=1000);p.add_argument('--prefix-variant',default='base');p.add_argument('--encoder',default='l3_10');p.add_argument('--moves',type=int,default=2);p.add_argument('--data-moves',type=int,default=4);p.add_argument('--min-round',type=int,default=30);p.add_argument('--max-round',type=int,default=50);p.add_argument('--embedding',type=int,default=-1);p.add_argument('--catalog');p.add_argument('--compact9',action='store_true');p.add_argument('--external-moves',type=int,default=1);p.add_argument('--seconds',type=float,default=300);p.add_argument('--workers',type=int,default=4);p.add_argument('--seed',type=int,default=0);p.add_argument('--incumbents',action='store_true');a=p.parse_args();m,V,pre,dets,embs,enc,decisions=create(a)
 if a.hint:
  old=json.loads(Path(a.hint).read_text());hints={}
  def hint(v,z):hints[v.Index()]=int(z)
  hint(V['R'],old['R']);hint(V['embedding'],0 if a.free_prefix else old['embedding'])
  for q,v in V['mapping'].items():hint(v,old['mapping'][str(q)])
  for v,z in zip(V['prefix_t'],old['prefix_t']):hint(v,z)
  for i,vs in enumerate(V['prefix_locs']):
   for q,v in zip(pre[i].qs,vs):hint(v,old['mapping'][str(q)])
  for k,tok in V['tokens'].items():
   for n,v in tok.items():
    if isinstance(v,list):
     for v1,z in zip(v,old['tokens'][k][n]):hint(v1,z)
    else:hint(v,old['tokens'][k][n])
  for k,vs in V['permutations'].items():
   for v,z in zip(vs,old['permutations'][k]):hint(v,z)
  for k,vs in V['endpoints'].items():
   for v,z in zip(vs,old['endpoints'][k]):hint(v,z)
  for job,oj in zip(V['jobs'],old['jobs']):
   if job['indices']!=oj['indices']or job['k']!=oj['k']:continue
   hint(job['t'],oj['t'])
   for n in('stage','loc'):
    for v,z in zip(job[n],oj[n]):hint(v,z)
  for i,z in hints.items():m.AddHint(m.GetIntVarFromProtoIndex(i),z)
 (H/(a.out+'.model.json')).write_text(json.dumps(dict(args=vars(a),embedding_count=len(embs),prefix_cx=sum(u.name=='CX'for u in pre),prefix_detectors=len(dets),variables=len(m.Proto().variables),constraints=len(m.Proto().constraints)),indent=2))
 s=cp_model.CpSolver();s.parameters.num_workers=a.workers;s.parameters.max_time_in_seconds=a.seconds;s.parameters.cp_model_presolve=False;s.parameters.random_seed=a.seed;s.parameters.stop_after_first_solution=not a.incumbents
 count=0;best=1.;seen=set()
 def price(cb):
  nonlocal count,best
  x=get(cb,a,V,pre,dets,embs,enc);name=a.out+f'_w{count}';count+=1
  (H/(name+'.solver.json')).write_text(json.dumps(x,indent=1));row=dict(name=name,model_R=x['R'],embedding=x['embedding'],search_objective=cb.ObjectiveValue())
  try:
   stem=build(x,name);sha=hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest()
   if sha in seen:row['duplicate']=True
   else:
    seen.add(sha);r=score(stem);row.update(r)
    if r.get('total',1)<best and r.get('exp_minus_A1',0)>=.5002:
     best=r['total'];(H/(a.out+'.best.json')).write_text(json.dumps(row,indent=2))
  except Exception as e:row['error']=repr(e)
  with gzip.open(H/(a.out+'.witnesses.jsonl.gz'),'at')as f:f.write(json.dumps(dict(result=row,plan=x))+'\n')
  append_result(name,row,'Complete new cultivation embedding/schedule plus separate ABC and moving data. No blue check or inherited incumbent suffix.');print(json.dumps(row),flush=True)
 class CB(cp_model.CpSolverSolutionCallback):
  def on_solution_callback(self):price(self)
 start=time.monotonic();st=s.Solve(m,CB());receipt=dict(status=s.StatusName(st),seconds=time.monotonic()-start,stats=s.ResponseStats(),witnesses=count,args=vars(a));(H/(a.out+'.receipt.json')).write_text(json.dumps(receipt,indent=2));append_result(a.out,receipt,'Solver termination; UNKNOWN is not infeasibility.');print(json.dumps(receipt),flush=True)
if __name__=='__main__':main()
