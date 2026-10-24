import os,sys,re,json,subprocess,hashlib,concurrent.futures,argparse
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','PYTHONDONTWRITEBYTECODE'):os.environ[k]='1'
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def run(name,procs):
 stem=OUT/name;digest=hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest()
 cmd=[sys.executable,str(ROOT/'work/lanes/EVAL/exact2.py'),str(stem.with_suffix('.qasm')),'--third','--procs',str(procs),'--top','0']
 with stem.with_suffix('.reference.log').open('w')as f:subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,check=True)
 text=stem.with_suffix('.reference.log').read_text();row=dict(name=name,sha256=digest,evaluator='work/lanes/EVAL/exact2.py',procs=procs)
 for key,pat in [('c1p',r'c1 p = (\S+)'),('second',r'second order: (\S+)'),('third',r'third order: (\S+)'),('total',r'1-F \(to 3rd order\) = (\S+)'),('exp_minus_A1',r'exp\(-A1\) = (\S+)')]:row[key]=float(re.search(pat,text)[1])
 if stem.with_suffix('.result.json').exists():
  old=json.loads(stem.with_suffix('.result.json').read_text());row['pruned_total_difference']=row['total']-old['total'];assert abs(row['pruned_total_difference'])<1e-10,row
 stem.with_suffix('.reference.json').write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(row),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('names',nargs='+');p.add_argument('--procs',type=int,default=4);p.add_argument('--jobs',type=int,default=4);a=p.parse_args()
 with concurrent.futures.ThreadPoolExecutor(a.jobs)as pool:list(pool.map(lambda n:run(n,a.procs),a.names))
