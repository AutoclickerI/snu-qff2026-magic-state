"""Finalist confirmation: unchanged exact CLI, judge, report, then unchanged mc3."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json,re,subprocess,time
from pathlib import Path
from evaluate import H,ROOT,judge
from report import report
p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--procs',type=int,default=4);p.add_argument('--mc',action='store_true');a=p.parse_args();stem=Path(a.stem);stem=stem if stem.is_absolute() else H/'finalists'/stem
print(json.dumps(dict(event='capacity',nproc=os.cpu_count(),load=os.getloadavg(),procs=a.procs)),flush=True)
with stem.with_suffix('.exact.log').open('w') as log:pr=subprocess.run([sys.executable,str(ROOT/'work/lanes/EVAL/exact2.py'),str(stem.with_suffix('.qasm')),'--third','--procs',str(a.procs),'--top','10','--json',str(stem.with_suffix('.exact.json'))],stdout=log,stderr=subprocess.STDOUT)
assert pr.returncode==0,pr.returncode
r=json.loads(stem.with_suffix('.screen.json').read_text());txt=stem.with_suffix('.exact.log').read_text();mt=re.search(r'1-F \(to 3rd order\) = (\S+)',txt);assert mt and abs(float(mt[1])-r['total'])<=5.1e-11
text=stem.with_suffix('.qasm').read_text();md=json.loads(stem.with_suffix('.json').read_text());ck=judge(text,md);assert ck['passed'] and ck['acceptance']>=.505
r['confirmation_check']=ck;stem.with_suffix('.screen.json').write_text(json.dumps(r,indent=2));report();print(json.dumps(dict(event='EXACT_VERIFIED',stem=str(stem),total=r['total'],exp_minus_A1=r['exp_minus_A1'])),flush=True)
if a.mc:
 with stem.with_suffix('.mc.log').open('w') as log:pr=subprocess.run([sys.executable,str(H/'inputs/mc3.py'),str(stem),'--procs',str(a.procs)],stdout=log,stderr=subprocess.STDOUT)
 assert pr.returncode==0
 print(stem.with_suffix('.mc.log').read_text(),flush=True);report()
