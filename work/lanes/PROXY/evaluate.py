"""Full non-Clifford judge evaluation, artifacts and caches confined to PROXY."""
import os,sys,json,math,time,subprocess,runpy,multiprocessing as mp
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
os.chdir(HERE);sys.dont_write_bytecode=True
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',XTIM_TWIRL_CACHE_DIR=str(HERE/'.twirl_cache'))
sys.path[:0]=[str(ROOT/'work'),str(ROOT/'work/lanes/EVAL')]
import xtim
xtim.cache_dir=str(HERE/'.xtim_cache')

def screen_one(name):
 from exact2 import Eval,run
 start=time.time();meta=json.loads((HERE/f'{name}.json').read_text());text=(HERE/f'{name}.qasm').read_text()
 ev=Eval(text,meta['data_qubits'])
 keys=list({(sa^sb,da^db) for i,(sa,da) in enumerate(ev.gkeys) for sb,db in ev.gkeys[i:]})
 cache={}
 for lo in range(0,len(keys),128):
  part=keys[lo:lo+128];aa,nn=ev.e.batch_n([k[0] for k in part],[k[1] for k in part])
  for key,a,n in zip(part,aa,nn):cache[key]=(float(a),n if a>1e-18 else None)
 ev.e.ntable=lambda s,d:cache[s,d]
 r=run(ev,procs=1,keep_thr=math.inf,log=lambda *a:None)
 out=dict(name=name,**{k:float(r[k]) for k in ('loss','loss1','loss2','A1')},exp_A1=math.exp(-r['A1']),seconds=time.time()-start)
 (HERE/f'{name}.screen.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True);return out

def select():
 rows=[]
 for shard in (0,1):rows+=json.loads((HERE/f'search_results_{shard}.json').read_text())
 rows=[r for r in rows if r.get('check',{}).get('passed')]
 rows.sort(key=lambda r:r['proxy'])
 chosen=rows[:24];seen={r['index'] for r in chosen}
 # Include the best member of every surviving geometry and every leaf topology.
 for keyfunc in (lambda r:json.dumps(r['layout']['pos']),lambda r:json.dumps([r['layout']['pos'],r['leaves']])):
  groups={}
  for r in rows:groups.setdefault(keyfunc(r),r)
  for r in list(groups.values()):
   if r['index'] not in seen and r['proxy']<rows[0]['proxy']*1.5:chosen.append(r);seen.add(r['index'])
 names=[f"cycle_{r['index']:04d}" for r in chosen]
 names+=['reference_r86']
 for f in ('qasm','json'):(HERE/f'reference_r86.{f}').write_text((ROOT/f'work/submissions/v12_L5lns12_r86.{f}').read_text())
 (HERE/'shortlist.json').write_text(json.dumps(names,indent=2))
 summary=dict(results=len(rows),best=[dict(index=r['index'],proxy=r['proxy'],proxy_second=r['proxy_second'],depth=r['depth'],moves=r['layout']['moves']) for r in rows[:15]],shortlist=len(names),geometry_count=len({tuple(r['layout']['pos']) for r in rows}))
 (HERE/'search_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)

def third(names,procs):
 for name in names:
  cmd=[str(ROOT/'.venv/bin/python'),str(HERE/'evaluate.py'),'cli',name,str(procs)]
  log=HERE/f'{name}.third.log'
  with log.open('w') as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
  import re
  txt=log.read_text()
  def val(p):return float(re.search(p,txt).group(1))
  out=dict(name=name,second=val(r'1-F \(2nd order\) = ([\deE+.-]+)'),third=val(r'1-F \(to 3rd order\) = ([\deE+.-]+)'),first=val(r'c1 p = ([\deE+.-]+)'),exp_A1=val(r'exp\(-A1\) = ([\deE+.-]+)'))
  (HERE/f'{name}.third.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)

def monte(names,procs):
 import fast_check,tprep
 for name in names:
  text=(HERE/f'{name}.qasm').read_text();meta=json.loads((HERE/f'{name}.json').read_text());rows=[]
  check=tprep.check(text,meta['data_qubits'],shots=10**6,seed=0)
  assert check.passed,str(check)
  for seed in (0,1000,2000):
   start=time.time();r=fast_check.check(text,meta['data_qubits'],shots=10**8,seed=seed,procs=procs)
   row=dict(seed=seed,shots=10**8,score=r.score,sem=r.sem,acceptance=r.acceptance,passed=r.passed,seconds=time.time()-start);assert r.passed,str(r);rows.append(row);print(name,json.dumps(row),flush=True)
  out=dict(name=name,check_1e6=str(check),rows=rows,mean=sum(r['score'] for r in rows)/3,sem_mean=math.sqrt(sum(r['sem']**2 for r in rows))/3)
  (HERE/f'{name}.mc.json').write_text(json.dumps(out,indent=2));print('MC_RESULT',json.dumps(out),flush=True)

if __name__=='__main__':
 mode=sys.argv[1]
 if mode=='select':select()
 elif mode=='screen':
  shard,nshards,workers=map(int,sys.argv[2:5]);names=json.loads((HERE/'shortlist.json').read_text())[shard::nshards]
  with mp.get_context('fork').Pool(workers) as p:rows=list(p.imap_unordered(screen_one,names))
  (HERE/f'screen_results_{shard}.json').write_text(json.dumps(rows,indent=2))
 elif mode=='cli':
  name,procs=sys.argv[2:4];sys.argv=[str(ROOT/'work/lanes/EVAL/exact2.py'),str(HERE/f'{name}.qasm'),'--third','--procs',procs,'--top','6'];runpy.run_path(sys.argv[0],run_name='__main__')
 elif mode=='third':third(sys.argv[3:],int(sys.argv[2]))
 elif mode=='mc':monte(sys.argv[3:],int(sys.argv[2]))
 else:raise ValueError(mode)
