"""All-orders detector/physical-element pricing and budgeted recombination."""
import os,sys,json,re,math,time,hashlib,copy,contextlib,io,argparse,lzma
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H));import directed as d
from concurrent.futures import ProcessPoolExecutor,as_completed
C=d.C;OUT=H/'knapsack';FLOOR=.5005;BASE_LOSS=5.1443198493581796e-5;BASE_ACC=.5009617725494582
ECHO=[(10,11,'X',19,29,264),(7,13,'X',20,23,265),(0,6,'Z',34,41,267),(20,19,'X',18,33,268),(20,26,'Z',20,31,269),(10,16,'X',21,27,270),(4,5,'X',18,33,271),(15,21,'X',20,28,272)]
def bits(s):return list(map(int,re.findall(r'c\[(\d+)\]',s)))
def remove_units(c,inds):
 c['u']=[u for i,u in enumerate(c['u']) if i not in inds];c['t']=[t for i,t in enumerate(c['t']) if i not in inds];return c

def strip_bits(c,bs):
 bs=set(bs);tail=[]
 for s in c['tail']:
  if s.startswith('// DETECTOR'):
   v=set(bits(s))-bs
   if not v:continue
   s='// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(v))
  tail.append(s)
 c['tail']=tail;return c

def drop_echo(c,e):
 c=C.clone(c);q,h,axis,a,b,bit=e;inds=[]
 for i,(u,t) in enumerate(zip(c['u'],c['t'])):
  if t in (a,a+1,b-1,b) and h in u.qs and ((len(u.qs)==1)or(q in u.qs)):inds.append(i)
 assert len(inds)==4,(e,[(c['t'][i],c['u'][i].lines) for i in inds])
 remove_units(c,set(inds));strip_bits(c,[bit]);return d.normalize(c)

def pricing(c):
 yield 'base',c,dict(family='base')
 for j,s in enumerate(c['tail']):
  if not s.startswith('// DETECTOR'):continue
  x=C.clone(c);x['tail'].pop(j)
  yield f'det_{j:02}',x,dict(family='detector_only',row=j,detector=s)
 for e in ECHO:
  yield f'echo_{e[-1]}_off',drop_echo(c,e),dict(family='echo_remove',echo=e)
 # All singleton known-zero measurements: both physical omission and reset
 # replacement. Other references to a known-zero outcome are removed too.
 singles={bits(s)[0] for s in c['tail'] if s.startswith('// DETECTOR') and len(bits(s))==1}
 echo_bits={e[-1] for e in ECHO}
 for i,(u,t) in enumerate(zip(c['u'],c['t'])):
  bs=bits(' '.join(u.lines))
  if u.name not in ('MX','MEASURE') or len(bs)!=1 or bs[0] not in singles or bs[0] in echo_bits or t>=c['meta']['R']:continue
  b=bs[0];q=u.qs[0]
  for form in ('omit','reset'):
   x=C.clone(c);strip_bits(x,[b])
   if form=='omit':remove_units(x,{i})
   else:x['u'][i]=C.Unit([f'reset q[{q}];']+([f'h q[{q}];']if u.name=='MX'else []))
   yield f'meas_{b}_{form}',x,dict(family='known_measurement',bit=b,q=q,time=t,form=form)
 # Watch is parity c266+c43, not a singleton.
 x=C.clone(c);inds={i for i,u in enumerate(x['u']) if 266 in bits(' '.join(u.lines))};remove_units(x,inds)
 x['tail']=[s for s in x['tail'] if 266 not in bits(s)]
 yield 'watch266_off',x,dict(family='watch_remove',bit=266)
 # Full blue-X/Z window is identified by the two helper lifetimes.
 for hs,name,bs in [({1},'blue_Z',[64]),({2},'blue_X',[67]),({1,2},'blue_XZ',[64,67])]:
  x=C.clone(c);inds={i for i,(u,t) in enumerate(zip(x['u'],x['t']))if 28<=t<=36 and set(u.qs)&hs}
  # q1/q2 blue windows interconnect. Individual branches are priced even if
  # their remaining instrument is rejected by noiseless correctness.
  remove_units(x,inds);strip_bits(x,bs)
  yield name+'_off',x,dict(family='blue_physical',helpers=sorted(hs),removed=len(inds))
 # Full A/C detector subsets, with operations unchanged.
 for name,rows in [('A_syndromes',[14,15,16]),('B_syndromes',[17,18,19]),('C_syndromes',[20,21,22,23,53,54,55])]:
  x=C.clone(c);x['tail']=[s for i,s in enumerate(x['tail']) if i not in rows]
  yield name+'_off',x,dict(family='detector_subset',rows=rows)

def score(job):
 p,desc=job;p=Path(p);start=time.monotonic();r=dict(stem=str(p.relative_to(H)),description=desc)
 try:
  # All proposals, including c1-harmful removals, receive all-orders prices.
  # No acceptance proxy or truncated-order rank prefilter is applied.
  ev=C.exact2.Eval(p.with_suffix('.qasm').read_text(),C.D)
  r.update(c1=float(ev.fp@ev.n_single),exp_minus_A1=math.exp(-float(ev.fp@(1-ev.a_single))))
  if desc.get('budget_screen'):
   import sparse_budget
   ao=sparse_budget.run(p,FLOOR)
   r.update(ok=True,acceptance=ao['acceptance'],eligible=ao['eligible'],acceptance_screen_exact=True,conditioned_width=ao['conditioned_width'])
   if ao['eligible']:r.update(loss=ao['loss'],omission_bound=ao['conditional_loss_kernel_omission_bound'],delta_loss=ao['loss']-BASE_LOSS,acceptance_recovered=ao['acceptance']-BASE_ACC)
   r['seconds']=time.monotonic()-start;p.with_suffix('.score.json').write_text(json.dumps(r,indent=2));return r
  od=p.parent/'sparse_results'/p.name;od.mkdir(parents=True,exist_ok=True);d.sw.__file__=str(od/'sparse_walsh.py')
  with contextlib.redirect_stdout(io.StringIO()):ao=d.sw.run(p,72,True,procs=1)
  r.update(ok=True,loss=ao['loss'],acceptance=ao['acceptance'],eligible=ao['acceptance']>=FLOOR,omission_bound=ao['conditional_loss_kernel_omission_bound'],conditioned_width=ao['conditioned_width'])
  r.update(delta_loss=r['loss']-BASE_LOSS,acceptance_recovered=r['acceptance']-BASE_ACC)
  (od/(p.name+'_canonical_sparse_result.json')).unlink();od.rmdir()
 except Exception as e:r.update(ok=False,error=repr(e))
 r['seconds']=time.monotonic()-start;p.with_suffix('.score.json').write_text(json.dumps(r,indent=2));return r

def batch(items,label,workers=14):
 od=OUT/label;od.mkdir(exist_ok=True);jobs=[];bad=[];seen=set()
 for name,c,desc in items:
  try:
   c=d.normalize(c);fp=d.digest(c)
   if fp in seen:continue
   seen.add(fp);p=od/name;d.save(c,p);jobs.append((str(p),desc))
  except Exception as e:bad.append(dict(stem=name,description=desc,error=repr(e)))
 print('BATCH',label,len(jobs),'build_rejected',len(bad),flush=True)
 rows=[];pending=[]
 for job in jobs:
  receipt=Path(job[0]).with_suffix('.score.json')
  if receipt.exists():rows.append(json.loads(receipt.read_text()))
  else:pending.append(job)
 print('RESUME',len(rows),'pending',len(pending),flush=True)
 with ProcessPoolExecutor(workers) as pool,(od/'trace.jsonl').open('w')as f:
  fs={pool.submit(score,j):j for j in pending}
  for fut in as_completed(fs):
   r=fut.result();rows.append(r);f.write(json.dumps(r)+'\n');f.flush()
   print(r['stem'],r.get('loss'),r.get('acceptance'),r.get('c1'),r.get('error',''),flush=True)
 rows.sort(key=lambda r:r.get('loss',1));(od/'results.json').write_text(json.dumps(dict(rows=rows,build_rejected=bad),indent=2));return rows

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode');p.add_argument('--workers',type=int,default=14);a=p.parse_args()
 if a.mode=='price':batch(pricing(d.normalize(C.read(OUT/'base'))),'prices',a.workers)
