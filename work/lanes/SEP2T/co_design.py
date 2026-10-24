"""Joint placement, lifetime occupancy, native-operation timing and routing.

Separate seven-wire encoder templates; every initial and final block cell is free.
Prefix per-wire dependencies are preserved, but its end and internal schedule are
free. A source cell remains occupied through the teleport measurement/second CX;
the destination is reserved starting with its reset. B verification and coupling
are consecutive. Optional skipped moves have zero duration, not phantom occupancy.
All output is local to this lane. CP-SAT UNKNOWN is always a timeout.
"""
import os, sys, json, re, time, argparse
from pathlib import Path
sys.dont_write_bytecode = True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
ROOT=Path('/home/jihoon/competitions/quantumn'); HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE/'inputs'),str(ROOT/'work/lanes/SCHED'),str(ROOT/'work/lanes/EVAL')]
import schedule as S
from util import native_times
from ortools.sat.python import cp_model
QRE=re.compile(r'q\[(\d+)\]')
GENS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
D0=[0,20,7,4,3,15,8]; P0={0,1,2,3,4,6,7,8,9,10,13,14,15,19,20}
AC=[1,14,8,9,2,16,15]
BCELLS=[6,26,13,11,4,23,27];CCELLS=[12,25,19,17,5,29,28]
EDGES=[(u,v) for u in range(36) for v in range(36) if abs(u//6-v//6)+abs(u%6-v%6)==1]

def automorphisms():
 out=[]
 for a in range(1,8):
  for b in range(1,8):
   for c in range(1,8):
    p=[((a if i&1 else 0)^(b if i&2 else 0)^(c if i&4 else 0))-1 for i in range(1,8)]
    if sorted(p)==list(range(7)):out.append(p)
 assert len(out)==168
 return out

def transform(k,tr,tc):
 def f(q):
  r,c=divmod(q,6);return [(r,c),(r,5-c),(5-r,c),(5-r,5-c),(c,r),(c,5-r),(5-c,r),(5-c,5-r)][k]
 rr=[f(q) for q in P0];mr=min(r for r,c in rr);mc=min(c for r,c in rr)
 return {q:(f(q)[0]-mr+tr)*6+f(q)[1]-mc+tc for q in P0}

def prefix():
 text=(HERE/'inputs/encoder19.qasm').read_text()
 h,r,d=S.qasm_ops(text);us=S.fold_units(r);ts=native_times(text,us)
 pre=[u for u,t in zip(us,ts) if t<=29]
 bits={int(b) for u in pre for line in u.lines for b in re.findall(r'c\[(\d+)\]',line)}
 det=[x for x in d if x.startswith('// DETECTOR') and set(map(int,re.findall(r'c\[(\d+)\]',x)))<=bits]
 return pre,det

def template(option,kind):
 if option=='l3_10':
  p=json.loads((HERE/'inputs/prep_l3_10.json').read_text());cells=p['cells']
  ops=[[(cells.index(u),cells.index(v)) for u,v in L] for L in p['ops']];piv=[cells.index(q) for q in p['pivots']]
  if kind!='a':ops=[[(v,u) for u,v in L] for L in ops];piv=[i for i in range(7) if i not in piv]
  return dict(ops=ops,pivots=piv)
 p=json.loads((HERE/'inputs'/('prepA_L5_s7307.json' if option=='l5_11' else 'prepA_L5_exact.json')).read_text())
 ops=[[(AC.index(u),AC.index(v)) for u,v in L] for L in p['ops']]
 piv=[AC.index(q) for q in p['pivots']]
 if kind!='a':ops=[[(v,u) for u,v in L] for L in ops];piv=[i for i in range(7) if i not in piv]
 return dict(ops=ops,pivots=piv)

def joint_template():
 text=(HERE/'inputs/encoder19.qasm').read_text();h,r,d=S.qasm_ops(text);us=S.fold_units(r);ts=native_times(text,us)
 names={q:f'{k}{i}' for k,cells in [('b',BCELLS),('c',CCELLS)] for i,q in enumerate(cells)}
 piv={names[u.qs[0]] for u,t in zip(us,ts) if 29<t<47 and u.name=='RX' and u.qs[0] in names}
 ops=[]
 for u,t in zip(us,ts):
  if 29<t<47 and u.name=='CX' and set(u.qs)<=names.keys():
   v,w=map(int,QRE.findall(u.lines[0]));ops.append((names[v],names[w]))
 assert len(ops)==82
 return ops,piv

def solve(a):
 started=time.monotonic();m=cp_model.CpModel();H=a.horizon;xx=[];yy=[]
 def V(lo=0,hi=H+3,n=''):return m.NewIntVar(lo,hi,n)
 def addocc(pos,start,end,name):
  size=V(n=name+'_size');m.Add(size==end-start)
  xx.append(m.NewFixedSizeIntervalVar(pos,1,name+'_cell'))
  yy.append(m.NewIntervalVar(start,size,end,name+'_life'))
 R=V(29,H,'R');RA=V(29,H,'RA');m.Add(RA<=R)
 if not a.early_a:m.Add(RA==R)
 mp=transform(a.sym,a.row,a.col)
 pre,dets=prefix();pts=[V(0,H-1,f'pre{i}') for i in range(len(pre))];per={}
 for i,u in enumerate(pre):
  for q in u.qs:per.setdefault(q,[]).append(i)
 for q,seq in per.items():
  for x,y in zip(seq,seq[1:]):m.Add(pts[y]>pts[x])
  m.Add(pts[seq[-1]]<R)
  if q not in D0:
   e=V(n=f'pend{q}');m.Add(e==pts[seq[-1]]+1)
   addocc(m.NewConstant(mp[q]),pts[seq[0]],e,f'prefix{q}')
 PE=V(n='prefix_end');m.AddMaxEquality(PE,pts)
 T={};jobs=[];idle=[];movecost=[]
 enc={k:template(a.option if k=='a' else a.bc_option,k) for k in 'abc'}
 if a.encoders:
  supplied=json.loads(Path(a.encoders).read_text())
  for k,p in supplied.items():
   cells=p['cells'];enc[k]=dict(ops=[[(cells.index(u),cells.index(v)) for u,v in L] for L in p['ops']],pivots=[cells.index(q) for q in p['pivots']])
 ej=[]
 for k in ('a' if a.joint else 'abc'):
  ej += [(f'{k}{u}',f'{k}{v}') for L in enc[k]['ops'] for u,v in L]
 if a.joint:
  ops,piv=joint_template();ej+=ops
  for k in 'bc':enc[k]=dict(ops=[],pivots=[i for i in range(7) if f'{k}{i}' in piv])
 if a.abstract:ej=[]
 for k in 'dabc':
  for i in range(7):
   key=f'{k}{i}';n=a.dhops if k=='d' else a.bhops
   pos=[V(0,35,key+f'p{j}') for j in range(n+1)]
   if a.fixed_endpoints:
    endmap={'d':[0,20,7,10,3,22,21],'a':AC,'b':[6,26,13,11,4,23,27],'c':[12,25,19,17,5,29,28]}
    m.Add(pos[-1]==endmap[k][i])
   init=V(0,H-1,key+'init')
   if k=='d':m.Add(pos[0]==mp[D0[i]]);m.Add(init==pts[per[D0[i]][0]])
   moves=[];ts=[];ends=[];reset=[]
   for j in range(n):
    mv=m.NewBoolVar(key+f'm{j}');t=V(0,H,key+f't{j}');e=V(n=key+f'e{j}');r=V(n=key+f'r{j}')
    m.AddAllowedAssignments([pos[j],pos[j+1],mv],[(u,v,1) for u,v in EDGES]+[(q,q,0) for q in range(36)])
    m.Add(e==t+2*mv);m.Add(r==t-mv)
    if j:
     m.Add(t >= (ts[-1]+moves[-1] if a.pipeline and k!='d' else ends[-1]));m.Add(mv<=moves[-1])
    m.Add(t>=init+1)
    moves.append(mv);ts.append(t);ends.append(e);reset.append(r)
   deadline=RA if k in 'da' else R
   finish=(RA+2) if k=='a' else R+(3 if k in 'db' else 2)
   arrivals=[init]+reset;departures=ends+[finish]
   for j in range(n+1):addocc(pos[j],arrivals[j],departures[j],key+f's{j}')
   if n:m.Add(ends[-1]<=deadline+(moves[-1] if a.pipeline and k!='d' else 0))
   if k=='d':
    m.Add((ts[0] if n else RA)>=pts[per[D0[i]][-1]]+1)
    idle.append(5*(R-pts[per[D0[i]][-1]]-1))
   T[key]=dict(pos=pos,init=init,moves=moves,ts=ts,ends=ends)
   movecost.extend((3 if k=='d' else 1)*z for z in moves)
 for k in ['a','bc'] if a.joint else ['a','b','c']:
  m.AddAllDifferent([T[f'{kk}{i}']['pos'][0] for kk in k for i in range(7)])
 last={k:v['init'] for k,v in T.items() if k[0]!='d'}
 if a.abstract:
  for k in 'abc':
   start=T[f'{k}0']['init'];mem={}
   for i in range(7):m.Add(T[f'{k}{i}']['init']==start);last[f'{k}{i}']=start+a.abstract_depth
   for q in range(36):
    z=[]
    for i in range(7):
     b=m.NewBoolVar(f'{k}{i}_on{q}');m.Add(T[f'{k}{i}']['pos'][0]==q).OnlyEnforceIf(b);m.Add(T[f'{k}{i}']['pos'][0]!=q).OnlyEnforceIf(b.Not());z.append(b)
    mem[q]=sum(z)
    if q==0:root={}
    root[q]=z[0]
   flow={(u,v):V(0,6,f'{k}flow{u}_{v}') for u,v in EDGES}
   for (u,v),f in flow.items():m.Add(f<=6*mem[u]);m.Add(f<=6*mem[v])
   for q in range(36):m.Add(sum(f for (u,v),f in flow.items() if u==q)-sum(f for (u,v),f in flow.items() if v==q)==7*root[q]-mem[q])
 for li,(u,v) in enumerate(ej):
  t=V(0,H-1,f'cx{li}_{u}_{v}')
  pu,pv=T[u]['pos'][0],T[v]['pos'][0]
  m.AddAllowedAssignments([pu,pv],EDGES)
  m.Add(t>last[u]);m.Add(t>last[v]);last[u]=last[v]=t
  jobs.append((u,v,t))
 for k in 'abc':
  for i in range(7):
   v=T[f'{k}{i}'];m.Add((v['ts'][0] if v['ts'] else (RA if k=='a' else R))>last[f'{k}{i}'])
   # Lifespan minus number of native prep operations, a block exposure proxy.
   idle.append((1 if k=='c' else 2)*(R-v['init']))
 perms={};at={}
 for k in 'abc':
  perms[k]=[V(0,6,f'{k}perm{i}') for i in range(7)]
  if a.automorphisms:m.AddAllowedAssignments(perms[k],automorphisms())
  else:
   for i in range(7):m.Add(perms[k][i]==i)
  at[k]=[V(0,35,f'{k}partner{i}') for i in range(7)]
  for i in range(7):m.AddElement(perms[k][i],[T[f'{k}{j}']['pos'][-1] for j in range(7)],at[k][i])
 if a.joint:
  for i in range(7):m.Add(perms['b'][i]==perms['c'][i])
 for i in range(7):
  m.AddAllowedAssignments([T[f'd{i}']['pos'][-1],at['a'][i]],EDGES)
  m.AddAllowedAssignments([T[f'd{i}']['pos'][-1],at['b'][i]],EDGES)
  m.AddAllowedAssignments([at['b'][i],at['c'][i]],EDGES)
 m.AddNoOverlap2D(xx,yy)
 # Every token must be in a distinct final cell; redundant but useful propagation.
 m.AddAllDifferent([v['pos'][-1] for k,v in T.items() if not (a.reuse_a and k[0]=='a')])
 if a.hint:
  hh=json.loads(Path(a.hint).read_text())
  for k in 'dabc':
   for i in range(7):
    for key,at in [('initial',0),('final',-1)]:m.AddHint(T[f'{k}{i}']['pos'][at],hh[key][k][i])
 if a.solution_hint:
  hh=json.loads(Path(a.solution_hint).read_text());m.AddHint(R,hh['R']);m.AddHint(RA,hh.get('RA',hh['R']))
  for v,t in zip(pts,hh['prefix_times']):m.AddHint(v,t)
  for key,vs in T.items():
   hv=hh['tokens'][key]
   for name in ('pos','ts','moves'):
    for v,value in zip(vs[name],hv[name]):m.AddHint(v,value)
   m.AddHint(vs['init'],hv['init'])
  for (u,v,t),(_,__,value) in zip(jobs,hh['jobs']):m.AddHint(t,value)
 # Absolute R is a compactness regularizer; pre-end delay and live exposure carry loss.
 obj=10*R+25*(R-PE-1)+10*sum(movecost)+sum(idle)+sum(R-t for t in pts)
 if a.calibration:
  w=json.loads(Path(a.calibration).read_text())['weights']
  raw=dict(pre_exposure=sum(R-t for t in pts),data_wait=sum(R-pts[per[q][-1]]-1 for q in D0),
   data_exposure=sum(R-pts[per[q][0]] for q in D0),a_exposure=sum(R-T[f'a{i}']['init'] for i in range(7)),
   bc_exposure=sum(R-T[f'{k}{i}']['init'] for k in 'bc' for i in range(7)))
  # Fits do not identify moves/CX in fixed-layout calibration, so these remain
  # explicit exploratory priors; actual ranking always uses exact and MC.
  obj=R+sum(round(w.get(k,0)*1e10)*v for k,v in raw.items())+1000*sum(movecost)
 m.Minimize(obj)
 s=cp_model.CpSolver();s.parameters.num_workers=a.workers;s.parameters.max_time_in_seconds=a.seconds
 s.parameters.stop_after_first_solution=a.first
 s.parameters.random_seed=a.seed;s.parameters.cp_model_presolve=False
 def result(cb,status):
  return dict(status=status,args=vars(a),R=cb.Value(R),RA=cb.Value(RA),pre_end=cb.Value(PE),proxy=cb.Value(obj),bound=primary_bound if phase2 else cb.BestObjectiveBound(),
   prefix_times=[cb.Value(x) for x in pts],mapping=mp,encoders=enc,permutations={k:[cb.Value(v) for v in vs] for k,vs in perms.items()},
   jobs=[(u,v,cb.Value(t)) for u,v,t in jobs],
   tokens={k:{name:([cb.Value(x) for x in val] if isinstance(val,list) else cb.Value(val)) for name,val in v.items()} for k,v in T.items()})
 out=HERE/a.out
 phase2=False;primary_bound=None
 class CB(cp_model.CpSolverSolutionCallback):
  def on_solution_callback(self):
   x=result(self,'FEASIBLE');out.with_suffix('.solver.json').write_text(json.dumps(x,indent=1));print('incumbent',x['proxy'],x['R'],self.WallTime(),flush=True)
 st=s.Solve(m,CB());first_status=st;winning=None;secondary_status=None
 if st in (cp_model.FEASIBLE,cp_model.OPTIMAL):winning=result(s,s.StatusName(st))
 if a.alap_tie and st in (cp_model.FEASIBLE,cp_model.OPTIMAL):
  primary_bound=s.BestObjectiveBound();primary_value=s.Value(obj);phase2=True;m.Add(obj==primary_value)
  m.Maximize(sum(pts)+sum(t for u,v,t in jobs)+sum(v['init']+sum(v['ts']) for k,v in T.items() if k[0]!='d')+sum(sum(v['ts']) for k,v in T.items() if k[0]=='d'))
  s.parameters.stop_after_first_solution=False
  s.parameters.max_time_in_seconds=30;st=s.Solve(m,CB());secondary_status=s.StatusName(st)
  if first_status!=cp_model.OPTIMAL and st==cp_model.OPTIMAL:st=cp_model.FEASIBLE
  if st in (cp_model.FEASIBLE,cp_model.OPTIMAL):winning=result(s,s.StatusName(st))
  elif winning is not None:
   # Preserve an actually feasible primary witness if tie-breaking times out.
   st=cp_model.FEASIBLE;winning['status']='FEASIBLE';winning['secondary_status']='TIMEOUT'
 status=s.StatusName(st)
 receipt=dict(status=status,result=('TIMEOUT' if st==cp_model.UNKNOWN else status),secondary_status=secondary_status,seconds=time.monotonic()-started,stats=s.ResponseStats(),args=vars(a))
 out.with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=1))
 if winning is not None:
  out.with_suffix('.solver.json').write_text(json.dumps(winning,indent=1))
  if not a.abstract:build(winning,out)
 print(json.dumps(receipt),flush=True)

def build(x,out):
 pre,dets=prefix();mp={int(k):v for k,v in x['mapping'].items()};us=[];T=x['tokens'];R=x['R'];RA=x.get('RA',R);bit=64;frames={k:set() for k in T}
 def add(t,lines,region='pre',round_offset=None):us.append(dict(t=t,lines=lines,region=region,**({'round_offset':round_offset} if round_offset is not None else {})))
 for u,t in zip(pre,x['prefix_times']):
  lines=[QRE.sub(lambda z:f'q[{mp[int(z.group(1))]}]',line) for line in u.lines]
  # Retain the native MX basis if the physical cell is reused later without reset.
  if u.name=='MX' and not lines[-1].startswith('h '):lines.append(f'h q[{mp[u.qs[0]]}];')
  add(t,lines)
 for k in 'abc':
  for i in range(7):
   v=T[f'{k}{i}'];q=v['pos'][0];add(v['init'],[f'reset q[{q}];']+([f'h q[{q}];'] if i in x['encoders'][k]['pivots'] else []),f'prep_{k}')
 for u,v,t in x['jobs']:add(t,[f"cx q[{T[u]['pos'][0]}],q[{T[v]['pos'][0]}];"],f'prep_{u[0]}')
 for key,v in T.items():
  k=key[0]
  for src,dst,t,mv in zip(v['pos'],v['pos'][1:],v['ts'],v['moves']):
   if not mv:continue
   add(t-1,[f'reset q[{dst}];']+([f'h q[{dst}];'] if k=='a' else []),'moves')
   if k=='d':add(t,[f'cx q[{src}],q[{dst}];'],'moves');add(t+1,[f'cx q[{dst}],q[{src}];'],'moves')
   else:
    c,z=(dst,src) if k=='a' else (src,dst)
    add(t,[f'cx q[{c}],q[{z}];'],'moves')
    add(t+1,([f'h q[{src}];'] if k!='a' else [])+[f'measure q[{src}] -> c[{bit}];']+([f'h q[{src}];'] if k!='a' else []),'moves')
    frames[key]^={bit};bit+=1
 ends={k:v['pos'][-1] for k,v in T.items()};bits={};perm=x.get('permutations',{k:list(range(7)) for k in 'abc'})
 for i in range(7):
  aa,bb,cc=(f'{k}{perm[k][i]}' for k in 'abc')
  add(RA,[f"cx q[{ends[f'd{i}']}],q[{ends[aa]}];"],'round_a',0)
  add(R,[f"cx q[{ends[bb]}],q[{ends[cc]}];"],'round',0)
  add(R+1,[f"cx q[{ends[bb]}],q[{ends[f'd{i}']}];"],'round',1)
  # C's teleport Z frame propagates onto B at B->C; it flips B readout only.
  frames[bb]^=frames[cc]
  for k in 'abc':
   bits[k,i]=bit;q=ends[f'{k}{i}'];add((RA+1) if k=='a' else R+(2 if k=='b' else 1),([f'h q[{q}];'] if k=='b' else [])+[f'measure q[{q}] -> c[{bit}];'],'round_a' if k=='a' else 'round',1 if k in 'ac' else 2);bit+=1
 for k in 'abc':
  for g in GENS+([list(range(7))] if k=='c' else []):
   bs={bits[k,i] for i in g}
   if k in 'ab':
    for i in g:bs^=frames[f'{k}{i}']
   dets.append('// DETECTOR '+' '.join(f'c[{b}]' for b in sorted(bs)))
 # Normalize folds before matching the schedule. Source-cell post-MX h is free.
 by={}
 for u in us:by.setdefault(u['t'],[]).extend(u['lines'])
 head=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];',f'creg c[{bit}];']
 txt=list(head)
 for t in sorted(by):txt+=by[t]+['barrier '+','.join(f'q[{q}]' for q in range(36))+';']
 txt=txt[:-1]+dets;text='\n'.join(txt)+'\n'
 h,raw,tail=S.qasm_ops(text);units=S.fold_units(raw);native=native_times(text,units)
 # Check every emitted unit against the planned layer after compression of empty
 # layers. A whole-circuit maximum-depth check alone can hide folding shifts.
 compressed={t:i for i,t in enumerate(sorted(by))}
 expected=[(compressed[u['t']],u['lines']) for u in sorted(us,key=lambda u:u['t'])]
 actual=[(t,u.lines) for t,u in zip(native,units)]
 assert expected==actual,('native schedule mismatch',expected,actual)
 actual_round=[t for u,t in zip(units,native) if t==compressed[RA] and u.lines[0] in [f"cx q[{ends[f'd{i}']}],q[{ends[f'a{perm['a'][i]}']}];" for i in range(7)]]
 assert max(native)<=R+2,(max(native),R)
 out.with_suffix('.qasm').write_text(text)
 meta=dict(data_qubits=[ends[f'd{i}'] for i in range(7)],R_native=actual_round,R_A_native=compressed[RA],R_BC_native=compressed[R],R_BD_native=compressed[R+1],R_model=R,native_depth=max(native)+1,solver=x,
  cx=sum(line.startswith('cx ') for line in text.splitlines()),block_moves=sum(sum(v['moves']) for k,v in T.items() if k[0]!='d'),data_hops=sum(sum(v['moves']) for k,v in T.items() if k[0]=='d'))
 out.with_suffix('.json').write_text(json.dumps(meta,indent=1));out.with_suffix('.units.json').write_text(json.dumps(us,indent=1))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--sym',type=int,default=0);p.add_argument('--row',type=int,default=0);p.add_argument('--col',type=int,default=0)
 p.add_argument('--option',choices=['l5_11','l5_12','l3_10'],default='l5_11');p.add_argument('--bc-option',choices=['l5_11','l5_12','l3_10'],default='l5_11');p.add_argument('--dhops',type=int,default=2);p.add_argument('--bhops',type=int,default=2)
 p.add_argument('--horizon',type=int,default=60);p.add_argument('--seconds',type=float,default=300);p.add_argument('--workers',type=int,default=8);p.add_argument('--seed',type=int,default=0);p.add_argument('--fixed-endpoints',action='store_true');p.add_argument('--hint');p.add_argument('--joint',action='store_true');p.add_argument('--calibration');p.add_argument('--early-a',action='store_true');p.add_argument('--automorphisms',action='store_true');p.add_argument('--alap-tie',action='store_true');p.add_argument('--pipeline',action='store_true')
 p.add_argument('--abstract',action='store_true');p.add_argument('--abstract-depth',type=int,default=6)
 p.add_argument('--reuse-a',action='store_true')
 p.add_argument('--first',action='store_true')
 p.add_argument('--solution-hint')
 p.add_argument('--encoders')
 solve(p.parse_args())
