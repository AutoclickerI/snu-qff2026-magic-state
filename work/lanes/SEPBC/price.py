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
import math,time
import categorical_cache as cc
started=time.monotonic();original_run=exact2.run;original_third=exact2.third_order;state={}
def capture_run(ev,*args,**kwargs):
 kwargs['keep_thr']=0.0;r=original_run(ev,*args,**kwargs);state.update(ev=ev,r=r);return r
def capture_third(ev,*args,**kwargs):
 key=cc.fingerprint(ev);state['categorical_key']=key;p=cc.path(key)
 if p.exists():
  cached=json.loads(p.read_text());assert abs(cached['second']-state['r']['loss2'])<1e-15
  r=(cached['third']-state['r']['t3bc'],[]);state['third_reused_from']=cached['stem'];print('Exact categorical-equivalent third-order reuse:',cached['stem'],key,flush=True)
 else:
  r=original_third(ev,*args,**kwargs);cc.store(key,dict(stem=str(Path(sys.argv[1]).with_suffix('')),second=state['r']['loss2'],third=r[0]+state['r']['t3bc']))
 state['triple']=r;return r
exact2.run=capture_run;exact2.third_order=capture_third
exact2.main()
ev,r=state['ev'],state['r'];t3=state.get('triple',(0,[]))[0]+r['t3bc']
stem=Path(sys.argv[1]).with_suffix('');pairs=collections.Counter();examples={}
md=json.loads(stem.with_suffix('.json').read_text());R=md.get('R',45)
data=set(md['data_qubits']);aa={1,14,8,9,2,16,15};bb={6,26,13,11,4,23,27};cc={12,25,19,17,5,29,28}
def region(ch):
 lab=ev.chan_label(ch);start=int(lab['steps'].split('..')[0]) if lab['steps']not in('None',None)else -1;qs=set(lab['qubits'])
 if start>=R:return 'round'
 if lab['kind']=='idle'and qs<=data:return 'data_idle'
 if qs<=aa:return 'A_region'
 if qs<=bb|cc|{18,24,30,31,32,33,34,35}and start>=28:return 'BC_region'
 return 'prefix_or_moves'
for value,i,j,n,a in r['big']:
 key=' x '.join(sorted([region(ev.fch[i]),region(ev.fch[j])]))
 pairs[key]+=value
 if value>examples.get(key,[0])[0]:examples[key]=[value,ev.fault_label(i),ev.fault_label(j)]
out=dict(c1=r['loss1'],second=r['loss2'],third=t3,total=r['loss']+t3,exp_minus_A1=math.exp(-r['A1']),seconds=time.monotonic()-started,pair_classes=dict(pairs.most_common()),examples=examples,evaluator='Exact2 CLI with exact zero-acceptance pruning; physical adjacency and all surviving arithmetic unchanged')
out.update(categorical_key=state.get('categorical_key'),third_reused_from=state.get('third_reused_from'))
stem.with_suffix('.price.json').write_text(json.dumps(out,indent=2))
with(H/'REPORT.md').open('a')as f:f.write('\nExact2 verified `'+stem.name+'`: '+json.dumps(out)+'\n')
print('PRICE',json.dumps(out),flush=True)
