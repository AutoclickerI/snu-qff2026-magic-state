"""Single-process all-orders jobs in a bounded fork pool; unchanged evaluator."""
from a34_evaluate import *
import concurrent.futures

def work(s):
 stem=H/s
 try:
  p=Path(str(stem)+'.allorders.json')
  r={k:v for k,v in json.loads(p.read_text()).items() if k in ('loss','acceptance','seconds','conditional_loss_kernel_omission_bound')} if p.exists() else evaluate(stem,1)
  r['stem']=s
 except Exception as e:r=dict(stem=s,error=repr(e),trace=traceback.format_exc())
 return r
if __name__=='__main__':
 p=Path(sys.argv[1]);workers=int(sys.argv[2]);ss=json.loads(p.read_text());results=[]
 with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
  for f in concurrent.futures.as_completed({pool.submit(work,s):s for s in ss}):
   r=f.result();results.append(r);print(json.dumps(r),flush=True);(D/'runs'/('results_'+p.stem+'.json')).write_text(json.dumps(results,indent=2))
 print('DONE',len(results),flush=True)
