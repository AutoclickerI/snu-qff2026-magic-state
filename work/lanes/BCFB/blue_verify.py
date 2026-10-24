import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,subprocess,time,re,socket
from pathlib import Path
from blue_report import report
H=Path(__file__).resolve().parent;ROOT=H.parents[2];D=H/'blue';os.environ['XTIM_TWIRL_CACHE_DIR']=str(D/'.xtim_cache')
p=argparse.ArgumentParser();p.add_argument('stems',nargs='+');p.add_argument('--exact',action='store_true');p.add_argument('--procs',type=int,default=2);a=p.parse_args()
for name in a.stems:
 stem=D/'finalists'/name;out=stem.with_suffix('.verify.json');r=json.loads(out.read_text()) if out.exists() else dict(tag=name)
 print(json.dumps(dict(event='capacity',host=socket.gethostname(),cores=os.cpu_count(),load=os.getloadavg(),procs=a.procs)),flush=True)
 if not a.exact:
  assert socket.gethostname()=='zebra'
  start=time.monotonic();cmd=[sys.executable,str(ROOT/'work/fast_check.py'),str(stem.with_suffix('.qasm')),str(stem.with_suffix('.json')),'1000000','1']
  with stem.with_suffix('.speed.log').open('w') as log:
   pr=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,cwd=D)
   try:rc=pr.wait(timeout=30)
   except subprocess.TimeoutExpired:pr.kill();rc=pr.wait()
  r.update(speed_seconds=time.monotonic()-start,speed_host=socket.gethostname(),speed_returncode=rc)
  txt=stem.with_suffix('.speed.log').read_text();m=re.search(r'1-F=(\S+) sem=(\S+) acc=(\S+) n_2q=(\S+) passed=(\S+)',txt)
  r.update(judge_pass=bool(m and m[5]=='True'),acceptance=float(m[3]) if m else None,score=float(m[1].removeprefix('np.float64(').removesuffix(')')) if m else None)
  r['speed_pass']=rc==0 and r['speed_seconds']<=20
  r['gates_pass']=r['speed_pass'] and r['judge_pass'] and r['acceptance']>=.5
 else:
  with stem.with_suffix('.exact.log').open('w') as log:rc=subprocess.run([sys.executable,str(ROOT/'work/lanes/EVAL/exact2.py'),str(stem.with_suffix('.qasm')),'--third','--procs',str(a.procs),'--top','5','--json',str(stem.with_suffix('.exact.json'))],stdout=log,stderr=subprocess.STDOUT).returncode
  txt=stem.with_suffix('.exact.log').read_text();m=re.search(r'1-F \(to 3rd order\) = (\S+)',txt);screen=json.loads(stem.with_suffix('.screen.json').read_text());assert rc==0 and m and abs(float(m[1])-screen['total'])<=5.1e-11,(name,rc,txt[-500:]);r.update(exact_verified=True,exact_cli_total=float(m[1]))
 out.write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
 if socket.gethostname()=='zebra':report()
