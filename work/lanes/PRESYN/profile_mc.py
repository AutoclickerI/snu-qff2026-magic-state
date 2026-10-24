from core import *
import tprep
tc=sys.modules['tprep.check'];original=tc._sample
for nm in sys.argv[1:]:
 stem=OUT/nm;text=stem.with_suffix('.qasm').read_text();meta=json.loads(stem.with_suffix('.json').read_text());start=time.monotonic();parts=[]
 def sample(circuit,shots,seed,plan=None):
  print(nm,'pre_sample_seconds',time.monotonic()-start,flush=True)
  ts=time.monotonic();r=original(circuit,shots,seed,plan);parts.append(time.monotonic()-ts);return r
 tc._sample=sample
 r=tprep.check(text,meta['data_qubits'],shots=100000,seed=0)
 print(json.dumps(dict(stem=nm,shots=100000,passed=r.passed,elapsed=time.monotonic()-start,sampling=parts,repr=str(r))),flush=True)
tc._sample=original
