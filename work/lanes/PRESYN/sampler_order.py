"""Test whether noise-preserving instruction order repairs slow exact sampling."""
from core import *
import reorder,random,tprep
tc=sys.modules['tprep.check'];orig=tc._sample
for nm in sys.argv[1:]:
 stem=OUT/nm;txt=stem.with_suffix('.qasm').read_text();meta=json.loads(stem.with_suffix('.json').read_text());sig=reorder.signature(txt);rows=[];best=None
 for seed in range(17):
  var=txt if seed==0 else'\n'.join(reorder.shuffle(txt.split('\n'),random.Random(seed)))
  assert reorder.signature(var)==sig
  parts=[]
  def timed(circuit,shots,seed,plan=None):
   t=time.monotonic();r=orig(circuit,shots,seed,plan);parts.append(time.monotonic()-t);return r
  tc._sample=timed;r=tprep.check(var,meta['data_qubits'],shots=10000,seed=0)
  row=dict(order_seed=seed,sampling_seconds=parts[-1],passed=r.passed);rows.append(row);print(nm,json.dumps(row),flush=True)
  if best is None or row['sampling_seconds']<best[0]:best=(row['sampling_seconds'],seed,var)
 tc._sample=orig
 (OUT/(nm+'.sampler_order.json')).write_text(json.dumps(rows,indent=2)+'\n')
 if best[0]<rows[0]['sampling_seconds']*.5:
  out=OUT/(nm+'_fastorder');out.with_suffix('.qasm').write_text(best[2]);out.with_suffix('.json').write_text(json.dumps(dict(meta,sampler_order_seed=best[1],physical_source=nm),indent=2)+'\n');print('FAST',out,best[:2],flush=True)
