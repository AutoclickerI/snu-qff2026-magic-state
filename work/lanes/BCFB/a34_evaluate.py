import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,time,contextlib,hashlib,traceback,subprocess
H=Path(__file__).resolve().parent;D=H/'a34';ROOT=H.parents[2]
sys.path[:0]=[str(D/'sparse'),str(H),str(ROOT/'work'),str(ROOT/'work/lanes/EVAL')]
import xtim
xtim.cache_dir=str(D/'.xtim_cache');os.environ['XTIM_TWIRL_CACHE_DIR']=str(D/'.xtim_cache')
import sparse_walsh as sw
import schedule as S
from util import native_times
BASE_LOSS=4.6629334817191845e-5

def evaluate(stem,procs):
 text=stem.with_suffix('.qasm').read_text();h,raw,tail=S.qasm_ops(text);us=S.fold_units(raw)
 assert S.source_times(text,us)==native_times(text,us),'native schedule differs from barriers'
 with Path(str(stem)+'.allorders.log').open('w') as log,contextlib.redirect_stdout(log):r=sw.run(stem,72,True,procs)
 Path(str(stem)+'.allorders.json').write_text(json.dumps(r,indent=2))
 return {k:r[k] for k in ('loss','acceptance','seconds','conditional_loss_kernel_omission_bound')}

def verify(stem,procs):
 import speed_predict,fast_check
 xtim.cache_dir=str(D/'.xtim_cache')
 r=speed_predict.predict(str(stem));Path(str(stem)+'.speed.json').write_text(json.dumps(r,indent=2))
 print('SPEED',stem.name,r['classification'],r['median_seconds_per_1e6'],flush=True)
 if r['classification']!='FAST':return dict(speed=r,passed=False,reason='SLOW')
 with Path(str(stem)+'.judge.log').open('w') as log,contextlib.redirect_stdout(log):
  start=time.monotonic();rep=fast_check.check(stem.with_suffix('.qasm').read_text(),json.loads(stem.with_suffix('.json').read_text())['data_qubits'],shots=10**6,seed=0,procs=1)
  j=dict(passed=rep.passed,score=rep.score,sem=rep.sem,acceptance=rep.acceptance,n_2q=rep.n_2q,seconds=time.monotonic()-start,report=repr(rep));print(json.dumps(j))
 Path(str(stem)+'.judge.json').write_text(json.dumps(j,indent=2));print('JUDGE',stem.name,j,flush=True)
 if not rep.passed:return dict(speed=r,judge=j,passed=False,reason='JUDGE')
 cmd=[sys.executable,str(D/'inputs/mc3.py'),str(stem),'--procs',str(procs)]
 # Standard mc3 implementation, with cache redirected by environment/startup wrapper.
 with Path(str(stem)+'.mc3.log').open('w') as log:
  code="import os,sys,runpy,xtim;xtim.cache_dir=os.environ['XTIM_TWIRL_CACHE_DIR'];sys.argv="+repr(cmd[1:])+";runpy.run_path(sys.argv[0],run_name='__main__')"
  p=subprocess.run([sys.executable,'-B','-c',code],stdout=log,stderr=subprocess.STDOUT,cwd=D)
 if p.returncode:raise RuntimeError('MC3 failed: '+str(stem))
 import re
 txt=Path(str(stem)+'.mc3.log').read_text();seeds=[float(v) for v in re.findall(r' (?:0|1000|2000) ([\deE+.-]+) ±',txt)]
 assert len(seeds)==3,txt
 out=dict(speed=r,judge=j,mc3_seeds=seeds,mc3_mean=sum(seeds)/3,passed=True)
 Path(str(stem)+'.verification.json').write_text(json.dumps(out,indent=2));print('VERIFIED',stem.name,json.dumps(out),flush=True)
 return out

def report():
 rows=[]
 for f in (D/'candidates').glob('*.verification.json'):
  v=json.loads(f.read_text())
  if not v['passed']:continue
  stem=Path(str(f).replace('.verification.json',''));a=json.loads(Path(str(stem)+'.allorders.json').read_text());m=json.loads(stem.with_suffix('.json').read_text())
  if a['loss']<BASE_LOSS and a['acceptance']>=.5005:rows.append((a['loss'],a['acceptance'],stem,v,m))
 rows.sort();lines=['# BCFB — A decoder on v34m','', 'Status: search active. All work remains in BCFB. No submissions, credentials, commits, pushes, or subagents.','']
 if rows:
  lines+=['Verified improvements over v34m (baseline supplied: 4.66293e-5, acceptance 0.50120). Rank is all-orders loss.','', '| Candidate | All-orders loss | Acceptance | CX | XTIM s/1e6 | MC seeds 0 / 1000 / 2000 | MC mean |','|---|---:|---:|---:|---:|---|---:|']
  for loss,acc,stem,v,m in rows:
   rel=stem.relative_to(H);lines.append(f'| [{stem.name}]({rel}.qasm) | {loss:.13g} | {acc:.12f} | {m["CX"]} | {v["speed"]["median_seconds_per_1e6"]:.3f} | '+ ' / '.join(f'{x:.8g}' for x in v['mc3_seeds'])+f' | {v["mc3_mean"]:.8g} |')
 else:lines+=['No new improvement has completed all gates yet.','']
 lines+=['','Prior v30f A-side search: [REPORT_a30_completed.md](REPORT_a30_completed.md).','', 'Source v34m metadata contained inherited v31s counts and verdicts. Frozen input metadata records only measured v34m structure; new candidates carry independent receipts.']
 (H/'REPORT.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('list');p.add_argument('--procs',type=int,default=16);p.add_argument('--gates',action='store_true');a=p.parse_args()
 if a.list=='base':stems=[D/'inputs/v34m']
 else:
  payload=json.loads(Path(a.list).read_text());stems=[H/s for s in (payload['stems'] if isinstance(payload,dict) else payload)]
 results=[]
 for stem in stems:
  start=time.monotonic()
  try:
   done=Path(str(stem)+'.allorders.json')
   r={k:v for k,v in json.loads(done.read_text()).items() if k in ('loss','acceptance','seconds','conditional_loss_kernel_omission_bound')} if done.exists() else evaluate(stem,a.procs)
   r['stem']=str(stem.relative_to(H));print('ALLORDERS',json.dumps(r),flush=True)
   if a.gates and r['loss']<BASE_LOSS and r['acceptance']>=.5005:
    f=Path(str(stem)+'.verification.json');v=json.loads(f.read_text()) if f.exists() else verify(stem,a.procs);r['verification']=v;report()
  except Exception as e:r=dict(stem=str(stem.relative_to(H)),error=repr(e),trace=traceback.format_exc());print('ERROR',json.dumps(r),flush=True)
  results.append(r);(D/'runs'/('results_'+Path(a.list).stem+'.json')).write_text(json.dumps(results,indent=2))
 print('DONE',len(results),'seconds',time.monotonic()-start,flush=True)
