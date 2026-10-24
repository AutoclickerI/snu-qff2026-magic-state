"""v36b native population context, exact fitness and static dispatch screen."""
import os,sys,json,re,time,copy,hashlib,contextlib,io
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;ROOT=H.parents[2];sys.path.insert(0,str(H))
import acceptance as a,knapsack_select as k
C=a.C;d=a.d;OUT=H/'pop36b';OUT.mkdir(exist_ok=True)
a.OUT=OUT;a.BASE_LOSS=4.129326085269341e-5;a.BASE_ACC=.5014386391688026;a.FLOOR=.5002
INCUMBENT=4.146051958326e-5
oldnorm=d.normalize
def normalize(c):
 c=oldnorm(c);c['meta']={key:c['meta'][key]for key in ('data_qubits','cx','native_depth','round_range')};c['meta'].update(R=max(c['meta']['round_range']),source='MAIN/v36b population');return c
d.normalize=normalize
def digest(c):
 # Classical record names are labels. Collapse parallel-order and record-ID
 # variants before spending exact-contraction time on the same instrument.
 order=sorted(range(len(c['u'])),key=lambda i:(c['t'][i],tuple(re.sub(r'c\[\d+\]','c[]',s)for s in c['u'][i].lines)))
 records={}
 for i in order:
  for line in c['u'][i].lines:
   if '->'in line:
    b=a.bits(line)[0]
    if b not in records:records[b]=len(records)
 def rewrite(s):return re.sub(r'c\[(\d+)\]',lambda m:f'c[{records[int(m[1])]}]',s)
 layers=sorted((c['t'][i],tuple(rewrite(s)for s in c['u'][i].lines))for i in order)
 tail=sorted(tuple(sorted(records[b]for b in a.bits(s)))for s in c['tail']if s.startswith('// DETECTOR'))
 return hashlib.sha256(json.dumps([layers,tail]).encode()).hexdigest()[:14]
d.digest=digest
import general_atoms as ga
C.xtim.cache_dir=str(H/'.xtim_cache');os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')

def score(job):
 import sparse_budget
 path,desc=job;p=Path(path);start=time.monotonic();r=dict(stem=str(p.relative_to(H)),description=desc,exp_minus_A1=None,method='canonical sparse all-orders; static dispatch then exact acceptance')
 try:
  static=ga.analyze(p);p.with_suffix('.static.json').write_text(json.dumps(static,indent=2));r['static']=static
  if static['prediction']!='FAST':r.update(ok=False,eligible=False,error='static dispatch '+static['prediction'])
  else:
   ao=sparse_budget.run(p,a.FLOOR);r.update(ok=True,acceptance=ao['acceptance'],eligible=ao['eligible'],acceptance_screen_exact=True,conditioned_width=ao['conditioned_width'])
   if ao['eligible']:r.update(loss=ao['loss'],omission_bound=ao['conditional_loss_kernel_omission_bound'],delta_loss=ao['loss']-a.BASE_LOSS,acceptance_recovered=ao['acceptance']-a.BASE_ACC)
 except Exception as e:r.update(ok=False,error=repr(e))
 r['seconds']=time.monotonic()-start;p.with_suffix('.score.json').write_text(json.dumps(r,indent=2));return r
a.score=score

def apply_patch(c,p,adapt=False):
 # Patches here are re-derived on the current base, so enforce exact sites.
 return k.apply(c,[p])

def renumber_patch(p,c):
 p=copy.deepcopy(p);donor={b for u in C.read(OUT/'base')['u']for line in u.lines for b in a.bits(line)}
 removed={b for _,ls in p['remove']for line in ls for b in a.bits(line)}
 new=sorted({b for _,ls in p['add']for line in ls if '->'in line for b in a.bits(line)}-donor-removed);mapping={b:C.bit(c)+j for j,b in enumerate(new)}
 def f(s):return re.sub(r'c\[(\d+)\]',lambda m:f'c[{mapping.get(int(m[1]),int(m[1]))}]',s)
 p['add']={(t,tuple(f(s)for s in ls))for t,ls in p['add']};p['add_tail']={f(s)for s in p['add_tail']};return p

def save_patch(name,base,c,desc):
 p=k.patches(base,c);return dict(name=name,description=desc,patch={key:sorted([list(x)if isinstance(x,tuple)else x for x in val],key=str)for key,val in p.items()})
