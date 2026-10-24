"""Per-wire commutation retiming: stagger finished round pairs without changing any gate."""
import os,sys,json,collections
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from ortools.sat.python import cp_model
H=Path(__file__).resolve().parent

def run(name,weight):
 p=json.loads((H/(name+'.plan.json')).read_text());ops=sorted(p['ops'],key=lambda o:o['t']);endold=max(o['t']for o in ops);m=cp_model.CpModel();end=m.NewIntVar(0,endold,'end');ts=[m.NewIntVar(0,endold,f't{i}')for i in range(len(ops))];last={}
 for i,o in enumerate(ops):
  m.Add(ts[i]<=end)
  for q in o['qs']:
   if q in last:m.Add(ts[i]>ts[last[q]])
   last[q]=i
  m.AddHint(ts[i],o['t'])
 s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.cp_model_presolve=False;m.Minimize(end);st=s.Solve(m);assert st==cp_model.OPTIMAL;best=s.Value(end);m.Add(end==best)
 objective=0
 for i,o in enumerate(ops):
  if o['region']=='round':objective-=weight*ts[i]
  elif o['name']in('MX','MEASURE')and not o.get('init_frame'):objective-=ts[i]
  else:objective+=ts[i]
 m.Maximize(objective);st=s.Solve(m);assert st==cp_model.OPTIMAL
 for o,t in zip(ops,ts):o['t']=s.Value(t)
 times=sorted({o['t']for o in ops});ct={t:i for i,t in enumerate(times)};used=sorted({q for o in ops for q in o['qs']});bar='barrier '+','.join(f'q[{q}]'for q in used)+';';lines=p['h'][:]
 for t in times:
  layer=[o for o in ops if o['t']==t];busy=[q for o in layer for q in o['qs']];assert len(busy)==len(set(busy))
  for o in layer:lines+=o['lines'];o['t']=ct[t]
  lines.append(bar)
 lines+=p['tail'];p['ops']=sorted(ops,key=lambda o:o['t']);roundcx=[o for o in ops if o['region']=='round'and o['name']=='CX'];bdi=[o['t']for o in roundcx if o['qs'][0]in p['meta']['B']and o['qs'][1]in p['meta']['data_qubits']]
 p['meta'].update(R=min(o['t']for o in roundcx),round_last_pair=max(o['t']for o in roundcx),staggered=True,BD_times=bdi,native_depth=len(times),retiming=dict(mode='fixed-wire commutation; minimum total end, weighted early round / late preparation',round_weight=weight,model_end=best))
 out=H/(name+f'_stagger{weight}');out.with_suffix('.qasm').write_text('\n'.join(lines)+'\n');out.with_suffix('.json').write_text(json.dumps(p['meta'],indent=2));out.with_suffix('.plan.json').write_text(json.dumps(p,indent=1));print(out.name,p['meta']['R'],p['meta']['round_last_pair'],bdi,flush=True);return out.name
out=[run('region2_k56_A2_safe_dest',w)for w in(2,20,100)];(H/'stagger_stems.json').write_text(json.dumps(out))
