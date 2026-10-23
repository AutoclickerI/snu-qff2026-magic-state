"""Physical Bell-round construction and exact-X/Y scheduling; fixed submitted pre-stage."""
import sys,os,json,itertools,math,random,time,hashlib,collections
from pathlib import Path
from prefix import *
import stim,numpy as np
import xtim,tprep
xtim.cache_dir=str(HERE/'.xtim_cache')
os.environ['XTIM_TWIRL_CACHE_DIR']=str(HERE/'.twirl_cache')
from ortools.sat.python import cp_model
from tprep.noise import noise_blocks,STANDARD
import relaxed
from topology import W4,adj
import exact_proxy as ep

class Cycle:
 def __init__(self,layout,leaves=(),orient=(0,0,0)):
  self.layout=layout;self.pos=layout['pos'];self.leaves=list(leaves);self.orient=list(orient)
  self.nodes=[];self.tags=[];self.deps=set();self.cp={};self.measure={};self.move_end={};self.init={}
  def add(tag,k,qs,b=None):
   j=len(self.nodes);self.tags.append(tag);self.nodes.append((k,tuple(qs),b));return j
  self.add=add
  for d,(src,dst) in enumerate(zip(DATA0,self.pos)):
   if src==dst:continue
   r=add(('MR',d),'R',[dst]);a=add(('M',d,0),'CX',[src,dst]);b=add(('M',d,1),'CX',[dst,src])
   self.deps|={(r,a),(a,b)};self.move_end[d]=b
  self.initial_state={}
  def init(q,basis):
   assert q not in self.pos
   if q in RETAINED and basis=='X':self.initial_state[q]='RX';return None
   if q in DATA0 and q not in self.pos and basis=='Z':return None
   j=add(('R',q),'RX' if basis=='X' else 'R',[q]);self.init[q]=j;return j
  bits=14;self.detectors=[]
  for t,edge in enumerate(layout['bells']):
   # Choose retained + as Bell root when available.
   root,target=sorted(edge,key=lambda q:(q not in RETAINED,q))
   for q,B in ((root,'X'),(target,'Z')):init(q,B)
   bell=add(('B',t),'CX',[root,target])
   for q in edge:
    if q in self.init:self.deps.add((self.init[q],bell))
   ax,az=edge if not orient[t] else edge[::-1]
   u=add(('U',t),'CX',[ax,az]);self.deps.add((bell,u))
   leaf_by_d={l['data']:l for l in leaves if l['tile']==t}
   attach={}
   for d,l in leaf_by_d.items():
    c=l['cell'];parent=l['parent'];init(c,'Z')
    a=add(('A',t,d),'CX',[parent,c]);attach[d]=a
    self.deps.add((bell,a))
    if c in self.init:self.deps.add((self.init[c],a))
    if parent==az:self.deps.add((a,u))
   touched=collections.defaultdict(list)
   for typ,support in (('X',layout['xs'][t]),('Z',layout['zs'][t])):
    for d in sorted(W4[support]):
     member=leaf_by_d[d]['cell'] if typ=='X' and d in leaf_by_d else next(q for q in edge if adj(q,self.pos[d]))
     j=add(('C',t,d,typ),'CX',[member,self.pos[d]] if typ=='X' else [self.pos[d],member]);self.cp[t,d,typ]=j
     self.deps.add((attach[d] if typ=='X' and d in leaf_by_d else bell,j))
     if d in self.move_end:self.deps.add((self.move_end[d],j))
     if member in edge and ((member==ax and typ=='Z') or (member==az and typ=='X')):self.deps.add((j,u))
     touched[member].append(j)
   per={'X':[],'Z':[]}
   for q,B in [(ax,'X'),(az,'Z')]+[(l['cell'],'X') for l in leaves if l['tile']==t]:
    b=bits;bits+=1;j=add(('read',t,q),'MX' if B=='X' else 'M',[q],b);per[B].append(b)
    for k in touched[q]:self.deps.add((k,j))
    self.deps.add((u if q in edge else attach[next(d for d,l in leaf_by_d.items() if l['cell']==q)],j))
    self.measure[b]=(t,B)
   self.detectors += [per['X'],per['Z']]
  self.nbits=bits
  # Original data cells are unavailable as ancillas until their two-CX move exits.
  for j,(k,qs,b) in enumerate(self.nodes):
   if self.tags[j][0] in ('M','MR'):continue
   for d,end in self.move_end.items():
    if DATA0[d] in qs and DATA0[d] not in self.pos:self.deps.add((end,j))
  self.lower=[max([nt[i]+1 for i,pre in enumerate(OPS[:NPRE]) if not self.commutes((k,qs,b),pre)]+[0]) for k,qs,b in self.nodes]
  self.fixed={(q,nt[i]) for i,(k,qs,b) in enumerate(OPS[:NPRE]) for q in qs}
  self.byq=collections.defaultdict(list)
  for j,(k,qs,b) in enumerate(self.nodes):
   for q in qs:self.byq[q].append(j)
  self.cache={}
 @staticmethod
 def commutes(op,pre):
  k,qs,_=op;pk,pqs,_=pre
  if not set(qs)&set(pqs):return True
  if k=='CX' and pk=='cx':return qs[0]!=pqs[1] and pqs[0]!=qs[1]
  if k=='CX' and pk in ('g:t','g:tdg','g:s','g:sdg','g:z'):return pqs[0]==qs[0]
  return False
 def norm(self,ts):
  live=sorted(set(nt[i] for i in range(NPRE))|set(ts));ix={t:i for i,t in enumerate(live)}
  return [ix[t] for t in ts]
 def reference_seed(self):
  by=collections.defaultdict(list)
  for i,(k,qs,b) in enumerate(OPS[NPRE:],NPRE):by[native(k),qs].append(nt[i])
  need=collections.Counter((k,qs) for k,qs,b in self.nodes)
  if need!=collections.Counter({k:len(v) for k,v in by.items()}):return None
  for v in by.values():v.sort(reverse=True)
  ts=[by[k,qs].pop() for k,qs,b in self.nodes]
  return ts if self.valid(ts) else None
 def valid(self,ts):
  if any(t<lo for t,lo in zip(ts,self.lower)):return False
  if any((q,ts[j]) in self.fixed for j,(k,qs,b) in enumerate(self.nodes) for q in qs):return False
  if any(ts[a]>=ts[b] for a,b in self.deps):return False
  if any(len({ts[j] for j in js})<len(js) for js in self.byq.values()):return False
  sch=[[] for _ in range(7)]
  for (tile,d,typ),j in self.cp.items():
   S=W4[self.layout['xs' if typ=='X' else 'zs'][tile]];cid=(typ,relaxed.W4.index(S));sch[d].append((ts[j],cid,typ))
  return relaxed.valid(sch)
 def solve(self,seed=0,horizon=65):
  m=cp_model.CpModel();v=[m.NewIntVar(lo,horizon,f't{j}') for j,lo in enumerate(self.lower)]
  for a,b in self.deps:m.Add(v[a]<v[b])
  for j,(k,qs,b) in enumerate(self.nodes):
   for q,t in self.fixed:
    if q in qs:m.Add(v[j]!=t)
  for js in self.byq.values():m.AddAllDifferent([v[j] for j in js])
  for tx in range(3):
   for tz in range(3):
    shared=W4[self.layout['xs'][tx]]&W4[self.layout['zs'][tz]];bs=[]
    for d in shared:
     b=m.NewBoolVar(f'ord{tx}_{tz}_{d}');m.Add(v[self.cp[tx,d,'X']]<v[self.cp[tz,d,'Z']]).OnlyEnforceIf(b);m.Add(v[self.cp[tx,d,'X']]>v[self.cp[tz,d,'Z']]).OnlyEnforceIf(b.Not());bs.append(b)
    z=m.NewIntVar(0,len(bs)//2,'parity');m.Add(sum(bs)==2*z)
  # A deterministic start: collect all Z parities before X, then disentangle.
  for j,tag in enumerate(self.tags):
   if tag[0]=='U':
    for (tile,d,B),k in self.cp.items():
     if tile==tag[1]:m.Add(v[k]<v[j])
  for (tx,dx,Bx),jx in self.cp.items():
   if Bx!='X':continue
   for (tz,dz,Bz),jz in self.cp.items():
    if Bz=='Z':m.Add(v[jz]<v[jx])
  end=m.NewIntVar(max(self.lower),horizon,'end');m.AddMaxEquality(end,v)
  # At fixed depth, push preparations late and measurements early.
  m.Minimize(10000*end+sum(v[j] for j,(k,_,_) in enumerate(self.nodes) if k in ('M','MX'))-sum(v[j] for j,(k,_,_) in enumerate(self.nodes) if k in ('R','RX')))
  s=cp_model.CpSolver();s.parameters.num_search_workers=1;s.parameters.max_time_in_seconds=8;s.parameters.random_seed=seed
  status=s.Solve(m)
  if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE):return None,s.StatusName(status)
  ts=[s.Value(x) for x in v];assert self.valid(ts)
  return ts,s.StatusName(status)
 def text(self,ts):return emit(self.nodes,ts,self.detectors,self.nbits)
 def probes(self,ts):
  text=self.text(ts);st,labels,errs=convert(text);assert not errs,errs
  prog,steps,gaps=schedule(st);_,blocks=noise_blocks(st,.001,STANDARD)
  # Identify exact fixed-prefix operations by signature and native time.
  pre_keys={(native(k),qs,nt[i]):i for i,(k,qs,b) in enumerate(OPS[:NPRE])}
  cycle_keys={(k,qs,t):j for j,((k,qs,b),t) in enumerate(zip(self.nodes,ts))}
  gapcount=collections.Counter(i for i,q,first,n in gaps)
  body=[];bits=[]
  for q,k in self.initial_state.items():body.append(f'{k} {q}')
  for ii,ins in enumerate(prog):
   if not steps[ii]:continue
   key=(ins.name,tuple(ins.qubits),steps[ii][0][1])
   if key in cycle_keys:
    j=cycle_keys[key];body+=blocks[ii]
    if ins.name in ('M','MX'):bits.append(self.nodes[j][2])
   else:
    i=pre_keys[key]
    # Keep only waiting noise after the final fixed pre-stage operation on a wire.
    for jj,q,first,n in gaps:
     if jj!=ii:continue
     if steps[ii][0][1]!=PRE_LAST.get(q):continue
     if q not in DATA0 and q not in self.initial_state:continue
     prob=.75*(1-(1-4*.001/3)**n);body.append(f'DEPOLARIZE1({prob}) {q}')
  # All cycle detectors correspond to a measured X/Z stabilizer.
  from topology import W4 as WW
  base=[WW[k] for k in (0,1,3)]
  def gens(s):
   for mask in range(1,8):
    acc=frozenset()
    for k in range(3):
     if mask>>k&1:acc^=base[k]
    if acc==s:return [k for k in range(3) if mask>>k&1]
   raise ValueError(s)
  def mpp(B,qs):return 'MPP '+'*'.join(f'{B}{q}' for q in qs)
  def full(L):
   lines=[mpp(B,[DATA0[d] for d in sorted(s)]) for B in 'XZ' for s in base]+[mpp(L,DATA0)]
   lines+=body
   lines+=[mpp(B,[self.pos[d] for d in sorted(s)]) for B in 'XZ' for s in base]+[mpp(L,self.pos)]
   n=14+len(bits);rec=lambda j:f'rec[{j-n}]';bp={b:i for i,b in enumerate(bits)}
   for ds in self.detectors:
    tile,B=self.measure[ds[0]];support=WW[self.layout['xs' if B=='X' else 'zs'][tile]]
    ini=[(0 if B=='X' else 3)+k for k in gens(support)]
    lines.append('DETECTOR '+' '.join([rec(7+bp[b]) for b in ds]+[rec(k) for k in ini]))
   for k in range(7):lines.append(f'OBSERVABLE_INCLUDE({k}) {rec(7+len(bits)+k)} {rec(k)}')
   return stim.Circuit('\n'.join(lines))
  return full('X'),full('Y')
 def cost(self,ts):
  if not self.valid(ts):return None
  key=tuple(ts)
  if key not in self.cache:
   try:
    x,y=self.probes(ts);r=ep.exact_loss(x,y,details=True)
    # The first-order term is part of the objective; no FT-only filter is used.
    self.cache[key]=ep.conditional_loss(x,y)
   except ValueError as e:
    if 'non-deterministic' in str(e):self.cache[key]=None
    else:raise
  return self.cache[key]
 def anneal(self,initial,seed=0,steps=1500):
  rng=random.Random(seed);ts=list(initial);cur=self.cost(ts)
  if cur is None:return None
  best=(cur,list(ts));ceil=max(ts)+2
  for it in range(steps):
   tt=list(ts);j=rng.randrange(len(tt));r=rng.random()
   if r<.25:
    k=rng.randrange(len(tt));tt[j],tt[k]=tt[k],tt[j]
   else:
    t=rng.randint(max(self.lower[j],ts[j]-3),min(ceil,ts[j]+3));old=tt[j];tt[j]=t
    if r<.7:
     for k,(kind,qs,b) in enumerate(self.nodes):
      if j!=k and tt[k]==t and set(qs)&set(self.nodes[j][1]):tt[k]=old
   tt=self.norm(tt);val=self.cost(tt)
   if val is None:continue
   temp=2e-6*(.02**(it/max(1,steps)))
   if val<cur or rng.random()<math.exp(min(0,(cur-val)/temp)):
    cur=val;ts=tt
    if cur<best[0]:best=(cur,list(ts))
  return best

def variants(layout):
 occupied=set(layout['pos'])|set(sum(layout['bells'],[]));choices=[]
 for t,edge in enumerate(layout['bells']):
  for d in sorted(W4[layout['xs'][t]]):
   for c in range(36):
    if c in occupied or not adj(c,layout['pos'][d]):continue
    for p in edge:
     if adj(c,p):choices.append(dict(tile=t,data=d,cell=c,parent=p))
 out=[]
 for mask in range(1<<len(choices)):
  leaf=[c for j,c in enumerate(choices) if mask>>j&1]
  if len({x['cell'] for x in leaf})<len(leaf) or len({(x['tile'],x['data']) for x in leaf})<len(leaf):continue
  out.append(leaf)
 return out

def job(args):
 idx,layout,leaves,orient,seed,steps=args
 start=time.time();m=Cycle(layout,leaves,orient);ts,status=m.solve(seed)
 r=dict(index=idx,layout=layout,leaves=leaves,orient=orient,solver=status,seed=seed)
 if ts is not None:
  reference=m.reference_seed()
  if reference is not None:ts=reference;r['start']='submitted v12'
  ts=m.norm(ts)
  val=m.cost(ts);r.update(initial=val,initial_times=ts)
  if val is not None:
   best=m.anneal(ts,seed,steps);r.update(proxy=best[0],times=best[1],nodes=m.nodes,detectors=m.detectors,data_qubits=m.pos,nbits=m.nbits,depth=max(best[1])+1)
   r['all_orders']=ep.conditional_loss(*m.probes(best[1]))
   r['proxy_second']=ep.exact_loss(*m.probes(best[1]))
   name=f'cycle_{idx:04d}';text=m.text(best[1]);r['prefix_audit']=audit(text)
   rep=tprep.check(text,m.pos,shots=10**6,seed=0)
   r['check']=dict(passed=rep.passed,score=rep.score,acceptance=rep.acceptance,shots=10**6,report=str(rep))
   if not rep.passed:
    r['seconds']=time.time()-start;return r
   (HERE/f'{name}.qasm').write_text(text);(HERE/f'{name}.json').write_text(json.dumps(r,indent=2))
 r['seconds']=time.time()-start;print(json.dumps({k:v for k,v in r.items() if k in ('index','solver','initial','proxy','all_orders','depth','seconds')}),flush=True)
 return r

def main():
 import argparse,multiprocessing as mp
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=10);p.add_argument('--steps',type=int,default=1800);p.add_argument('--mode',default='search');p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1);a=p.parse_args()
 lays=json.loads((HERE/'relocations.json').read_text())['layouts']
 tasks=[]
 for layout in lays:
  for leaves in variants(layout):
   for orient in itertools.product((0,1),repeat=3):
    tasks.append((len(tasks),layout,leaves,orient,200+len(tasks),a.steps))
 (HERE/'search_manifest.json').write_text(json.dumps(dict(layouts=len(lays),tasks=len(tasks),variants_per_layout=[len(variants(l)) for l in lays],workers=a.workers,steps=a.steps),indent=2))
 if a.mode=='count':print(len(tasks),flush=True);return
 if a.mode=='test':tasks=[tasks[0]]
 tasks=[t for t in tasks if t[0]%a.shards==a.shard]
 path=HERE/f'search_results_{a.shard}.json'
 rows=json.loads(path.read_text()) if path.exists() else []
 done={r['index'] for r in rows};tasks=[t for t in tasks if t[0] not in done]
 with mp.get_context('fork').Pool(a.workers) as pool:
  for r in pool.imap_unordered(job,tasks):
   rows.append(r);(HERE/f'search_results_{a.shard}.json').write_text(json.dumps(rows,indent=2))
if __name__=='__main__':main()
