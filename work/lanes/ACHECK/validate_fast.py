from common import *
import fast_exact,exact2,numpy as np,random
rows=[]
for name in ['base','flag_05','layout2_alap','reuse_1_2_16']:
 p=HERE/name;ev=exact2.Eval(p.with_suffix('.qasm').read_text(),json.loads(p.with_suffix('.json').read_text())['data_qubits']);rng=random.Random(42)
 keys=[]
 for n in [1,2,3]:
  for _ in range(150):
   s=d=0
   for k in rng.choices(ev.gkeys,k=n):s^=k[0];d^=k[1]
   keys.append((s,d))
 S0=np.array([s for s,d in keys]);D0=np.array([d for s,d in keys]);a,n=fast_exact._batch(ev.e,S0,D0);b,m=ev.e.batch_n(S0,D0)
 err=max(float(np.abs(a-b).max()),float(np.abs(n-m).max()));assert err<1e-14
 rows.append(dict(circuit=name,random_single_pair_triple_queries=len(keys),maximum_absolute_difference=err,identity_detector_count=fast_exact.mask(ev.e).bit_count()))
(HERE/'fast_validation.json').write_text(json.dumps(rows,indent=1));print(rows,flush=True)
