"""Separate B/C spacetime synthesis with teleports inside the encoders.

Retains v23's data/A/prefix schedule initially. B/C cell roles are free at every
teleport stage; encoder CXs may execute at any stage, not only before movement.
The round has consecutive B→C and B→D. Every SAT witness is emitted and priced.
"""
from common import *
import argparse,collections
GENS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
LAY=[[(0,2),(1,6),(3,5)],[(0,4),(1,2),(3,6)],[(0,6),(1,5),(3,4)]]
BASE_D=D[:];DATA_HOPS=[]
EDGES=[(a,b)for a in range(36)for b in range(36)if abs(a//6-b//6)+abs(a%6-b%6)==1]

def exterior(R=45,free_a=False):
 md=json.loads((H/'inputs/ladder_f00.json').read_text());ops=copy.deepcopy(md['units']);orig=read(H/'inputs/v23h_c2c9');tail=orig['tail'];removed=set();keep=[]
 for o in ops:
  u=unit(o);qs=list(map(int,S.QRE.findall(o['lines'][0])));bits=set(map(int,re.findall(r'c\[(\d+)\]',' '.join(o['lines']))))
  if o['tag']=='BC' or (free_a and o['tag']=='A'):removed|=bits;continue
  if o['tag']=='round':
   if free_a:removed|=bits;continue
   if u.name=='CX' and tuple(qs)in[(19,25),(17,16)]:continue
   if u.name=='CX' and tuple(qs)not in list(zip(D,A)):continue
   if u.name in('MEASURE','MX')and qs[0]not in A:removed|=bits;continue
   # Direct A measurement removes the C-controlled parity gadgets.
   if u.name=='MEASURE':o['t']=46
  if o['t']>=45:o['t']+=R-45
  keep.append(o)
 det=[]
 for l in tail:
  if not l.startswith('// DETECTOR'):continue
  bs=set(map(int,re.findall(r'c\[(\d+)\]',l)))
  if 19 in bs:bs.symmetric_difference_update({24})
  if 22 in bs:bs.symmetric_difference_update({23})
  bs-=removed
  if bs:det.append('// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(bs)))
 for hop_i,(logical,dst) in enumerate(DATA_HOPS):
  src=BASE_D[logical]
  source_ops=[o for o in keep if src in unit(o).qs]
  last=max(o['t'] for o in source_ops if unit(o).name!='TDG')
  dest_ops=[o for o in keep if dst in unit(o).qs]
  ready=max([o['t']+2 for o in dest_ops]+[0])
  t=max(last+1,ready)
  for o in source_ops:
   if o['t']>=t:
    assert unit(o).name=='TDG',o
    o['lines']=rename(o['lines'],{src:dst})
  keep.extend([dict(lines=[f'reset q[{dst}];'],t=t-1,tag='extra_data_init'),dict(lines=[f'cx q[{src}],q[{dst}];'],t=t,tag='extra_data_hop'),dict(lines=[f'cx q[{dst}],q[{src}];'],t=t+1,tag='extra_data_hop'),dict(lines=[f'measure q[{src}] -> c[{90+hop_i}];'],t=t+2,tag='extra_data_watch')])
  det.append(f'// DETECTOR c[{90+hop_i}]')
 return keep,det

def intervals(ops,R):
 out=[]
 for q in range(36):
  seq=sorted([(o['t'],unit(o))for o in ops if q in unit(o).qs],key=lambda z:z[0])
  if not seq:continue
  start=seq[0][0]
  for j,(t,u)in enumerate(seq):
   end=j+1==len(seq)
   resetnext=not end and seq[j+1][1].name in('RESET','RX')
   if end or resetnext:
    stop=t+1 if resetnext or u.name in('MEASURE','MX') or q not in D else R+3
    out.append((q,start,stop))
    if not end:start=seq[j+1][0]
 return out

def template(name):
 if name=='std9':return [e for L in LAY for e in L],[0,1,3]
 pth=H/'inputs'/('prep_l3_10.json'if name=='l3_10'else'prepA_L5_s7307.json');p=json.loads(pth.read_text());cells=p.get('cells',A)
 return [(cells.index(v),cells.index(u))for L in p['ops']for u,v in L],[i for i in range(7)if cells[i]not in p['pivots']]

def autos():
 return [[((a if i&1 else 0)^(b if i&2 else 0)^(c if i&4 else 0))-1 for i in range(1,8)]for a in range(1,8)for b in range(1,8)for c in range(1,8)if len({a,b,c,a^b,a^c,b^c,a^b^c})==7]

def model(a):
 R=a.round;K=a.moves;kinds='abc'if a.free_a else 'bc';ops,tail=exterior(R,a.free_a);busy=intervals(ops,R);enc,piv=template(a.encoder);piv={k:([i for i in range(7)if i not in piv]if k=='a'else piv[:])for k in kinds};m=cp_model.CpModel();xx=[];yy=[];tokens={};jobs=[];decisions=[]
 def v(lo,hi,n):return m.NewIntVar(lo,hi,n)
 def occupy(p,s,e,n):
  sv=v(0,R+3,n+'start');ev=v(0,R+3,n+'end');m.Add(sv==s);m.Add(ev==e);z=v(0,R+3,n+'len');m.Add(z==ev-sv);xx.append(m.NewFixedSizeIntervalVar(p,1,n+'cell'));yy.append(m.NewIntervalVar(sv,z,ev,n+'life'))
 for q,s,e in busy:occupy(m.NewConstant(q),s,e,f'fixed{q}_{s}')
 for k in kinds:
  for i in range(7):
   key=f'{k}{i}';ps=[v(0,35,key+f'p{j}')for j in range(K+1)];init=v(0,R-1,key+'init');mv=[];ts=[]
   for j in range(K):
    z=m.NewBoolVar(key+f'm{j}');t=v(1,R-1,key+f't{j}');m.AddAllowedAssignments([ps[j],ps[j+1],z],[(u,w,1)for u,w in EDGES]+[(q,q,0)for q in range(36)])
    m.Add(t>=init+1)
    if j:m.Add(t>=ts[-1]+mv[-1]);m.Add(z<=mv[-1])
    mv.append(z);ts.append(t)
   for j in range(K+1):
    start=init if j==0 else ts[j-1]-mv[j-1]
    end=R+(3 if k=='b'else 2)if j==K else ts[j]+2*mv[j]
    occupy(ps[j],start,end,key+f's{j}')
   tokens[key]=dict(pos=ps,init=init,moves=mv,ts=ts);decisions+=ps+mv
 # A gate's stage selects the cell and constrains it to the live portion of that stage.
 for k in kinds:
  last={i:tokens[f'{k}{i}']['init']for i in range(7)}
  for gi,(u,w)in enumerate([(v,u)for u,v in enc]if k=='a'else enc):
   t=v(1,R-1,f'{k}g{gi}t');locs=[];stages=[]
   for i in(u,w):
    tok=tokens[f'{k}{i}'];stage=v(0,K,f'{k}g{gi}s{i}');loc=v(0,35,f'{k}g{gi}p{i}');m.AddElement(stage,tok['pos'],loc);locs.append(loc);stages.append(stage)
    m.Add(t>last[i]);last[i]=t
    for j in range(K+1):
     z=m.NewBoolVar(f'{k}g{gi}i{i}is{j}');m.Add(stage==j).OnlyEnforceIf(z);m.Add(stage!=j).OnlyEnforceIf(z.Not())
     if j:
      m.Add(tok['moves'][j-1]==1).OnlyEnforceIf(z);m.Add(t>=tok['ts'][j-1]+1).OnlyEnforceIf(z)
     if j<K:m.Add(t<tok['ts'][j]).OnlyEnforceIf([z,tok['moves'][j]])
   m.AddAllowedAssignments(locs,EDGES);jobs.append(dict(k=k,u=u,v=w,t=t,stage=stages,loc=locs));decisions+=stages
 perm={};ends={}
 for k in kinds:
  perm[k]=[v(0,6,f'{k}perm{i}')for i in range(7)]
  if a.automorphisms:m.AddAllowedAssignments(perm[k],autos())
  else:
   for i in range(7):m.Add(perm[k][i]==i)
  ends[k]=[v(0,35,f'{k}end{i}')for i in range(7)]
  for i in range(7):m.AddElement(perm[k][i],[tokens[f'{k}{j}']['pos'][-1]for j in range(7)],ends[k][i])
 for i in range(7):
  if a.free_a:m.AddAllowedAssignments([ends['a'][i]],[(q,)for q in range(36)if(D[i],q)in EDGES])
  m.AddAllowedAssignments([ends['b'][i]],[(q,)for q in range(36)if(D[i],q)in EDGES]);m.AddAllowedAssignments([ends['b'][i],ends['c'][i]],EDGES)
 if a.fixed_endpoints:
  for k,qs in([('a',A)]if a.free_a else[])+[('b',B),('c',C)]:
   for i,q in enumerate(qs):m.Add(ends[k][i]==q)
 m.AddAllDifferent(sum(ends.values(),[]));m.AddNoOverlap2D(xx,yy)
 # Only a search priority, never a ranking: first feasible witness is priced in full.
 cost=sum(4*z for tok in tokens.values()for z in tok['moves'])+sum(R-tok['init']for tok in tokens.values())+sum(R-j['t']for j in jobs)
 m.Minimize(cost)
 return m,tokens,jobs,perm,ends,ops,tail,piv,decisions,busy

def result(s,a,T,J,perm,ends,piv):
 return dict(args=vars(a),tokens={k:{n:[s.Value(v)for v in vs]if isinstance(vs,list)else s.Value(vs)for n,vs in x.items()}for k,x in T.items()},jobs=[{n:[s.Value(v)for v in vs]if isinstance(vs,list)else(s.Value(vs)if n=='t'else vs)for n,vs in j.items()}for j in J],permutations={k:[s.Value(v)for v in vs]for k,vs in perm.items()},endpoints={k:[s.Value(v)for v in vs]for k,vs in ends.items()},pivots=piv)

def emit(x,name):
 global D,DATA_HOPS
 DATA_HOPS=[tuple(map(int,v.split(':')))for v in x['args'].get('data_hop',[])];D=BASE_D[:]
 for i,q in DATA_HOPS:D[i]=q
 R=x['args']['round'];free_a=x['args'].get('free_a',False);kinds='abc'if free_a else'bc';old,tail=exterior(R,free_a);ops=copy.deepcopy(old);n=100;T=x['tokens'];frames={q:[set(),set()]for q in range(36)};events=[];readouts={}
 for key,tok in T.items():
  q=tok['pos'][0];ops.append(dict(lines=[f'reset q[{q}];']+([f'h q[{q}];']if int(key[1:])in (x['pivots'][key[0]]if isinstance(x['pivots'],dict)else x['pivots'])else[]),t=tok['init'],tag='bc_init'))
  for j,z in enumerate(tok['moves']):
   if not z:continue
   u,v=tok['pos'][j:j+2];t=tok['ts'][j]
   ops.append(dict(lines=[f'reset q[{v}];']+([f'h q[{v}];']if key[0]=='a'else[]),t=t-1,tag='tele_init'))
   aa,bb=(v,u)if key[0]=='a'else(u,v)
   ops.append(dict(lines=[f'cx q[{aa}],q[{bb}];'],t=t,tag='tele_cx'))
   ops.append(dict(lines=([f'h q[{u}];']if key[0]!='a'else[])+[f'measure q[{u}] -> c[{n}];']+([f'h q[{u}];']if key[0]!='a'else[]),t=t+1,tag='tele_m',tele_destination=v,tele_axis=0 if key[0]=='a'else 1,bit=n));n+=1
 for job in x['jobs']:
  u,v=job['loc'];ops.append(dict(lines=[f'cx q[{u}],q[{v}];'],t=job['t'],tag='bc_encoder'))
 for i in range(7):
  b=x['endpoints']['b'][i];c=x['endpoints']['c'][i]
  if free_a:ops.append(dict(lines=[f"cx q[{D[i]}],q[{x['endpoints']['a'][i]}];"],t=R,tag='a_data'))
  ops.append(dict(lines=[f'cx q[{b}],q[{c}];'],t=R,tag='bc_check'))
  ops.append(dict(lines=[f'cx q[{b}],q[{D[i]}];'],t=R+1,tag='bc_data'))
  for k,q,t,basis in([('a',x['endpoints']['a'][i],R+1,'Z')]if free_a else[])+[('b',b,R+2,'X'),('c',c,R+1,'Z')]:
   ops.append(dict(lines=([f'h q[{q}];']if basis=='X'else[])+[f'measure q[{q}] -> c[{n}];'],t=t,tag='bc_read',bit=n,read_key=(k,i)));readouts[k,i]=n;n+=1
 # A borrowed cell must be restored before a former implicit first-use |0>.
 for q in range(36):
  previous=[o for o in old if q in unit(o).qs]
  if not previous:continue
  first=min(previous,key=lambda o:o['t'])
  if unit(first).name in ('RESET','RX'):continue
  if any(q in unit(o).qs and o['t']<first['t'] and o not in old for o in ops):
   ops.append(dict(lines=[f'reset q[{q}];'],t=first['t'],tag='restore_virgin'))
 ops.sort(key=lambda o:(o['t'],0 if o['tag']=='tele_m'else 1 if o['tag']=='restore_virgin'else 2))
 corr={}
 for o in ops:
  u=unit(o);qs=list(map(int,S.QRE.findall(o['lines'][0])))
  if u.name in('RESET','RX'):frames[qs[0]]=[set(),set()]
  elif u.name=='CX':a,b=qs;frames[b][0]^=frames[a][0];frames[a][1]^=frames[b][1]
  elif o['tag']=='tele_m':
   q=qs[0];axis=o.get('tele_axis',1);frames[o['tele_destination']][axis]^=frames[q][axis]^{o['bit']};frames[q]=[set(),set()]
  elif o['tag']=='bc_read':corr[o['bit']]=frames[qs[0]][1 if u.name=='MX'else 0].copy()
  elif u.name in('T','TDG'):assert not any(frames[qs[0]]),('frame on prefix T',o,frames[qs[0]])
 for k in kinds:
  for g in GENS+([list(range(7))]if k=='c'else[]):
   bs={readouts[k,i]for i in g}
   for i in g:bs^=corr[readouts[k,i]]
   tail.append('// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(bs)))
 # Same-time source measurement and destination CX commute physically, but frame
 # updates must happen before the destination operation; sorting above enforces it.
 assert all(not any(frames[q])for q in D)
 for i,o in enumerate(ops):o['id']=i
 actualR={t:i for i,t in enumerate(sorted({o['t']for o in ops}))}[R]
 c=dict(h=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{n}];'],ops=ops,tail=tail,meta=dict(data_qubits=D,R=actualR,R_model=R,source='separate BC with interleaved teleports',plan=x,block_teleports=sum(sum(tok['moves'])for tok in T.values()),encoder_cx=2*len(template(x['args']['encoder'])[0])))
 c['ordered']=True
 c,repair=schedule(c,mode='near')
 assert c is not None,repair
 c['meta']['virgin_restore_schedule']=repair
 return save(c,name)

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--free-a',action='store_true');p.add_argument('--data-hop',action='append',default=[]);p.add_argument('--round',type=int,default=45);p.add_argument('--moves',type=int,default=3);p.add_argument('--encoder',choices=['std9','l5_11','l3_10'],default='std9');p.add_argument('--seconds',type=float,default=180);p.add_argument('--workers',type=int,default=2);p.add_argument('--seed',type=int,default=0);p.add_argument('--automorphisms',action='store_true');p.add_argument('--fixed-endpoints',action='store_true');p.add_argument('--solutions',type=int,default=4);a=p.parse_args();
 global D,DATA_HOPS
 DATA_HOPS=[tuple(map(int,v.split(':')))for v in a.data_hop];D=BASE_D[:]
 for i,q in DATA_HOPS:
  assert a.free_a and q not in BASE_D and (BASE_D[i],q)in EDGES
  D[i]=q
 m,T,J,P,E,ops,tail,piv,dv,busy=model(a)
 (H/(a.out+'.model.json')).write_text(json.dumps(dict(args=vars(a),fixed_occupancy=busy,encoder=template(a.encoder),variables=len(m.Proto().variables),constraints=len(m.Proto().constraints)),indent=2))
 for iteration in range(a.solutions):
  s=cp_model.CpSolver();s.parameters.num_workers=a.workers;s.parameters.max_time_in_seconds=a.seconds;s.parameters.stop_after_first_solution=True;s.parameters.cp_model_presolve=False;s.parameters.random_seed=a.seed+iteration
  start=time.monotonic();status=s.Solve(m);rec=dict(status=s.StatusName(status),seconds=time.monotonic()-start,stats=s.ResponseStats(),iteration=iteration)
  if status in(cp_model.FEASIBLE,cp_model.OPTIMAL):
   x=result(s,a,T,J,P,E,piv);name=a.out+f'_w{iteration}';(H/(name+'.solver.json')).write_text(json.dumps(x,indent=1))
   try:stem=emit(x,name);rec['score']=score(stem);print('priced',name,rec,flush=True)
   except Exception as e:rec['error']=repr(e);print('build error',name,repr(e),flush=True)
   append_result(name,rec,'Separate B/C spacetime witness: gate-stage selection allows teleportation during encoding; retained A/data/prefix, late transversal B verification.')
   m.AddForbiddenAssignments(dv,[[s.Value(v)for v in dv]])
  else:
   append_result(a.out,rec,'Bounded separate B/C stage/cell model; UNKNOWN is timeout, not impossibility.');print(rec,flush=True)
  (H/(a.out+f'.receipt{iteration}.json')).write_text(json.dumps(rec,indent=2))
  if status not in(cp_model.FEASIBLE,cp_model.OPTIMAL):break
if __name__=='__main__':main()
