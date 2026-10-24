"""Separate B/C spacetime synthesis with teleports inside the encoders.

Retains v23's data/A/prefix schedule initially. B/C cell roles are free at every
teleport stage; encoder CXs may execute at any stage, not only before movement.
The round has consecutive B→C and B→D. Every SAT witness is emitted and priced.
"""
from common import *
import argparse,collections
GENS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
LAY=[[(0,2),(1,6),(3,5)],[(0,4),(1,2),(3,6)],[(0,6),(1,5),(3,4)]]
EDGES=[(a,b)for a in range(36)for b in range(36)if abs(a//6-b//6)+abs(a%6-b%6)==1]

def exterior(R=45):
 md=json.loads((ROOT/'work/lanes/LADDER/f00_base.json').read_text());ops=copy.deepcopy(md['units']);orig=read(ROOT/'work/lanes/MAIN/v23h_c2c9');tail=orig['tail'];removed=set();keep=[]
 for o in ops:
  u=unit(o);qs=list(map(int,S.QRE.findall(o['lines'][0])));bits=set(map(int,re.findall(r'c\[(\d+)\]',' '.join(o['lines']))))
  if o['tag']=='BC':removed|=bits;continue
  if o['tag']=='round':
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
 pth=ROOT/('work/lanes/SEP2T/inputs/prep_l3_10.json'if name=='l3_10'else'work/lanes/DR/prepA_L5_s7307.json');p=json.loads(pth.read_text());cells=p.get('cells',A)
 return [(cells.index(v),cells.index(u))for L in p['ops']for u,v in L],[i for i in range(7)if cells[i]not in p['pivots']]

def autos():
 return [[((a if i&1 else 0)^(b if i&2 else 0)^(c if i&4 else 0))-1 for i in range(1,8)]for a in range(1,8)for b in range(1,8)for c in range(1,8)if len({a,b,c,a^b,a^c,b^c,a^b^c})==7]

def model(a):
 R=a.round;K=a.moves;ops,tail=exterior(R);busy=intervals(ops,R);enc,piv=template(a.encoder);m=cp_model.CpModel();xx=[];yy=[];tokens={};jobs=[];decisions=[]
 def v(lo,hi,n):return m.NewIntVar(lo,hi,n)
 def occupy(p,s,e,n):
  sv=v(0,R+3,n+'start');ev=v(0,R+3,n+'end');m.Add(sv==s);m.Add(ev==e);z=v(0,R+3,n+'len');m.Add(z==ev-sv);xx.append(m.NewFixedSizeIntervalVar(p,1,n+'cell'));yy.append(m.NewIntervalVar(sv,z,ev,n+'life'))
 for q,s,e in busy:occupy(m.NewConstant(q),s,e,f'fixed{q}_{s}')
 for k in 'bc':
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
 for k in 'bc':
  last={i:tokens[f'{k}{i}']['init']for i in range(7)}
  for gi,(u,w)in enumerate(enc):
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
 for k in 'bc':
  perm[k]=[v(0,6,f'{k}perm{i}')for i in range(7)]
  if a.automorphisms:m.AddAllowedAssignments(perm[k],autos())
  else:
   for i in range(7):m.Add(perm[k][i]==i)
  ends[k]=[v(0,35,f'{k}end{i}')for i in range(7)]
  for i in range(7):m.AddElement(perm[k][i],[tokens[f'{k}{j}']['pos'][-1]for j in range(7)],ends[k][i])
 for i in range(7):
  m.AddAllowedAssignments([ends['b'][i]],[(q,)for q in range(36)if(D[i],q)in EDGES]);m.AddAllowedAssignments([ends['b'][i],ends['c'][i]],EDGES)
 if a.fixed_endpoints:
  for k,qs in[('b',B),('c',C)]:
   for i,q in enumerate(qs):m.Add(ends[k][i]==q)
 m.AddAllDifferent(ends['b']+ends['c']);m.AddNoOverlap2D(xx,yy)
 # Only a search priority, never a ranking: first feasible witness is priced in full.
 cost=sum(4*z for tok in tokens.values()for z in tok['moves'])+sum(R-tok['init']for tok in tokens.values())+sum(R-j['t']for j in jobs)
 m.Minimize(cost)
 return m,tokens,jobs,perm,ends,ops,tail,piv,decisions,busy

def result(s,a,T,J,perm,ends,piv):
 return dict(args=vars(a),tokens={k:{n:[s.Value(v)for v in vs]if isinstance(vs,list)else s.Value(vs)for n,vs in x.items()}for k,x in T.items()},jobs=[{n:[s.Value(v)for v in vs]if isinstance(vs,list)else(s.Value(vs)if n=='t'else vs)for n,vs in j.items()}for j in J],permutations={k:[s.Value(v)for v in vs]for k,vs in perm.items()},endpoints={k:[s.Value(v)for v in vs]for k,vs in ends.items()},pivots=piv)

def emit(x,name):
 R=x['args']['round'];old,tail=exterior(R);ops=copy.deepcopy(old);n=100;T=x['tokens'];frames={q:set()for q in range(36)};events=[];readouts={}
 for key,tok in T.items():
  q=tok['pos'][0];ops.append(dict(lines=[f'reset q[{q}];']+([f'h q[{q}];']if int(key[1:])in x['pivots']else[]),t=tok['init'],tag='bc_init'))
  for j,z in enumerate(tok['moves']):
   if not z:continue
   u,v=tok['pos'][j:j+2];t=tok['ts'][j]
   ops.append(dict(lines=[f'reset q[{v}];'],t=t-1,tag='tele_init'))
   ops.append(dict(lines=[f'cx q[{u}],q[{v}];'],t=t,tag='tele_cx'))
   ops.append(dict(lines=[f'h q[{u}];',f'measure q[{u}] -> c[{n}];',f'h q[{u}];'],t=t+1,tag='tele_m',tele_destination=v,bit=n));n+=1
 for job in x['jobs']:
  u,v=job['loc'];ops.append(dict(lines=[f'cx q[{u}],q[{v}];'],t=job['t'],tag='bc_encoder'))
 for i in range(7):
  b=x['endpoints']['b'][i];c=x['endpoints']['c'][i]
  ops.append(dict(lines=[f'cx q[{b}],q[{c}];'],t=R,tag='bc_check'))
  ops.append(dict(lines=[f'cx q[{b}],q[{D[i]}];'],t=R+1,tag='bc_data'))
  for k,q,t,basis in[('b',b,R+2,'X'),('c',c,R+1,'Z')]:
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
  if u.name in('RESET','RX'):frames[qs[0]]=set()
  elif u.name=='CX':a,b=qs;frames[a]^=frames[b]
  elif o['tag']=='tele_m':
   q=qs[0];frames[o['tele_destination']]^=frames[q]^{o['bit']};frames[q]=set()
  elif o['tag']=='bc_read':corr[o['bit']]=frames[qs[0]].copy()if u.name=='MX'else set()
  elif u.name in('T','TDG'):assert not frames[qs[0]],('frame on prefix T',o,frames[qs[0]])
 for k in 'bc':
  for g in GENS+([list(range(7))]if k=='c'else[]):
   bs={readouts[k,i]for i in g}
   for i in g:bs^=corr[readouts[k,i]]
   tail.append('// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(bs)))
 # Same-time source measurement and destination CX commute physically, but frame
 # updates must happen before the destination operation; sorting above enforces it.
 assert all(not frames[q]for q in D)
 for i,o in enumerate(ops):o['id']=i
 actualR={t:i for i,t in enumerate(sorted({o['t']for o in ops}))}[R]
 c=dict(h=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{n}];'],ops=ops,tail=tail,meta=dict(data_qubits=D,R=actualR,R_model=R,source='separate BC with interleaved teleports',plan=x,block_teleports=sum(sum(tok['moves'])for tok in T.values()),encoder_cx=2*len(template(x['args']['encoder'])[0])))
 c['ordered']=True
 c,repair=schedule(c,mode='near')
 assert c is not None,repair
 c['meta']['virgin_restore_schedule']=repair
 return save(c,name)

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--round',type=int,default=45);p.add_argument('--moves',type=int,default=3);p.add_argument('--encoder',choices=['std9','l5_11','l3_10'],default='std9');p.add_argument('--seconds',type=float,default=180);p.add_argument('--workers',type=int,default=2);p.add_argument('--seed',type=int,default=0);p.add_argument('--automorphisms',action='store_true');p.add_argument('--fixed-endpoints',action='store_true');p.add_argument('--solutions',type=int,default=4);a=p.parse_args();m,T,J,P,E,ops,tail,piv,dv,busy=model(a)
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
