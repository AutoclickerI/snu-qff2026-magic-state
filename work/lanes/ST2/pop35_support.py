"""Current-base native edits and all-orders scoring for ST2's population."""
import os,sys,json,re,copy,hashlib,itertools
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H))
import acceptance as a,knapsack_select as k
C=a.C;d=a.d;ROOT=H.parents[2];OUT=H/'pop35b';OUT.mkdir(exist_ok=True)
a.OUT=OUT;a.BASE_LOSS=4.376021340833061e-5;a.BASE_ACC=.5016883498058476

def population_score(job):
 # Direct exact fitness: the old reusable batch scorer also enumerated every
 # single fault solely for a diagnostic. That does not affect population rank.
 import time,sparse_budget
 path,desc=job;p=Path(path);start=time.monotonic();r=dict(stem=str(p.relative_to(H)),description=desc,exp_minus_A1=None,method='canonical sparse all-orders; exact acceptance first')
 try:
  ao=sparse_budget.run(p,.5005);r.update(ok=True,acceptance=ao['acceptance'],eligible=ao['eligible'],acceptance_screen_exact=True,conditioned_width=ao['conditioned_width'])
  if ao['eligible']:r.update(loss=ao['loss'],omission_bound=ao['conditional_loss_kernel_omission_bound'],delta_loss=ao['loss']-a.BASE_LOSS,acceptance_recovered=ao['acceptance']-a.BASE_ACC)
 except Exception as e:r.update(ok=False,error=repr(e))
 r['seconds']=time.monotonic()-start;p.with_suffix('.score.json').write_text(json.dumps(r,indent=2));return r
a.score=population_score
oldnorm=d.normalize
def normalize(c):
 c=oldnorm(c);c['meta']={key:c['meta'][key]for key in ('data_qubits','cx','native_depth','round_range')};c['meta'].update(R=max(c['meta']['round_range']),source='MAIN/v35b population');return c
d.normalize=normalize

def apply_patch(c,p,adapt=False):
 x=C.clone(c);need=set(p['remove']);present={(t,tuple(u.lines)):i for i,(u,t)in enumerate(zip(x['u'],x['t']))};remove=set();adaptmap={}
 for item in need:
  if item in present:remove.add(present[item]);continue
  if not adapt:raise ValueError(('patch conflict',item))
  # Preserve current instrument when porting a time-only edit of that site.
  t,ls=item;u=C.Unit(list(ls));same=[(key,i)for key,i in present.items()if key[0]==t and x['u'][i].qs==u.qs and len(u.qs)==1]
  moved=[(tt,ll)for tt,ll in p['add']if ll==ls]
  if same and moved:
   key,i=same[0];remove.add(i);adaptmap[ls]=tuple(x['u'][i].lines)
  elif moved:adaptmap[ls]=None
  else:raise ValueError(('patch conflict',item))
 a.remove_units(x,remove)
 existing={(t,tuple(u.lines))for u,t in zip(x['u'],x['t'])}
 for t,ls in p['add']:
  if ls in adaptmap:ls=adaptmap[ls]
  if ls is None:continue
  if (t,ls)not in existing:x['u'].append(C.Unit(list(ls)));x['t'].append(t)
 x['tail']=[s for s in x['tail']if s not in p['remove_tail']];x['tail'].extend(sorted(p['add_tail']-set(x['tail'])))
 return d.normalize(x)

def external_patches():
 base=C.read(ROOT/'work/lanes/MAIN/v35a');out=[]
 menu=ROOT/'work/lanes/WAITPROT/menu_v35a.json'
 if menu.exists():
  for r in json.loads(menu.read_text())['entries']:
   if not r.get('ok')or r['source']!='WAITPROT':continue
   p=C.read(ROOT/r['stem']);out.append((r['gadget'],k.patches(base,p),dict(family='WAITPROT',gadget=r['gadget'],source=r['stem'],old_loss=r['loss'],old_acceptance=r['acceptance'])))
 # Read measured timing endpoints and best integration outputs. Do not rerun
 # the standalone v35a timing/SX campaign; port its useful measured recipes.
 for f in (ROOT/'work/lanes/FRESH/r35').glob('*.allorders.json'):
  try:
   r=json.loads(f.read_text());stem=f.with_name(f.name.removesuffix('.allorders.json'))
   if r.get('loss',1)>=4.393527676043e-5 or r.get('acceptance',0)<.5005 or 'sx' in stem.name:continue
   p=C.read(stem);out.append(('FRESH_'+stem.name,k.patches(base,p),dict(family='FRESH_port',source=str(stem.relative_to(ROOT)),old_loss=r['loss'],old_acceptance=r['acceptance'])))
  except (OSError,KeyError,ValueError):continue
 st=ROOT/'work/lanes/FRESH/r35/feedback_i128_t30'
 if st.with_suffix('.qasm').exists():out.append(('FRESH_feedback',k.patches(base,C.read(st)),dict(family='FRESH_port',source=str(st.relative_to(ROOT)))))
 return out

def renumber_patch(p,c):
 p=copy.deepcopy(p);old={b for _,ls in p['remove']for line in ls for b in a.bits(line)}
 new=sorted({b for _,ls in p['add']for line in ls if '->'in line for b in a.bits(line)}-old)
 # A new bit is one not already in the donor base; known existing records
 # moved by the patch retain their identities.
 donor={b for u in C.read(ROOT/'work/lanes/MAIN/v35a')['u']for line in u.lines for b in a.bits(line)}
 new=[b for b in new if b not in donor];mapping={b:C.bit(c)+j for j,b in enumerate(new)}
 def f(s):return re.sub(r'c\[(\d+)\]',lambda m:f'c[{mapping.get(int(m[1]),int(m[1]))}]',s)
 p['add']={(t,tuple(f(s)for s in ls))for t,ls in p['add']};p['add_tail']={f(s)for s in p['add_tail']};return p

def seeds():
 c=C.read(OUT/'base');yield 'base',c,dict(family='base',budget_screen=True)
 good=[]
 for name,p,desc in external_patches():
  try:
   x=apply_patch(c,renumber_patch(p,c),True);good.append((name,p,desc));yield name,x,dict(desc,budget_screen=True)
  except Exception as e:print('PORT_SKIP',name,repr(e),flush=True)
 # Simultaneous accepted menu edits explore trades without requiring an
 # acceptance-infeasible intermediate to enter the population.
 priority=[z for z in good if 'late_reset'in z[0]or 'mz_parity'in z[0]or z[0]=='FRESH_feedback']
 for (n,p,ds),(nn,pp,dds)in itertools.combinations(priority,2):
  try:x=apply_patch(c,renumber_patch(p,c),True);x=apply_patch(x,renumber_patch(pp,x),True);yield n+'__'+nn,x,dict(family='menu_pair',sources=[ds,dds],budget_screen=True)
  except Exception:pass

if __name__=='__main__':
 import argparse,shutil
 p=argparse.ArgumentParser();p.add_argument('mode');p.add_argument('--workers',type=int,default=7);p.add_argument('--part',type=int,default=0);args=p.parse_args()
 if args.mode=='init':
  for ext in ('.qasm','.json'):shutil.copyfile(ROOT/'work/lanes/MAIN'/('v35b'+ext),str(OUT/'base')+ext)
  d.save(C.read(OUT/'base'),OUT/'base')
 elif args.mode=='seeds':a.batch((x for i,x in enumerate(seeds())if i%2==args.part),'seed'+str(args.part),args.workers)
