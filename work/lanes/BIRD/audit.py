"""BIRD-only evidence: provenance, ablations, and exact small terminal-channel audit."""
import os, sys, json, collections, itertools, math, hashlib
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(__file__).resolve().parent
for x in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[x]='1'
sys.path[:0]=[str(ROOT/'work/lanes/BCFB'),str(ROOT/'work/lanes/MAIN'),str(ROOT/'work/lanes/EVAL'),str(ROOT/'work/lanes/SCHED'),str(ROOT/'work/lanes/TREP'),str(ROOT/'work')]
import numpy as np
import exact2, model, regions as R, schedule as S
from util import native_times
from moments_vector import evaluate
import bounds
STEM=ROOT/'work/lanes/MAIN/v23h_c2c9'

def load(stem):
 text=stem.with_suffix('.qasm').read_text();meta=json.loads(stem.with_suffix('.json').read_text());_,raw,_=S.qasm_ops(text);u=S.fold_units(raw);t=native_times(text,u)
 return text,meta,u,t

def provenance():
 text,meta,u,t=load(STEM);_,ref,ru,rt=load(ROOT/'work/lanes/HOPS/hop_early')
 keys=set();counts=collections.Counter();pref=set(ref['prefix_unit_indices'])
 for i,v in enumerate(ru):
  k=tuple(v.lines);counts[k]+=1
  if i in pref:keys.add((k,counts[k]))
 counts.clear();pu=[]
 for i,v in enumerate(u):
  k=tuple(v.lines);counts[k]+=1
  if (k,counts[k]) in keys or v.name in ('T','TDG'):pu.append(i)
 meta=dict(meta,prefix_unit_indices=pu,_stem=str(STEM))
 reg=R.unit_regions(u,t,meta)
 # Explicit transfer identity: all six two-CX transfers in the inspected QASM.
 # Preserve the reconstructed prefix and final round; classify remaining resets/readouts by cells.
 hops=[(4,10),(15,16),(8,9),(9,15),(15,21),(16,22)]
 for a,b in hops:
  inds=[i for i,v in enumerate(u) if reg[i]!='pre' and t[i]<meta['R'] and v.name=='CX' and set(v.qs)=={a,b}]
  inds=sorted(inds,key=lambda i:t[i])[:2]
  assert len(inds)==2,(a,b,inds)
  for i in inds:reg[i]='hop'
 counts={g:sum(v.name=='CX' and r==g for v,r in zip(u,reg)) for g in R.REGIONS}
 inv=[]
 for i,(v,st,r) in enumerate(zip(u,t,reg)):inv.append(dict(unit=i,step=int(st),region=r,name=v.name,qs=list(v.qs),lines=list(v.lines)))
 (OUT/'inventory.json').write_text(json.dumps(dict(sha256=hashlib.sha256(text.encode()).hexdigest(),cx_counts=counts,depth=max(t)+1,units=inv),indent=2))
 print('CX_COUNTS',counts,'depth',max(t)+1,'R',meta['R'],flush=True)
 return text,meta,u,t,reg

def ablations():
 text,meta,u,t,reg=provenance();orig=model.noise_blocks;results={}
 def score(name,patch):
  model.noise_blocks=patch
  try:row=evaluate(exact2.Eval(text,meta['data_qubits']))
  finally:model.noise_blocks=orig
  results[name]=row;(OUT/'ablations.json').write_text(json.dumps(results,indent=2));print(name,json.dumps(row),flush=True)
 score('all',orig)
 for g in ['pre','A','BC','hop','round']:
  score('no_'+g,R.patch(text,u,reg,lambda r,g=g:r!=g))
 for name,kept in [('only_round',{'round'}),('only_BC',{'BC'}),('only_A',{'A'}),('only_pre',{'pre'}),('only_hop',{'hop'}),('no_pre_A_BC_hop',{'round','other'}),('no_A_BC',{'pre','hop','round','other'})]:
  score(name,R.patch(text,u,reg,lambda r,kept=kept:r in kept))
 # All physical data-storage idle exposure before the round, with moving data tokens tracked.
 tokens={0,20,7,4,3,15,8};token_by_step={};seen=collections.Counter()
 for st in range(max(t)+1):
  token_by_step[st]=set(tokens)
  for v,r,tt in zip(u,reg,t):
   if tt==st and r=='hop' and v.name=='CX':
    pair=frozenset(v.qs);seen[pair]+=1
    if seen[pair]==2:tokens^=set(pair)
 ranges=[]
 from tprep.noise import schedule as ns
 def data_idle_patch(f):
  def nb(txt,p,noise,first_order=False):
   prog,blocks=orig(txt,p,noise,first_order);_,steps,gaps=ns(txt)
   for i,q,first,n in gaps:
    removed=sum(s<meta['R'] and q in token_by_step.get(s,set()) for s in range(first,first+n))
    if not removed:continue
    ranges.append((q,first,n,removed))
    for j in range(len(blocks[i])-1,-1,-1):
     if blocks[i][j].startswith('DEPOLARIZE1(') and blocks[i][j].split()[-1]==str(q):
      duration=n-(1-f)*removed;blocks[i][j]=f'DEPOLARIZE1({.75*(1-(1-4*p/3)**duration)}) {q}';break
   return prog,blocks
  return nb
 score('data_idle_half',data_idle_patch(.5));score('data_idle_zero',data_idle_patch(0))
 (OUT/'data_idle_ranges.json').write_text(json.dumps(sorted(set(ranges)),indent=2))

def floors():
 # No probability cutoff. Binary Pauli encoding: X=1,Z=2,Y=3.
 pat=np.array(list(itertools.product(range(4),repeat=7)),dtype=np.uint8)
 xx=np.sum(((pat&1)>0)*(1<<np.arange(7)),axis=1);zz=np.sum(((pat&2)>0)*(1<<np.arange(7)),axis=1)
 def logical(a):
  syn=np.zeros(a.shape,dtype=np.uint8)
  for j in range(7):syn^=np.where(a&(1<<j),j+1,0).astype(np.uint8)
  return (np.bitwise_count(a)&1)^(syn!=0)
 fx=logical(xx);fz=logical(zz);cost=np.where(fx,.5,np.where(fz,1.,0.))
 def full(m):
  probs=np.ones(len(pat))
  for i,mm in enumerate(m):
   d=np.array([1-sum(mm.values()),mm['X'],mm['Z'],mm['Y']]);probs*=d[pat[:,i]]
  return float(probs@cost)
 vals={}
 for dummy in (False,True):
  mm=[bounds.final_step(dummy)]*7;vals['final_dummy_'+str(dummy)]=dict(pair=bounds.pair_loss(mm),enumerated=full(mm),old_cutoff=bounds.exact_loss(mm))
 for kind in ('direct','bell'):
  for dummy in ((False,True) if kind=='direct' else (False,)):
   choices=[(bounds.pair_loss([bounds.tail(kind,o,dummy=dummy) for o in ori]),ori)for ori in itertools.product('XZ',repeat=7)]
   p2,ori=min(choices);mm=[bounds.tail(kind,o,dummy=dummy) for o in ori]
   vals[kind+'_dummy_'+str(dummy)]=dict(pair=p2,enumerated_linear_masses=full(mm),orientation=''.join(ori))
 # Minimize the final noisy-step relaxation over arbitrary pre-noise states.
 # Recovery adjoint is block diagonal in the 64 stabilizer syndrome sectors.
 # In each sector its max eigenvalue is (1+hypot(Cx,Cy)/sqrt(2))/2.
 reps=[0]+[1<<j for j in range(7)]
 chars=[]
 for x in reps:
  for z in reps:
   a=logical(xx^x);b=logical(zz^z)
   chars.append(np.stack((1-2*b.astype(float),1-2*(a^b).astype(float)),axis=1))
 chars=np.stack(chars,axis=1)
 def matchings(qs):
  if not qs:yield [];return
  a,*rest=qs
  for tail in matchings(rest):yield [(a,)]+tail
  for b in rest:
   for tail in matchings([x for x in rest if x!=b]):yield [(a,b)]+tail
 rows=[]
 for parts in matchings(list(range(7))):
  probs=np.ones(len(pat))
  for block in parts:
   if len(block)==1:probs*=np.where(pat[:,block[0]]==0,1-.0008,.0008/3)
   else:probs*=np.where((pat[:,block[0]]==0)&(pat[:,block[1]]==0),.999,.001/15)
  c=np.einsum('i,isk->sk',probs,chars);loss=(1-np.hypot(c[:,0],c[:,1])/math.sqrt(2))/2
  rows.append(dict(parts=parts,minimum=float(min(loss)),sector=int(np.argmin(loss)),code_target_loss=float(probs@cost)))
 vals['terminal_relaxation']={str(k):dict(minimum=min(r['minimum'] for r in rows if sum(len(b)==2 for b in r['parts'])==k),cases=sum(sum(len(b)==2 for b in r['parts'])==k for r in rows))for k in range(4)}
 (OUT/'floors.json').write_text(json.dumps(vals,indent=2));print(json.dumps(vals,indent=2))

if __name__=='__main__':
 {'floors':floors,'ablations':ablations,'inventory':provenance}[sys.argv[1]]()
