"""Price one clean prep in v20 with exact2 arithmetic and judge gates."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,time,math,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
os.environ['XTIM_TWIRL_CACHE_DIR']=str(HERE/'.xtim_cache')
sys.path[:0]=[str(HERE),str(ROOT/'work/lanes/TREP2'),str(ROOT/'work/lanes/EVAL')]
from transplant import build
from synth import verify
import exact2,fast_third,tprep
from moments import evaluate as moment_evaluate

def price(prep,tag,mode='project',mx=(),reference=False,procs=1,reuse=()):
 t0=time.monotonic();out=HERE/'full'/tag;d=json.loads(Path(prep).read_text());v=verify(d);assert v['stim_target_pass'] and v['clean_pass'],v
 row=dict(tag=tag,prep=str(prep),verification=v,mode=mode,mx=list(mx),reuse=list(reuse));row.update(build(d,out,mode,mx,reuse));row['build_seconds']=time.monotonic()-t0
 text=out.with_suffix('.qasm').read_text();md=json.loads(out.with_suffix('.json').read_text());ev=exact2.Eval(text,md['data_qubits'])
 if abs(float(ev.fp@ev.n_single))>=1e-12:
  row['c1']=float(ev.fp@ev.n_single);row['exact_status']='INVALID_C1'
 elif not reference:
  row.update(moment_evaluate(ev));row['evaluator']='exact2 Fourier moments, validated against unaggregated sums'
 else:
  r=exact2.run(ev,procs=procs,third=True,keep_thr=1)
  row.update(c1=r['loss1'],second=r['loss2'],exp_minus_A1=math.exp(-r['A1']))
  if abs(row['c1'])<1e-12:
   th=exact2.third_order(ev,procs)[0]+r['t3bc'];row.update(third=th,total=r['loss']+th)
 row['exact_seconds']=time.monotonic()-t0;out.with_suffix('.price.json').write_text(json.dumps(row,indent=2))
 ck=tprep.check(text,md['data_qubits'],shots=10**6,seed=0);row['check']=dict(passed=bool(ck.passed),format_ok=bool(ck.format_ok),class_ok=bool(ck.class_ok),correct_ok=bool(ck.correct_ok),acceptance_ok=bool(ck.acceptance_ok),acceptance=float(ck.acceptance),score=float(ck.score),format_errors=ck.format_errors,correctness_errors=ck.correctness_errors)
 row['wall_seconds']=time.monotonic()-t0;row['reference']=reference;out.with_suffix('.price.json').write_text(json.dumps(row,indent=2));print(json.dumps(row),flush=True);return row

def main():
 p=argparse.ArgumentParser();p.add_argument('prep');p.add_argument('tag');p.add_argument('--mode',default='project');p.add_argument('--mx',default='');p.add_argument('--reuse',default='');p.add_argument('--reference',action='store_true');p.add_argument('--procs',type=int,default=1);a=p.parse_args()
 lock=HERE/'full'/(a.tag+'.lock')
 try:
  with lock.open('x') as f:f.write(str(os.getpid()))
 except FileExistsError:
  print(json.dumps(dict(tag=a.tag,status='IN_FLIGHT')),flush=True);return
 try:price(a.prep,a.tag,a.mode,[int(q) for q in a.mx.split(',') if q],a.reference,a.procs,[int(q) for q in a.reuse.split(',') if q])
 finally:lock.unlink()
if __name__=='__main__':main()
