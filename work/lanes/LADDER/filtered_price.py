"""Exact2 CLI with algebraic zero-acceptance pruning, no approximations.
Dependent detector projector products imply XOR constraints on fault signatures.
A violated identity has exactly zero postselected amplitude for every rotation.
All surviving rows use the unmodified Engine and exact2 pair/triple sums.
"""
import os,sys,runpy
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parents[2]/'work/lanes/EVAL'))
import numpy as np
from engine import Engine
from model import Basis
old_init=Engine.__init__;old_batch=Engine.batch_n;old_nt=Engine.ntable

def init(self,*args,**kwargs):
 old_init(self,*args,**kwargs)
 bas=Basis();indices=[];constraints=[]
 for i,(x,z,c) in enumerate(self.projs):
  combo=bas.express(x|(z<<self.r))
  if combo is None:bas.add(x|(z<<self.r));indices.append(i)
  else:
   rel=1<<i
   for j,bi in enumerate(indices):
    if combo>>j&1:rel^=1<<bi
   constraints.append(rel)
 self.zero_constraints=constraints
 # Validate each identity against reference signs indirectly by comparing every
 # single detector flip and the zero signature against the unmodified evaluator.
 for d in [0]+[1<<i for i in range(len(self.projs))]:
  if any((d&h).bit_count()%2 for h in constraints):
   a,n=old_nt(self,0,d)
   assert abs(a)<1e-15 and (n is None or np.max(abs(n))<1e-15),('invalid projector identity',d,a)

def nt(self,s,d):
 if any((int(d)&h).bit_count()%2 for h in self.zero_constraints):return 0.,None
 return old_nt(self,s,d)

def batch(self,S,D):
 D=np.asarray(D,dtype=np.int64);live=np.ones(len(D),dtype=bool)
 for h in self.zero_constraints:live &= (np.bitwise_count(D&h)&1)==0
 a=np.zeros(len(D));n=np.zeros((len(D),1024))
 if live.any():a[live],n[live]=old_batch(self,np.asarray(S)[live],D[live])
 return a,n
Engine.__init__=init;Engine.ntable=nt;Engine.batch_n=batch;Engine.ladder_pruned=True
# Preserve exact2's original distinct-channel fault enumeration and top triples;
# prune only class triples whose projector identity syndrome is nonzero.
import exact2,inspect,collections,hashlib,json
source=inspect.getsource(exact2._triple_chunk)
old_line='cs = np.arange(gb, len(ev.gkeys))'
new_line='cs = np.array([c for c in G["zero_groups"].get(G["zero_syndromes"][ga] ^ G["zero_syndromes"][gb], ()) if c >= gb], dtype=int)\n        if len(cs) == 0: continue'
assert source.count(old_line)==1
exec(compile(source.replace(old_line,new_line),'<exact2 mathematically zero class pruning>','exec'),exact2.__dict__)
base_third=exact2.third_order
def pruned_third(ev,procs):
 sy=[sum(((int(d)&h).bit_count()%2)<<j for j,h in enumerate(ev.e.zero_constraints)) for s,d in ev.gkeys]
 groups=collections.defaultdict(list)
 for i,y in enumerate(sy):groups[y].append(i)
 exact2.G['zero_syndromes']=sy;exact2.G['zero_groups']=groups
 return base_third(ev,procs)
exact2.third_order=pruned_third
print('Exact2 zero-acceptance class pruning; original _triple_chunk SHA256',hashlib.sha256(source.encode()).hexdigest(),flush=True)
runpy.run_path(str(H/'price.py'),run_name='__main__')
