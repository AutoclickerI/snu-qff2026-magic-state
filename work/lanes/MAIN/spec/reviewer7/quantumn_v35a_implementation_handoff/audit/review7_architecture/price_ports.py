from pathlib import Path
import subprocess,sys,concurrent.futures,json,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];EVAL=ROOT/'audit/reaudit_evaluation/portable'
def run(name):
 stem=HERE/name
 with stem.with_suffix('.log').open('w')as log:
  p=subprocess.run([sys.executable,str(EVAL/'sparse_walsh.py'),str(stem),'72','canonical'],stdout=log,stderr=subprocess.STDOUT)
 if p.returncode:return dict(source=str(stem),error=p.returncode)
 path=EVAL/(stem.name+'_canonical_sparse_result.json');shutil.copyfile(path,HERE/path.name)
 d=json.loads(path.read_text())
 return {k:d[k]for k in['source','loss','acceptance','seconds','conditioned_width','conditional_loss_kernel_omission_bound']}
if __name__=='__main__':
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:
  for task in concurrent.futures.as_completed([pool.submit(run,n)for n in sys.argv[1:]or['v32p_control','v32p_a_decode']]):
   r=task.result();results.append(r);print(json.dumps(r),flush=True)
 (HERE/'port_prices.json').write_text(json.dumps(results,indent=2)+'\n')
