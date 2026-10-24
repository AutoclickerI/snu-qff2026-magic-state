from common import *
import numpy as np,itertools
s=H/'c4_path_earlyA_fixed_w26';c=json.loads(s.with_suffix('.plan.json').read_text());out=json.loads(s.with_suffix('.tail_ablation.json').read_text());ta={int(k):v for k,v in out['data_A_contacts'].items()};tb={int(k):v for k,v in out['data_B_contacts'].items()};ev=exact2.Eval(s.with_suffix('.qasm').read_text(),c['meta']['data_qubits']);rates={q:np.zeros(3)for q in ta};selected=set()
for ci,ch in enumerate(ev.m.chans):
 if ch['gap']is None:continue
 q,start,n=ch['gap']
 if q in ta and start>ta[q]:
  selected.add(ci);rates[q][0]+=ch['prob']/3
  if start>tb[q]:rates[q][1:]+=ch['prob']/3
formula=0.
for a,b in itertools.combinations(rates.values(),2):
 x,y,z=a;u,v,w=b;formula+=.5*(x*u+x*v+y*u+y*v)+y*w+z*v+z*w
for i,ch in enumerate(ev.fch):
 if ch not in selected:ev.fp[i]=0
r=mom.evaluate(ev);assert abs(r['second']-formula)<1e-13,(formula,r)
row=dict(passed=True,formula_second=formula,exact_second=r['second'],tail_only_third=r['third'],tail_only_total=r['total'],rates={q:v.tolist()for q,v in rates.items()},formula='sum_{i<j} [0.5*(x_i*x_j+x_i*y_j+y_i*x_j+y_i*y_j)+y_i*z_j+z_i*y_j+z_i*z_j], with x from all post-A idle and y,z from post-B idle only');(H/'tail_cost_validation.json').write_text(json.dumps(row,indent=2));append_result('C4_tail_pair_objective',row,'Exact pure-output-idle second-order polynomial validated against full fault propagation; finite-length native idle channel probabilities retained.');print(json.dumps(row))
