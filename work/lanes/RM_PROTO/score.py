import os,sys
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
sys.dont_write_bytecode=True
from pathlib import Path
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
sys.path.insert(0,str(ROOT/'work/lanes/EVAL'))
import json,time,argparse,warnings,multiprocessing as mp
import numpy as np
import tprep.qasm as tq
import importlib
tp=importlib.import_module("tprep.parse")
tq.adjacent=tp.adjacent=lambda a,b:True
import exact2,xtim
xtim.cache_dir=str(BASE/".xtim_cache")
os.environ["XTIM_TWIRL_CACHE_DIR"]=str(BASE/".xtim_cache"/"twirl")
import fast_engine
from tprep.noise import apply_noise,STANDARD,schedule
from tprep.parse import declarations,count_measurements
from tprep.exact import verify
import importlib
tc=importlib.import_module('tprep.check')

def worker(args):
 text,data,shots,seed=args
 frame,post=declarations(text)
 plan=tc.Plan(data,frame,post,count_measurements(text))
 with warnings.catch_warnings():
  warnings.simplefilter('ignore')
  return tc._sample(xtim.Circuit(apply_noise(text,1e-3,STANDARD)+'\n'+plan.tail),shots,seed,plan)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--procs',type=int,default=1);ap.add_argument('--shots',type=int,default=10000000);ap.add_argument('--mode',default='both');ap.add_argument('--seed',type=int,default=0);args=ap.parse_args()
 stem=Path(args.stem);qasm=stem.with_suffix('.qasm').read_text();data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
 text,labels,err=tq.convert(qasm);assert not err,err
 out={'stem':str(stem),'p':1e-3};start=time.time()
 frame,post=declarations(text);out['noiseless']=verify(text,data,frame=frame,postselect=post)
 print('noiseless',out['noiseless'],flush=True)
 if args.mode in ['both','exact']:
  ev=exact2.Eval(qasm,data);print('model',len(ev.m.chans),'channels',len(ev.m.faults),'faults',len(ev.gkeys),'groups','rank',ev.e.rank_rot,flush=True)
  r=exact2.run(ev,procs=args.procs)
  out['exact2']={k:float(v) for k,v in r.items() if k not in ['sens','big']}
  out['channels']=[dict(ev.chan_label(i),prob=ch['prob'],loss2_attribution=float(r['sens'][i]/2)) for i,ch in enumerate(ev.m.chans)]
  out['bad_singles']=[dict(label=ev.fault_label(i),loss=float(ev.fp[i]*n)) for i,n in enumerate(ev.n_single) if ev.fp[i]*n>1e-12]
  print('exact2',out['exact2'],'bad_singles',out['bad_singles'],flush=True)
  stem.with_name(stem.name+'_score').with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
 if args.mode in ['both','mc']:
  for seed in [args.seed,args.seed+1000,args.seed+2000]:
   chunks=[(text,data,min(1000000,args.shots-i),seed+i//1000000) for i in range(0,args.shots,1000000)]
   with mp.get_context('fork').Pool(args.procs) as pool:rs=pool.map(worker,chunks)
   print('raw',rs[:1],flush=True)
   ac=sum(r['acceptance']*ch[2] for r,ch in zip(rs,chunks));loss=sum(r['score']*r['acceptance']*ch[2] for r,ch in zip(rs,chunks))/ac
   sem=sum((r['sem']*r['acceptance']*ch[2])**2 for r,ch in zip(rs,chunks))**.5/ac
   result={'seed':seed,'shots':args.shots,'loss':loss,'sem':sem,'acceptance':ac/args.shots};out.setdefault('mc',[]).append(result);print('mc',result,flush=True)
 out['seconds']=time.time()-start
 stem.with_name(stem.name+'_'+args.mode+'_score').with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
if __name__=='__main__':main()
