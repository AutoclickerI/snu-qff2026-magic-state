import os,sys,json,re,time
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
from pathlib import Path
ROOT=Path(__file__).parents[3]
sys.path.insert(0,str(ROOT/'work'))
sys.path.insert(0,str(ROOT/'work'/'lanes'/'EVAL'))
import tprep, exact2
from fast_check import check as mc_check

def score(stem,procs=2,mc=False):
 p=Path(stem); text=p.with_suffix('.qasm').read_text(); meta=json.loads(p.with_suffix('.json').read_text());
 rep=tprep.check(text,meta['data_qubits'],shots=10**6,seed=0)
 out={'file':str(p.with_suffix('.qasm')),'cx':rep.n_2q,'R':meta.get('R'),'pre_end':meta.get('pre_end'),'check_score':rep.score,'check_sem':rep.sem,'acceptance':rep.acceptance,'passed':rep.passed,'format_errors':rep.format_errors,'class_error':rep.class_error,'correctness_errors':rep.correctness_errors}
 if rep.correct_ok:
  ev=exact2.Eval(text,meta['data_qubits']); r=exact2.run(ev,procs,third=True); t3=exact2.third_order(ev,procs)[0]+r['t3bc'] if abs(r['loss1'])<1e-12 else float('nan')
  out.update({'c1':r['loss1'],'second':r['loss'],'third':t3,'exp_A1':exact2.np.exp(-r['A1'])})
  if mc:
   out['mc']=[]
   for seed in (0,1000,2000):
    m=mc_check(text,meta['data_qubits'],shots=10**8,seed=seed,procs=procs)
    out['mc'].append({'seed':seed,'score':m.score,'sem':m.sem,'acceptance':m.acceptance,'passed':m.passed})
  p.with_suffix('.metrics.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps(out,indent=2),flush=True)
 return out

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('stems',nargs='+');ap.add_argument('--procs',type=int,default=2);ap.add_argument('--mc',action='store_true'); a=ap.parse_args()
 for s in a.stems: score(s,a.procs,a.mc)
