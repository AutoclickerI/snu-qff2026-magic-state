from common import *
import numpy as np,argparse
p=argparse.ArgumentParser();p.add_argument('stem');a=p.parse_args();stem=Path(a.stem);c=json.loads(stem.with_suffix('.plan.json').read_text());ev=exact2.Eval(stem.with_suffix('.qasm').read_text(),c['meta']['data_qubits']);fp=ev.fp.copy();start=100+c['meta']['data_hops']+c['meta']['block_teleports'];read={o['bit']:o['t']for o in c['ops']if o.get('tag')=='read'};ta={q:read[start+2*i]-1 for i,q in enumerate(c['meta']['data_qubits'])};tb={q:read[start+2*i+1]-1 for i,q in enumerate(c['meta']['data_qubits'])};rows=[]
for label,pred in [('all',lambda ch:False),('no_post_A_data_idle',lambda ch:ch['gap']is not None and ch['gap'][0]in ta and ch['gap'][1]>ta[ch['gap'][0]]),('no_post_B_data_idle',lambda ch:ch['gap']is not None and ch['gap'][0]in tb and ch['gap'][1]>tb[ch['gap'][0]]),('no_idle',lambda ch:ch['gap']is not None)]:
 selected={i for i,ch in enumerate(ev.m.chans)if pred(ch)};ev.fp=fp.copy()
 for i,ch in enumerate(ev.fch):
  if ch in selected:ev.fp[i]=0
 r=mom.evaluate(ev);rows.append(dict(label=label,channels=len(selected),**r));print(json.dumps(rows[-1]),flush=True);append_result(stem.name+':'+label,r,'C4 counterfactual idle-channel removal, not an achievable independent gain. A and B contacts obtained from exact per-wire readout provenance.')
out=dict(data_A_contacts=ta,data_B_contacts=tb,native_depth=c['meta']['native_depth'],rows=rows);stem.with_suffix('.tail_ablation.json').write_text(json.dumps(out,indent=2))
