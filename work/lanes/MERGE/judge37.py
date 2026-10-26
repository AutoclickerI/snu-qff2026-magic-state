from cont37 import *
import statistics
sys.path.insert(0,str(ROOT/'work'))
import xtim
xtim.cache_dir=str(H/'.xtim_cache')
import fast_check
from speed_predict import predict
def one(st):
 st=Path(st);txt=st.with_suffix('.qasm').read_text();s=sha(st);start=time.monotonic()
 data=json.loads(st.with_suffix('.json').read_text())['data_qubits']
 rep=fast_check.check(txt,data,shots=10**6,procs=1)
 r=dict(sha256=s,gates_ok=bool(rep.correct_ok),passed=bool(rep.passed),shots=10**6,seed=0,
        sampled_loss=float(rep.score),sampled_acceptance=float(rep.acceptance),seconds=time.monotonic()-start)
 return r
def baseline():
 st=C/'base';probe=predict(str(st),shots=100000,repeats=3);runs=[]
 for _ in range(3):
  r=one(st);runs.append(r);print(json.dumps(r),flush=True)
 out=dict(stem=str(st),sha256=sha(st),judge_runs=runs,median_judge_seconds=statistics.median(r['seconds'] for r in runs),sampler_probe=probe)
 dump(R/'baseline_speed.json',out);print(json.dumps(dict(event='speed_baseline',**out)),flush=True)
def verify(st,name=None):
 st=Path(st);base=json.loads((R/'baseline_speed.json').read_text());s=sha(st)
 # Brief sampler timing prevents sending a slow dispatch to a million-shot run.
 probe=predict(str(st),shots=10000,repeats=2)
 baseline_sampler=base['sampler_probe']['median_seconds_per_1e6']
 if probe['median_seconds_per_1e6']>max(1.5*baseline_sampler+5,30):
  r=dict(sha256=s,gates_ok=None,speed_ok=False,reason='short exact-sampler probe exceeds1.5x budget by >5s',probe=probe)
  dump(R/f'judge_{s}.json',r);print(json.dumps(r),flush=True);return r
 runs=[one(st)];full=probe=predict(str(st),shots=100000,repeats=3)
 ratio=full['median_seconds_per_1e6']/baseline_sampler
 if not(ratio<=1.5 and runs[0]['seconds']<=1.5*base['median_judge_seconds']):
  # Same-process paired repeats distinguish transient host load from sampler regressions.
  controls=[]
  for _ in range(2):controls.append(one(C/'base'));runs.append(one(st))
  reference=statistics.median([base['median_judge_seconds']]+[r['seconds'] for r in controls])
 else:reference=base['median_judge_seconds'];controls=[]
 median=statistics.median(r['seconds'] for r in runs)
 verdict=dict(sha256=s,gates_ok=all(r['gates_ok'] for r in runs),speed_ok=bool(median<=1.5*reference and ratio<=1.5),
              judge_runs=runs,median_judge_seconds=median,baseline_judge_seconds=reference,judge_speed_ratio=median/reference,
              sampler_speed_ratio=ratio,sampler_probe=full,paired_controls=controls)
 dump(R/f'judge_{s}.json',verdict);print(json.dumps(verdict),flush=True)
 if name and verdict['gates_ok'] and verdict['speed_ok']:
  p=price(st,dict(kind='verified candidate',name=name));assert feasible(p) and p['loss']<TAU-3e-8
  dest=H/'cand'/name;shutil.copyfile(st.with_suffix('.qasm'),dest.with_suffix('.qasm'));plan=M.read(st)
  dump(dest.with_suffix('.json'),dict(p,source=json.loads(st.with_suffix('.json').read_text()).get('source'),judge_1e6=verdict,
       cx=sum(M.unit(o).name=='CX' for o in plan['ops']),native_depth=M.depth(plan),tau=TAU))
 return verdict
if __name__=='__main__':
 if sys.argv[1]=='baseline':baseline()
 else:verify(Path(sys.argv[1]),sys.argv[2] if len(sys.argv)>2 else None)
