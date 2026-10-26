from pass4 import *
import statistics,socket
sys.path.insert(0,str(ROOT/'work'))
import xtim
xtim.cache_dir=str(H/'.xtim_cache')
import fast_check

def one(st):
 st=Path(st);txt=st.with_suffix('.qasm').read_text();data=json.loads(st.with_suffix('.json').read_text())['data_qubits'];t=time.monotonic()
 rep=fast_check.check(txt,data,shots=10**6,procs=1)
 return dict(sha256=sha(st),host=socket.gethostname(),seconds=time.monotonic()-t,shots=10**6,procs=1,gates_ok=bool(rep.correct_ok),passed=bool(rep.passed),sampled_loss=float(rep.score)if rep.score is not None else None,sampled_acceptance=float(rep.acceptance)if rep.acceptance is not None else None,n_2q=rep.n_2q)

def bounded_one(st, baseline_seconds):
 # Wait for the actual judge subprocess; a generous timeout only rejects clear slow paths.
 import signal,traceback
 queue=get_context('fork').Queue()
 def run():
  try:queue.put(dict(result=one(st)))
  except BaseException:queue.put(dict(error=traceback.format_exc()))
 proc=get_context('fork').Process(target=run);start=time.monotonic();proc.start();limit=max(30.0,4.5*baseline_seconds);proc.join(limit)
 if proc.is_alive():
  os.kill(proc.pid,signal.SIGTERM);proc.join()
  return dict(sha256=sha(st),gates_ok=None,speed_ok=False,reason='full one-process judge timeout',runtime_lower_bound_seconds=time.monotonic()-start,baseline_seconds=baseline_seconds,speed_limit_seconds=1.5*baseline_seconds,killed_pid=proc.pid)
 result=queue.get(timeout=2);queue.close()
 if 'error'in result:raise RuntimeError(result['error'])
 return result['result']

def verify(st):
 st=Path(st);s=sha(st);p=R/f'judge_{s}.json'
 if p.exists():return json.loads(p.read_text())
 controls=[];runs=[]
 for i in range(3):
  order=[('base',C/'base'),('candidate',st)]if i%2==0 else [('candidate',st),('base',C/'base')]
  for kind,path in order:
   r=one(path)if kind=='base'else bounded_one(path,statistics.median(x['seconds']for x in controls))
   print(json.dumps(dict(event='judge',kind=kind,**r)),flush=True)
   if r.get('speed_ok')is False:dump(p,r);return r
   (controls if kind=='base'else runs).append(r)
 bs=statistics.median(r['seconds']for r in controls);cs=statistics.median(r['seconds']for r in runs)
 result=dict(sha256=s,host=socket.gethostname(),gates_ok=all(r['gates_ok']for r in runs),speed_ok=cs<=1.5*bs,median_seconds=cs,baseline_median_seconds=bs,ratio=cs/bs,judge_runs=runs,baseline_runs=controls)
 dump(p,result);return result

if __name__=='__main__':print(json.dumps(verify(Path(sys.argv[1]))),flush=True)
