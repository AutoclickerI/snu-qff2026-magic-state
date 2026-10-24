"""Contract-relaxed SAT feedback with a fixed-initialization boundary cache."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent
from synth import Model,verify,trace
from build import build
from cache import setup,compile_cache,contract,evaluate
import argparse,json,time,random,copy,numpy as np,lzma
p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--seconds',type=float,default=900);p.add_argument('--seed',type=int,default=901);p.add_argument('--depth',type=int);p.add_argument('--cap',type=int,default=100);a=p.parse_args()
source=Path(a.stem);md=json.loads(source.with_suffix('.json').read_text());base=md['prep'];kind,value=base['kind'],base['value'];sourceopt=dict(md.get('options',{}));sourceopt['timing']='alap';tag=f'cache_{sourceopt.get("base","v23")}_{kind}_{value}_{a.seed}';rng=random.Random(a.seed)
text,md=build(base,sourceopt);init=md['init_times'];fixedopt=dict(sourceopt,fixed_init=init);control=H/'inputs'/f'{tag}_control';control.with_suffix('.qasm').write_text(text);control.with_suffix('.json').write_text(json.dumps(md,indent=2));path=H/'runs'/f'{tag}.cache.npz';compile_cache(control,path);z=np.load(path,allow_pickle=True);best=float(json.loads(path.with_suffix('.json').read_text())['full']['total']);current=best;bestprep=base
D=a.depth or len(base['ops']);base=dict(base,ops=(base['ops']+[[]]*D)[:D]);bestprep=base;m=Model(D,a.cap,a.seed,kind,value,extra_check=sourceopt.get('endpoint_parity',base.get('extra_check',False)),endpoint_rank=base.get('endpoint_rank'))
for q,nz in m.nz.items():m.add([nz if q in base['pivots'] else -nz])
for t in range(D+1):
 for q in m.cells:m.cut((t,(q,)))
for t,ss in enumerate(m.sel):
 for e in ss:m.cut((t+1,e))
m.warm(base);start=time.monotonic();it=count=hits=misses=0;seen=set();seenrows=[]
with lzma.open(H/'runs'/f'{tag}.jsonl.xz','wt') as witness:
 while time.monotonic()-start<a.seconds:
  width=rng.choice([2,3,4,5,6]);lo=rng.randrange(D+1-width);free=set(range(lo,lo+width)) if it%2 else set(rng.sample(range(D),width));ass=[]
  for t,ss in enumerate(m.sel):
   if t not in free:
    active={tuple(e) for e in base['ops'][t]};ass.extend(v if e in active else -v for e,v in ss.items())
  m.s.conf_budget(3000);ok=m.s.solve_limited(assumptions=ass);it+=1
  if ok is not True:continue
  d=m.candidate();v=verify(d);assert v['stim_target_pass'] and v['policy_pass'];mv={z for z in m.s.get_model() if z>0};m.add([-z if z in mv else z for ss in m.sel for z in ss.values()]);tr=trace(d)
  if tr in seen:continue
  seen.add(tr);count+=1;ntag=f'{tag}_{count:05d}'
  try:
   text,md=build(d,fixedopt);tmp=H/'inputs'/f'{tag}_current';tmp.with_suffix('.qasm').write_text(text);tmp.with_suffix('.json').write_text(json.dumps(md));ev,b,ks,prep,ext,hh=setup(tmp)
   compatible=hh==str(z['ext_hash'])
   if compatible:row=contract(ev,prep,z['response'],z['n3']);hits+=1
   else:row=evaluate(ev);misses+=1
   row.update(tag=ntag,cache_hit=compatible,verification=v)
   if row['total']<best-1e-12 and row['exp_minus_A1']>=.5002:
    full=evaluate(ev);assert abs(full['total']-row['total'])<1e-14
    import tprep
    ck=tprep.check(text,md['data_qubits'],shots=10**6,seed=0);row['judge']=dict(passed=bool(ck.passed),acceptance=float(ck.acceptance))
    if ck.passed:
     best=row['total'];bestprep=d;out=H/'finalists'/ntag;out.with_suffix('.qasm').write_text(text);out.with_suffix('.json').write_text(json.dumps(md,indent=2));out.with_suffix('.screen.json').write_text(json.dumps(row,indent=2));(H/'runs'/f'{tag}.best.json').write_text(json.dumps(dict(tag=ntag,prep=d,row=row),indent=2));print(json.dumps(dict(event='best',**row)),flush=True)
     with (H/'REPORT.md').open('a') as f:f.write(f'\nCache-feedback judge screen `{ntag}`: {best:.12g}; exp(-A1) {row["exp_minus_A1"]:.9g}. CLI, runtime and MC pending.\n')
   if row['total']<current or rng.random()<np.exp(min(0,(current-row['total'])/1e-7)):base=d;current=row['total']
   if count%30==0:base=bestprep;current=best
  except (ValueError,AssertionError) as e:row=dict(tag=ntag,error=str(e),status='INVALID')
  witness.write(json.dumps(dict(prep=d,row=row))+'\n');witness.flush();m.warm(base)
rec=dict(status='BUDGET_FINISHED',kind=kind,value=value,seed=a.seed,iterations=it,witnesses=count,cache_hits=hits,cache_misses=misses,best=best,seconds=time.monotonic()-start)
(H/'runs'/f'{tag}.receipt.json').write_text(json.dumps(rec,indent=2));print(json.dumps(rec),flush=True)
