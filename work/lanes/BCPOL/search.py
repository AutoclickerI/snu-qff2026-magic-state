"""Finite contract portfolio, exact full-circuit feedback, compressed witnesses."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,random,time,math,lzma,traceback
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
from synth import Model,verify,trace,B,C,faults
from build import build
from moments_batch import evaluate,exact2
BASE=6.92210398228e-5;BASEA=.540859577712

def score(d,opt):
 text,md=build(d,opt);ev=exact2.Eval(text,md['data_qubits']);c1=float(ev.fp@ev.n_single)
 if abs(c1)>=1e-12:return dict(status='INVALID_C1',c1=c1),text,md
 row=evaluate(ev);row.update(status='SCREENED',delta_loss=row['total']-BASE,delta_A1=-math.log(row['exp_minus_A1']/BASEA),R=md['R'],CX=md['CX'])
 return row,text,md

def main():
 p=argparse.ArgumentParser();p.add_argument('kind',choices=['policy','endpoint','c6']);p.add_argument('value',type=int);p.add_argument('--seed',type=int,default=701);p.add_argument('--seconds',type=float,default=900);p.add_argument('--cap',type=int,default=90);p.add_argument('--depth',type=int);p.add_argument('--helper-x',action='store_true');a=p.parse_args()
 rng=random.Random(a.seed);tag=f'{a.kind}_{a.value}_s{a.seed}';start=time.monotonic();base=json.loads((H/'inputs/base.prep.json').read_text());base.update(kind=a.kind,value=a.value,helper_x=a.helper_x)
 if a.kind=='endpoint':base['ops'].append([list(e) for e in zip(B,C)])
 D=a.depth or len(base['ops']);base['ops']=(base['ops']+[[]]*D)[:D]
 m=Model(D,a.cap,a.seed,a.kind,a.value,helper_x=a.helper_x)
 for t in range(D+1):
  for q in m.cells:m.cut((t,(q,)))
 for t,ss in enumerate(m.sel):
  for e in ss:m.cut((t+1,e))
 m.warm(base);seen=set();count=priced=clean=0;best=1.;current=1.;bestprep=base;it=0;solver_seconds=0.;rows=[]
 with lzma.open(H/'runs'/f'{tag}.jsonl.xz','wt') as witness:
  while time.monotonic()-start<a.seconds:
   widths=[2,3,4,5,6,7,8] if count else [4,6,8,10,D]
   width=min(D,rng.choice(widths));lo=rng.randrange(D+1-width);free=set(range(lo,lo+width)) if it%2 else set(rng.sample(range(D),width));ass=[]
   for t,ss in enumerate(m.sel):
    if t not in free:
     active={tuple(e) for e in base['ops'][t]};ass.extend(z if e in active else -z for e,z in ss.items())
   m.s.conf_budget(2000 if width<D else 10000);tt=time.monotonic();ok=m.s.solve_limited(assumptions=ass);solver_seconds+=time.monotonic()-tt;it+=1
   if ok is not True:continue
   d=m.candidate();v=verify(d);assert v['stim_target_pass'] and v['policy_pass'],v
   mv={z for z in m.s.get_model() if z>0};m.add([-z if z in mv else z for ss in m.sel for z in ss.values()]);tr=trace(d)
   if tr in seen:continue
   seen.add(tr);count+=1
   if a.kind=='policy' and v['clean_pass']:
    clean+=1
    # A structurally nearby clean intermediate can lead to a relaxed witness;
    # no clean-contract pricing duplicates BCFB's search.
    if count%3==0:base=d
    continue
   ntag=f'{tag}_{count:05d}';opt=dict(timing='alap');tt=time.monotonic()
   try:
    row,text,md=score(d,opt);priced+=1
    val=row.get('total',1);eligible=row.get('exp_minus_A1',0)>=.5002
    if eligible and val<best:
     import tprep
     t0=time.monotonic();ck=tprep.check(text,md['data_qubits'],shots=10**5,seed=0)
     row['judge']=dict(passed=bool(ck.passed),acceptance=float(ck.acceptance),seconds=time.monotonic()-t0,format_ok=bool(ck.format_ok),class_ok=bool(ck.class_ok),correct_ok=bool(ck.correct_ok))
     # Small-shot acceptance fluctuates; keep exact-eligible correct circuits
     # for mandatory final seed-0 gate, never waive that gate.
     if ck.format_ok and ck.class_ok and ck.correct_ok:
      best=val;bestprep=d
      out=H/'finalists'/ntag;out.with_suffix('.qasm').write_text(text);out.with_suffix('.json').write_text(json.dumps(md,indent=2));out.with_suffix('.screen.json').write_text(json.dumps(row,indent=2))
      (H/'runs'/f'{tag}.best.json').write_text(json.dumps(dict(tag=ntag,prep=d,row=row),indent=2))
      if val<BASE:
       with (H/'REPORT.md').open('a') as f:f.write(f'\nVerified correctness screen: `{ntag}`, loss {val:.12g}, delta {val-BASE:+.9g}, exp(-A1) {row["exp_minus_A1"]:.9g}, delta A1 {row["delta_A1"]:+.9g}. Final exact CLI / runtime / MC pending.\n')
    if val<current or rng.random()<math.exp(min(0,(current-val)/3e-7)):
     base=d;current=val
    if count%30==0 and best<1:base=bestprep;current=best
   except (ValueError,AssertionError) as e:row=dict(status='INVALID',error=str(e))
   row.update(tag=ntag,verification=v,seconds=time.monotonic()-tt);rows.append(row);witness.write(json.dumps(dict(row=row,prep=d,opt=opt))+'\n');witness.flush()
   print(json.dumps(row),flush=True);m.warm(base)
 rec=dict(vars(a),status='BUDGET_FINISHED',iterations=it,witnesses=count,clean_skipped=clean,priced=priced,best=best,solver_seconds=solver_seconds,seconds=time.monotonic()-start)
 (H/'runs'/f'{tag}.receipt.json').write_text(json.dumps(rec,indent=2));print(json.dumps(rec),flush=True)

if __name__=='__main__':main()
