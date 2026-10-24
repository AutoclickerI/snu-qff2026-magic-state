import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import concurrent.futures,json,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
def check(f):
 import tprep
 out=Path(str(f)[:-len('.timing.json')]);d=json.loads(out.with_suffix('.json').read_text());r=json.loads(f.read_text());ck=tprep.check(out.with_suffix('.qasm').read_text(),d['data_qubits'],shots=10**6,seed=0)
 r['check']=dict(passed=bool(ck.passed),acceptance=float(ck.acceptance),score=float(ck.score));r['mode']='native BC timing';out.with_suffix('.price.json').write_text(json.dumps(r,indent=2));return r['tag'],bool(ck.passed)
def main():
 rows=[]
 with concurrent.futures.ProcessPoolExecutor(max_workers=3) as e:
  for row in e.map(check,sorted((H/'full').glob('time_*.timing.json'))):rows.append(row);print(row,flush=True)
 (H/'timing_checks.json').write_text(json.dumps(rows,indent=2))
 for prep in sorted((H/'runs').glob('fb_*.prep.json')):
  tag=prep.name[:-len('.prep.json')];price=H/'full'/f'{tag}.price.json'
  if price.exists() and 'check' in json.loads(price.read_text()):continue
  d=json.loads(prep.read_text());cmd=[sys.executable,str(H/'price.py'),str(prep),tag,'--mode','release_alap','--mx',','.join(map(str,d['pivots']))]
  with (H/'full'/f'{tag}.price.log').open('w') as log:p=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,cwd=H);print('reprice',tag,p.returncode,flush=True)
if __name__=='__main__':main()
