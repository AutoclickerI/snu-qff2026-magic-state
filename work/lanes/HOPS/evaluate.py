import os,sys,json,re,subprocess,concurrent.futures,argparse,time
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','PYTHONDONTWRITEBYTECODE'):os.environ[k]='1'
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
FAST=False
def one(name):
 stem=OUT/name
 cmd=[sys.executable,str(ROOT/('work/lanes/TREP2/fast_third.py' if FAST else 'work/lanes/EVAL/exact2.py')),str(stem.with_suffix('.qasm')),'--third','--procs','1','--top','0']
 with stem.with_suffix('.exact.log').open('w')as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
 row={'name':name};log=stem.with_suffix('.exact.log').read_text()
 for key,pat in [('c1p',r'c1 p = (\S+)'),('second',r'second order: (\S+)'),('third',r'third order: (\S+)'),('total',r'1-F \(to 3rd order\) = (\S+)'),('exp_minus_A1',r'exp\(-A1\) = (\S+)')]:
  m=re.search(pat,log)
  if m:row[key]=float(m[1])
 subprocess.run([sys.executable,str(OUT/'check.py'),name],check=True)
 row['check']=json.loads(stem.with_suffix('.check.json').read_text());stem.with_suffix('.result.json').write_text(json.dumps(row,indent=2)+'\n');return row
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('names',nargs='+');p.add_argument('--workers',type=int,default=1);p.add_argument('--fast',action='store_true');a=p.parse_args();FAST=a.fast
 with concurrent.futures.ThreadPoolExecutor(a.workers)as pool:
  for x in pool.map(one,a.names):print(json.dumps(x),flush=True)
