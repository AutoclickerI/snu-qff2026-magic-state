from context76 import *
import argparse
p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--judge',action='store_true');a=p.parse_args();import xtim_predict_snapshot as speed_predict
xtim.cache_dir=str(H/'.xtim_cache');stem=Path(a.stem);r=speed_predict.predict(str(stem));stem.with_suffix('.speed.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
if a.judge and r['classification']=='FAST':
 import fast_check
 st=time.monotonic()
 with stem.with_suffix('.judge.log').open('w')as log,contextlib.redirect_stdout(log):
  rep=fast_check.check(stem.with_suffix('.qasm').read_text(),json.loads(stem.with_suffix('.json').read_text())['data_qubits'],shots=10**6,seed=0,procs=1)
  j=dict(passed=rep.passed,score=rep.score,sem=rep.sem,acceptance=rep.acceptance,n_2q=rep.n_2q,seconds=time.monotonic()-st,report=repr(rep));print(json.dumps(j))
 stem.with_suffix('.judge.json').write_text(json.dumps(j,indent=2));r['judge']=j;print(json.dumps(j),flush=True)
append_result(stem.name+':speed',r,'Unchanged XTIM speed_predict; cache path alone redirected to ST1. Judge when requested is unchanged fast_check at 1e6 seed0.')
