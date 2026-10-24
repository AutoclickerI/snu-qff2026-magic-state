import os,sys,json,argparse,time,importlib.util,runpy,collections,math
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;ROOT=H.parents[2];sys.path[:0]=[str(ROOT/'work/lanes/EVAL'),str(ROOT/'work')]
import xtim
xtim.cache_dir=str(H/'.xtim_cache');os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
p=argparse.ArgumentParser();p.add_argument('mode',choices=['exact','check','speed','split','screen']);p.add_argument('stem');p.add_argument('--procs',type=int,default=1);a=p.parse_args();stem=Path(a.stem).resolve();start=time.monotonic()
if a.mode=='exact':
 sys.argv=[str(ROOT/'work/lanes/EVAL/exact2.py'),str(stem.with_suffix('.qasm')),'--procs',str(a.procs),'--third','--json',str(stem.with_suffix('.sens.json'))];runpy.run_path(sys.argv[0],run_name='__main__')
elif a.mode=='check':
 import fast_check
 r=fast_check.check(stem.with_suffix('.qasm').read_text(),json.loads(stem.with_suffix('.json').read_text())['data_qubits'],shots=10**6,seed=0,procs=a.procs);out=dict(passed=r.passed,score=r.score,sem=r.sem,acceptance=r.acceptance,n_2q=r.n_2q,details=str(r),seconds=time.monotonic()-start);stem.with_suffix('.check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
elif a.mode=='speed':
 spec=importlib.util.spec_from_file_location('unchanged_speed_predict',ROOT/'work/lanes/XTIM/speed_predict.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.xtim.cache_dir=str(H/'.xtim_cache');out=mod.predict(str(stem));stem.with_suffix('.speed.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
elif a.mode=='screen':
 spec=importlib.util.spec_from_file_location('sepbc_screen',ROOT/'work/lanes/SEPBC/common.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.H=H;mod.xtim.cache_dir=str(H/'.xtim_cache');print(json.dumps(mod.score(stem)),flush=True)
else:
 import exact2
 plan=json.loads(stem.with_suffix('.plan.json').read_text());text=stem.with_suffix('.qasm').read_text();meta=json.loads(stem.with_suffix('.json').read_text());ev=exact2.Eval(text,meta['data_qubits']);bytime={(o['t'],tuple(sorted(__import__('re').findall(r'q\[(\d+)\]',o['lines'][0])))):o.get('region',o.get('tag','unknown'))for o in plan['ops']};regions=[]
 for ch in range(len(ev.m.chans)):
  lab=ev.chan_label(ch);t=int(lab['steps'].split('..')[0]);qs=tuple(sorted(map(str,lab['qubits'])))
  if lab['kind']=='idle':reg='round'if t>=meta['R']else'exposure'
  else:
   reg=bytime.get((t,qs))
   if reg is None:
    opts=[o.get('region',o.get('tag','unknown'))for o in plan['ops']if o['t']==t and set(map(int,qs))<=set(map(int,__import__('re').findall(r'q\[(\d+)\]',' '.join(o['lines']))))];assert len(opts)==1,(ch,lab,opts);reg=opts[0]
   if reg.startswith('encoder_')or reg=='prep_init':reg='ancilla_prep'
  regions.append(reg)
 from model import Basis
 bas=Basis();indices=[];constraints=[]
 for i,(xx,zz,c)in enumerate(ev.e.projs):
  combo=bas.express(xx|(zz<<ev.e.r))
  if combo is None:bas.add(xx|(zz<<ev.e.r));indices.append(i)
  else:
   rel=1<<i
   for j,bi in enumerate(indices):
    if combo>>j&1:rel^=1<<bi
   constraints.append(rel)
 original=ev.e.ntable
 ev.e.ntable=lambda s,d:(0.,None)if any((int(d)&h).bit_count()%2 for h in constraints)else original(s,d)
 fr=[regions[int(ch)]for ch in ev.fch];r=exact2.run(ev,procs=a.procs,keep_thr=0,third=False);pairs=collections.Counter()
 for value,i,j,*rest in r['big']:pairs[' x '.join(sorted([fr[i],fr[j]]))]+=value
 out=dict(second=r['loss'],first=r['loss1'],pair_classes=dict(pairs.most_common()),round_x_round=pairs['round x round'],pre_round_only=sum(v for k,v in pairs.items()if'round'not in k),teleports_involving=sum(v for k,v in pairs.items()if'teleports'in k),exposure_involving=sum(v for k,v in pairs.items()if'exposure'in k),note='second-order disjoint pair table; aggregate teleports/exposure marginals overlap and must not be added; full third order is in unchanged exact2 receipt')
 stem.with_suffix('.split.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
(H/(stem.name+'.'+a.mode+'.exit.json')).write_text(json.dumps(dict(mode=a.mode,seconds=time.monotonic()-start,exit_code=0),indent=2))
