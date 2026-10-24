"""Matched physical fault-pair differences for the added q5 measurement."""
from common import *
import collections
def pairs(stem):
 ev=exact2.Eval(stem.with_suffix('.qasm').read_text(),json.loads(stem.with_suffix('.json').read_text())['data_qubits']);r=exact2.run(ev,procs=4,third=False,keep_thr=0.0);out=collections.Counter()
 for w,i,j,_,_ in r['big']:
  labels=tuple(sorted(re.sub(r'^L\d+ ','',ev.fault_label(k))for k in(i,j)));out[labels]+=w
 return out
old=pairs(H/'inputs/endpoint_blue');new=pairs(H/'zero_endpoint_blue_q5_t37');delta={k:new[k]-old[k]for k in set(old)|set(new)if abs(new[k]-old[k])>1e-18};top=sorted(delta.items(),key=lambda x:abs(x[1]),reverse=True)
out=dict(delta_second=sum(delta.values()),largest=[dict(delta=v,pair=k)for k,v in top[:40]])
(H/'q5_pair_delta.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
