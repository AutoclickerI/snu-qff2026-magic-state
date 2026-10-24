import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,time,importlib,collections
H=Path(__file__).resolve().parent;R=H.parents[2];D=H/'r36';D.mkdir(exist_ok=True)
sys.path[:0]=[str(R/'upstream/snu-qff2026-problem')]
import xtim,numpy as np
xtim.cache_dir=str(D/'.cache');os.environ['XTIM_TWIRL_CACHE_DIR']=str(D/'.cache')
from tprep.noise import STANDARD,apply_noise
from tprep.qasm import to_stim
ck=importlib.import_module('tprep.check')

def build(stem,p=.001):
 stem=Path(stem);text,errors=to_stim(stem.with_suffix('.qasm').read_text());assert not errors,errors
 noisy=apply_noise(text,p,STANDARD);data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
 body=xtim.Circuit(noisy);plan=ck.Plan(data,{'X':(0,[]),'Z':(0,[])},(),body.num_measurements)
 return noisy+'\n'+plan.tail

def probe(stem,shots=10000):
 text=build(stem);c=xtim.Circuit(text);s=c.compile_detector_sampler(seed=0,engine='exact')
 t=time.perf_counter();raw=s._run(shots,want_meas=True,want_det=True,want_obs=False,want_exp=True);dt=time.perf_counter()-t
 result=dict(stem=str(stem),shots=shots,seconds=dt,seconds_per_1e6=dt*1e6/shots,exact_scalars={k:v for k,v in raw.items() if not isinstance(v,np.ndarray)},program_attributes=dir(s._program))
 tw=xtim.compile_twirl_sampler(c,disk_cache=False,selfcheck=0,skip_refused_observables=True)
 t=time.perf_counter()
 try:tw.sample(shots,seed=0)
 except RuntimeError as ex:
  result['twirl_error']=str(ex);result['twirl_report']=tw.channel_report();return result
 result['twirl_seconds']=time.perf_counter()-t
 result['twirl_report']=tw.channel_report()
 try:buf=tw.sample_barrier(shots,seed=0,compact=True)
 except RuntimeError as ex:
  result['barrier_error']=str(ex);return result
 keys=collections.Counter(bytes(buf.plan_key(i)) for i in range(shots));laws=[]
 for key,n in keys.items():
  law=tw.plan_structure(key);laws.append(dict(shots=n,key_bytes=len(key),r=law['r'],kappa=law['kappa'],fallback=law['fallback']))
 result['laws']=laws;result['law_summary']={str(k):v for k,v in collections.Counter({}).items()}
 counts=collections.Counter()
 for law in laws:counts[(law['r'],law['kappa'],law['fallback'])]+=law['shots']
 result['law_summary']={str(k):v for k,v in counts.items()}
 return result

if __name__=='__main__':
 stem=Path(sys.argv[1]);shots=int(sys.argv[2]) if len(sys.argv)>2 else 10000
 if '--exact-only' in sys.argv:
  s=xtim.Circuit(build(stem)).compile_detector_sampler(seed=0,engine='exact');r=s._run(shots,want_meas=True,want_det=True,want_obs=False,want_exp=True);print('DONE',r['shots']);sys.exit()
 try:r=probe(stem,shots)
 except Exception as e:
  import traceback;r=dict(error=repr(e),trace=traceback.format_exc());print(r)
 name=stem.name+('_memo0' if os.getenv('QEC_FRAMED_MEMO')=='0' else '')+('_fallback' if os.getenv('QEC_FORCE_FALLBACK')=='1' else '')
 (D/(name+'.probe.json')).write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in ('laws','program_attributes')}),flush=True)
